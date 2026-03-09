'''
This file handles the openai prompts and responses
'''
#****************************************************************************************************

from openai import OpenAI as openai
import os
from dotenv import load_dotenv
from spotify import get_recently_played
import json

#****************************************************************************************************

load_dotenv()

#****************************************************************************************************

def get_song_recommendations(prompt):
    client = openai(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a music expert. When given a description, return exactly 10 song recommendations. Return only a plain list, one per line, in the format: Song Name - Artist. No numbering, no extra text."},
            {"role": "user", "content": f"Recommend 10 songs based on this description: {prompt}"}
        ]
    )
    text = response.choices[0].message.content
    songs = [line.strip() for line in text.strip().split('\n') if line.strip()]

    return songs

#****************************************************************************************************

def get_current_mood(token=None):
    recently_played = get_recently_played(limit=20, token=token)

    if not recently_played:
        return "No recent songs found. Please listen to some music and try again."
    
    print(os.getenv("OPENAI_API_KEY"))
    client = openai(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": "You are a music expert. Analyze the following list of recently played songs and determine the user's current mood. Return a single word or short phrase that best describes the mood."},
            {"role": "user", "content": f"Here are the recently played songs: {json.dumps(recently_played)}"}
        ]
    )
    mood = response.choices[0].message.content.strip()

    return mood

#****************************************************************************************************
