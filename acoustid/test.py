import os
import subprocess
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPUB
from mutagen import File
import json
import shutil
import sys
from ShazamAPI import Shazam
import requests
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPUB, COMM


def convert_clip(input_file, output_file):
    command = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-map_metadata", "0",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        "-loglevel", "quiet", 
        output_file
    ]
    subprocess.run(command, check=True)

def extract_clip(input_file, output_file, start_time=20, duration=10):
    command = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-ss", str(start_time),
        "-t", str(duration),
        "-acodec", "copy",
        "-loglevel", "quiet", 
        output_file
    ]
    subprocess.run(command, check=True)

def identify_song(audio_file):
    try:
        with open(audio_file, 'rb') as file:
            audio_bytes = file.read()
        
        shazam = Shazam(audio_bytes)
        recognition = next(shazam.recognizeSong())
        
        track = recognition[1]['track']
        
        return {
            "title": track.get('title', ''),
            "artist": track.get('subtitle', ''),
            "album": track.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', ''),
            "label": track.get('sections', [{}])[0].get('metadata', [{}])[1].get('text', '')
        }
    except Exception as e:
        print(f"Error identifying song: {e}")
        return None

def del_mp3_tags(file_path):
    audio = ID3(file_path)
    audio.delall("COMM")
    audio.save()

def update_mp3_tags(file_path, song_info):
    audio = ID3(file_path)
    
    #if song_info.get("title"):
    #    audio["TIT2"] = TIT2(encoding=3, text=song_info["title"])
    #if song_info.get("artist"):
    #    audio["TPE1"] = TPE1(encoding=3, text=song_info["artist"])
    if song_info.get("album"):
        audio["TALB"] = TALB(encoding=3, text=song_info["album"])
    if song_info.get("label"):
        audio["TPUB"] = TPUB(encoding=3, text=song_info["label"])
    audio.delall("TSSE")
    audio.delall("COMM")
    
    audio.save()

def show_mp3_tags(file_path):
    audio = ID3(file_path)
    # Loop through all tags and print them
    for key, value in audio.items():
        if key.startswith("APIC"):  # Skip any APIC tag
            continue
        else:
            print(f"{key}: {value}")

def process_directory(input_directory,ouptput_directory,processed_directory):
    for filename in os.listdir(input_directory):
        if filename.endswith(".mp3"):
            file_path = os.path.join(input_directory, filename)
            clip_path = os.path.join(ouptput_directory, f"clip_{filename}")
            
            # Extract clip
            extract_clip(file_path, clip_path)
            
            # Identify song
            song_info = identify_song(clip_path)
            os.remove(clip_path)

            if song_info:
                print(f"Identified song: {json.dumps(song_info, indent=2)}")
                print(f"Before update")
                show_mp3_tags(file_path)

                new_path = os.path.join(ouptput_directory, f"{filename}")                
                del_mp3_tags(file_path)  
                convert_clip(file_path, new_path)                

                update_mp3_tags(new_path, song_info)
                print(f"After update")
                show_mp3_tags(new_path)
            else:
                print(f"Could not identify {filename}")

            # Move the file
            processed_file = os.path.join(processed_directory, f"{filename}")
            shutil.move(file_path, processed_file)
# Usage
process_directory("mp3","output","done")