import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import argparse
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

def main():
    parser = argparse.ArgumentParser(description="Add songs to a Spotify playlist.")
    parser.add_argument("song_name", help="Name of the song to search for")
    parser.add_argument("--singer", help="Name of the singer (optional)")
    args = parser.parse_args()

    sp = setup_spotify()
    if sp:
        playlist_id = os.getenv("SPOTIPY_PLAYLIST_ID")
        search_and_add_songs(sp, args.song_name, args.singer, playlist_id)

if __name__ == "__main__":
    main()
