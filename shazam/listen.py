#!/usr/bin/env python3

import pyaudio
import wave
import io
from ShazamAPI import Shazam

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import os

def setup_spotify():
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
        response = input('Enter the URL you were redirected to: ')
        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)

    if token_info:
        return spotipy.Spotify(auth=token_info['access_token'])
    else:
        print("Error: Couldn't get access token. Please check your credentials and try again.")
        return None

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
    # Construct search query
    query = f"track:{song_name}"
    if singer:
        query += f" artist:{singer}"

    # Search for the songs
    results = sp.search(q=query, type="track", limit=10)  # Increase limit to get more results
    
    if results['tracks']['items']:
        tracks = results['tracks']['items']
        
        # Sort results by popularity, then by release date
        tracks.sort(key=lambda x: (x['popularity'], x['album']['release_date']), reverse=True)
        
        # Limit to 5 results
        tracks = tracks[:7]
        
        # Display the sorted tracks with indices
        for index, track in enumerate(tracks, start=1):
            display_track_metadata(track, index)
        
        # Prompt user to choose which songs to add
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
            # Add the selected songs to the playlist
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

    # Save as WAV file
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
            #print(f"Artist: {track['subtitle']}")
            #print(f"Genre: {track.get('genre', 'N/A')}")
            print("=" * 40)

            sp = setup_spotify()
            if sp:
                playlist_id = os.getenv("SPOTIPY_PLAYLIST_ID")
                search_and_add_songs(sp, track['title'], track['subtitle'], playlist_id)

        else:
            print("Song not identified.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()