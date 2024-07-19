#!/usr/bin/env python3

import pyaudio
import wave
import io
from ShazamAPI import Shazam

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import os
import time
from flask import Flask, request, redirect
import threading

app = Flask(__name__)
auth_code = None

@app.route('/callback')
def callback():
    global auth_code
    auth_code = request.args.get('code')
    return "Authorization code received. You can close this window now."

def get_spotify_client():
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri="http://localhost:8888/callback",
        scope="playlist-modify-public playlist-modify-private"
    )
    
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        print(f'Please go to this URL and authorize the app: {auth_url}')

        # Start Flask server to capture the callback
        threading.Thread(target=lambda: app.run(port=8888)).start()

        while not auth_code:
            time.sleep(1)

        token_info = sp_oauth.get_access_token(auth_code)

    return sp_oauth, token_info

def refresh_token_if_needed(sp_oauth, token_info):
    if token_info and time.time() > token_info['expires_at']:
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

def setup_spotify():
    sp_oauth, token_info = get_spotify_client()

    if not token_info:
        print("Error: Couldn't get access token. Please check your credentials and try again.")
        return None

    token_info = refresh_token_if_needed(sp_oauth, token_info)
    return spotipy.Spotify(auth=token_info['access_token']), sp_oauth, token_info

def format_duration(duration_ms):
    minutes = duration_ms // 60000
    seconds = (duration_ms % 60000) // 1000
    return f"{minutes}:{seconds:02}"

def display_track_metadata(track, index):
    print(f"{index}. Name: {track['name']} / {', '.join([artist['name'] for artist in track['artists']])}")
    print(f"   Album: {track['album']['name']} ({track['album']['release_date']})")
    print(f"   Duration: {format_duration(track['duration_ms'])}    Popularity: {track['popularity']}")
    print("-" * 40)

def search_and_add_songs(sp, song_name, singer, playlist_id):
    query = f"track:{song_name}"
    if singer:
        query += f" artist:{singer}"

    results = sp.search(q=query, type="track", limit=10)
    
    if results['tracks']['items']:
        tracks = results['tracks']['items']
        tracks.sort(key=lambda x: (x['popularity'], x['album']['release_date']), reverse=True)
        tracks = tracks[:7]
        
        for index, track in enumerate(tracks, start=1):
            display_track_metadata(track, index)
        
        selected_indices = input("Enter the numbers of the songs you want to add, separated by commas: ").strip()
        if not selected_indices:
            print("No songs selected. Exiting.")
            return
        
        try:
            selected_indices = [int(index.strip()) for index in selected_indices.split(",")]
        except ValueError:
            print("Invalid input. Exiting.")
            return

        if any(index < 1 or index > len(tracks) for index in selected_indices):
            print("Invalid selection. Exiting.")
            return

        track_uris = [tracks[index - 1]['uri'] for index in selected_indices]

        try:
            sp.playlist_add_items(playlist_id, track_uris)
            for index in selected_indices:
                item = tracks[index - 1]
                print(f"Added '{item['name']}' by {item['artists'][0]['name']} to the playlist.")
        except SpotifyException as e:
            print(f"Error adding songs to playlist: {e}")
            print(f"Playlist ID used: {playlist_id}")
            print("Make sure you're using the correct playlist ID and that you have permission to modify this playlist.")
    else:
        print(f"No songs found for '{song_name}'{' by ' + singer if singer else ''}.")

def record_audio(filename="/tmp/output.wav", duration=10, sample_rate=44100):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=1024)

    print("Listening for 10 seconds...")
    frames = []
    for _ in range(0, int(sample_rate / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    return filename

def identify_song(filename):
    with open(filename, 'rb') as file:
        audio_bytes = file.read()
    
    shazam = Shazam(audio_bytes)
    recognize_generator = shazam.recognizeSong()
    return next(recognize_generator)

def main():
    audio_file = record_audio()
    print("Identifying song...")
    try:
        result = identify_song(audio_file)
        if 'track' in result[1]:
            track = result[1]['track']
            print(f"   Name: {track['title']} / {track['subtitle']}")
            print("=" * 40)

            sp, sp_oauth, token_info = setup_spotify()
            if sp:
                playlist_id = os.getenv("SPOTIPY_PLAYLIST_ID")
                search_and_add_songs(sp, track['title'], track['subtitle'], playlist_id)

        else:
            print("Song not identified.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
