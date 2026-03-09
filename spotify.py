''''
This file handles the spotify api calls and interactions
'''

import spotipy
import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import json

#****************************************************************************************************

load_dotenv()

#****************************************************************************************************

def get_spotify_client(token=None):
    if token:
        return spotipy.Spotify(auth=token['access_token'])
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-read-recently-played user-top-read playlist-modify-public playlist-modify-private user-library-read user-library-modify"
    ))

#****************************************************************************************************

def get_recently_played(limit=10, token=None):
    sp = get_spotify_client(token)
    results = sp.current_user_recently_played(limit=limit)
    recent_tracks = []

    for item in results['items']:
        track = item['track']
        recent_tracks.append({
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'played_at': item['played_at']
        })

    return recent_tracks

#****************************************************************************************************

def get_top_tracks(limit=10, time_range='short_term', token=None):
    sp = get_spotify_client(token)
    results = sp.current_user_top_tracks(limit=limit, time_range=time_range)
    top_tracks = []

    for track in results['items']:
        top_tracks.append({
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name']
        })

    return top_tracks

#****************************************************************************************************

def get_top_artists(limit=10, time_range='short_term', token=None):
    sp = get_spotify_client(token)
    results = sp.current_user_top_artists(limit=limit, time_range=time_range)
    top_artists = []

    for artists in results['items']:
        top_artists.append(artists['name'])

    return top_artists

#****************************************************************************************************

def get_top_genres(limit=10, token=None):
    sp = get_spotify_client(token)
    results = sp.current_user_top_artists(limit=limit)
    genre_count = {}

    for artist in results['items']:
        for genre in artist['genres']:
            if genre in genre_count:
                genre_count[genre] += 1
            else:
                genre_count[genre] = 1

    sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
    top_genres = sorted_genres[:limit]

    return top_genres


#****************************************************************************************************

# private by default
def create_playlist(name, description='', public=False, token=None):
    import requests as req
    sp = get_spotify_client(token)
    user_id = sp.current_user()['id']
    headers = {
        'Authorization': f'Bearer {token["access_token"]}',
        'Content-Type': 'application/json'
    }
    response = req.post(
        f'https://api.spotify.com/v1/users/{user_id}/playlists',
        headers=headers,
        json={'name': name, 'description': description, 'public': public}
    )
    print("Status:", response.status_code)
    print("Response:", response.text)
    response.raise_for_status()
    return response.json()['id']
    
#****************************************************************************************************

def add_tracks_to_playlist(playlist_id, songs, token=None):
    sp = get_spotify_client(token)
    tracks_uris = []

    for song in songs:
        results = sp.search(q=song, type='track')
        items = results['tracks']['items']

        if items:
            tracks_uris.append(items[0]['uri'])

    sp.playlist_add_items(playlist_id, tracks_uris)

#****************************************************************************************************

    
