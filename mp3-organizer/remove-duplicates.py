import os
import shutil
import mutagen
from mutagen.id3 import ID3, UFID
import subprocess

def get_bitrate(file_path):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=bit_rate', '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        bitrate_str = result.stdout.strip()
        if bitrate_str:
            bitrate = int(bitrate_str)
            return bitrate
        else:
            print(f"ffprobe returned empty result for file {file_path}")
            return None
    except Exception as e:
        print(f"ffprobe error for file {file_path}: {e}")
        return None

def move_file(src, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    dest = os.path.join(dest_folder, os.path.basename(src))
    base, ext = os.path.splitext(dest)
    counter = 1
    while os.path.exists(dest):
        dest = f"{base}-{counter}{ext}"
        counter += 1
    shutil.move(src, dest)

def extract_musicbrainz_recording_id(file_path):
    try:
        audio = ID3(file_path)
        ufid_frames = audio.getall('UFID')
        for ufid in ufid_frames:
            if 'musicbrainz.org' in ufid.owner:
                return ufid.data.decode('utf-8')
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return None

def process_mp3_files(root_folder, missing_id_folder, to_be_deleted_folder):
    acoustid_map = {}
    musicbrainz_map = {}
    duplicates = []

    for subdir, _, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith(".mp3"):
                file_path = os.path.join(subdir, file)
                try:
                    audio = ID3(file_path)
                    acoustid = audio.get("TXXX:Acoustid Id")
                    musicbrainz = extract_musicbrainz_recording_id(file_path)

                    has_acoustid = acoustid is not None and acoustid.text[0] != ''
                    has_musicbrainz = musicbrainz is not None and musicbrainz != ''

                    if has_acoustid:
                        acoustid = acoustid.text[0]
                        if acoustid in acoustid_map:
                            duplicates.append((file_path, acoustid_map[acoustid]))
                        else:
                            acoustid_map[acoustid] = file_path
                    elif has_musicbrainz:
                        if musicbrainz in musicbrainz_map:
                            duplicates.append((file_path, musicbrainz_map[musicbrainz]))
                        else:
                            musicbrainz_map[musicbrainz] = file_path
                    else:
                        print(f"Moving to missingID: {file_path}")
                        move_file(file_path, missing_id_folder)

                except mutagen.id3.ID3NoHeaderError:
                    print(f"Moving to missingID (no ID3 header): {file_path}")
                    move_file(file_path, missing_id_folder)

    for file1, file2 in duplicates:
        bitrate1 = get_bitrate(file1)
        bitrate2 = get_bitrate(file2)

        if bitrate1 is None or bitrate2 is None:
            continue

        size1 = os.path.getsize(file1)
        size2 = os.path.getsize(file2)

        if bitrate1 > bitrate2 or (bitrate1 == bitrate2 and size1 > size2):
            move_file(file2, to_be_deleted_folder)
            print(f"keep: {file1}")
            print(f"   x: {file2}")
        else:
            move_file(file1, to_be_deleted_folder)
            print(f"keep: {file2}")
            print(f"   x: {file1}")

root_folder = "/Users/barry/Music/Store"
missing_id_folder = "/Users/barry/Music/MissingID"
to_be_deleted_folder = "/Users/barry/Music/Duplicates"

process_mp3_files(root_folder, missing_id_folder, to_be_deleted_folder)
