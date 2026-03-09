'''
This file handles the website and the flask app
'''

#****************************************************************************************************

from flask import Flask, render_template, jsonify, request, session, redirect
from spotify import *
from ai import *
from spotipy.oauth2 import SpotifyOAuth
import os

#****************************************************************************************************

if os.path.exists('.cache'):
    os.remove('.cache')
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.context_processor
def inject_user():
    return {'username': session.get('username')}

def require_login():
    if not session.get('token'):
        return redirect('/login')

#****************************************************************************************************

@app.route('/')
def index():
    check = require_login()
    if check:
        return check
    return render_template('index.html')


#****************************************************************************************************

@app.route('/login')
def login():
    auth_manager = SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URL"),
        scope="user-read-recently-played user-top-read playlist-modify-public playlist-modify-private",
        show_dialog=True
    )

    return redirect(auth_manager.get_authorize_url())

#****************************************************************************************************

@app.route('/callback')
def callback():
    auth_manager = SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URL"),
        scope="user-read-recently-played user-top-read playlist-modify-public playlist-modify-private"
    )
    token = auth_manager.get_access_token(request.args.get('code'))
    session['token'] = token
    sp = get_spotify_client(token)
    session['username'] = sp.current_user()['display_name']
    return redirect('/')

#****************************************************************************************************

@app.route('/mood')
def mood():
    check = require_login()
    if check:
        return check
    token = session.get('token')
    mood = get_current_mood(token=token)
    return render_template('mood.html', mood=mood)

#****************************************************************************************************

@app.route('/top-tracks')
def top_tracks():
    check = require_login()
    if check:
        return check
    token = session.get('token')
    time_range = request.args.get('time_range', 'short_term')
    tracks = get_top_tracks(time_range=time_range, token=token)
    return render_template('top_tracks.html', tracks=tracks)

#****************************************************************************************************

@app.route('/top-artists')
def top_artists():
    check = require_login()
    if check:
        return check
    token = session.get('token')
    time_range = request.args.get('time_range', 'short_term')
    artists = get_top_artists(time_range=time_range, token=token)
    return render_template('top_artists.html', artists=artists)

#****************************************************************************************************

@app.route('/recently-played')
def recently_played():
    check = require_login()
    if check:
        return check
    token = session.get('token')
    tracks = get_recently_played(token=token)
    return render_template('recently_played.html', tracks=tracks)

#****************************************************************************************************

@app.route('/create-playlist', methods=['GET', 'POST'])
def create_playlist_page():
    check = require_login()
    if check:
        return check
    playlist_created = False

    if request.method == 'POST':
        token = session.get('token')
        print(token['scope'])
        name = request.form.get('name')
        description = request.form.get('description')
        song_recommendations = get_song_recommendations(description)
        playlist_id = create_playlist(name, description, public=False, token=token)
        print("Playlist created:", playlist_id)
        add_tracks_to_playlist(playlist_id, song_recommendations, token=token)
        print("Tracks added")
        playlist_created = True

    return render_template('create_playlist.html', recommendations=song_recommendations if request.method == 'POST' else None, playlist_created=playlist_created)

#****************************************************************************************************

if __name__ == '__main__':
    app.run(debug=True)