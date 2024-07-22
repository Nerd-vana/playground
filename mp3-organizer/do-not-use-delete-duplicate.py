import os
import subprocess
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1

def get_ffprobe_data(file_path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                             'format=bit_rate,duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = result.stdout.decode().split('\n')
    # Ensure we are only capturing the necessary lines and converting correctly
    duration = float(output[0]) if output[0] else 0
    bitrate = int(output[1]) if output[1] else 0
    return duration, bitrate

def get_mp3_metadata(file_path):
    audio = MP3(file_path, ID3=ID3)
    title = audio.get('TIT2', TIT2(text='')).text[0]
    artist = audio.get('TPE1', TPE1(text='')).text[0]
    duration, bitrate = get_ffprobe_data(file_path)
    return title, artist, duration, bitrate

def find_duplicate_mp3_files(root_folder):
    mp3_files = []
    for subdir, _, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith('.mp3'):
                file_path = os.path.join(subdir, file)
                title, artist, duration, bitrate = get_mp3_metadata(file_path)
                file_info = {
                    'path': file_path,
                    'title': title,
                    'artist': artist,
                    'duration': duration,
                    'bitrate': bitrate,
                    'size': os.path.getsize(file_path)
                }
                mp3_files.append(file_info)
    return mp3_files

def filter_duplicates(mp3_files):
    unique_files = {}
    for file in mp3_files:
        key = (file['title'], file['artist'])
        if key in unique_files:
            existing_file = unique_files[key]
            if abs(existing_file['duration'] - file['duration']) < 2:
                if (file['bitrate'] > existing_file['bitrate']) or (
                        file['bitrate'] == existing_file['bitrate'] and file['size'] > existing_file['size']):
                    unique_files[key] = file
        else:
            unique_files[key] = file
    return unique_files.values()

def main(root_folder):
    mp3_files = find_duplicate_mp3_files(root_folder)
    unique_files = filter_duplicates(mp3_files)
    duplicate_files = set([file['path'] for file in mp3_files]) - set([file['path'] for file in unique_files])

    print("Duplicates to delete:")
    for file in duplicate_files:
        print(file)

    proceed = input("Do you want to proceed with deletion? (yes/no): ").strip().lower()
    if proceed == 'yes':
        for file in duplicate_files:
            os.remove(file)
            print(f"Deleted: {file}")
    else:
        print("Deletion aborted.")

if __name__ == "__main__":
    root_folder = "/Users/barry/Music/Store"
    main(root_folder)
