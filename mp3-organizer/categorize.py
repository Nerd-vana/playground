import os
import shutil
import re
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3

def sanitize_filename(filename):
    # Remove special characters and replace spaces with hyphens
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'\s+', '-', filename)
    return filename

def get_tag_or_misc(tags, key):
    return sanitize_filename(tags.get(key, ["Misc"])[0])

def move_file(src, dst):
    base, extension = os.path.splitext(dst)
    counter = 1
    while os.path.exists(dst):
        dst = f"{base}-{counter}{extension}"
        counter += 1
    shutil.move(src, dst)

def organize_music_files(root_dir, output_dir, special_folder):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.mp3'):
                src_file = os.path.join(subdir, file)

                tags = EasyID3(src_file)
                id3_tags = ID3(src_file)
                id3_comments = id3_tags.getall("COMM")

                if id3_comments and any("ToBeUpdate" in str(comment) for comment in id3_comments):
                    special_dst = os.path.join(output_dir, special_folder, file)
                    move_file(src_file, special_dst)
                    print(f"Moved {src_file} to {special_dst} (special folder)")
                    continue

                genre = get_tag_or_misc(tags, 'genre')
                compilation = get_tag_or_misc(tags, 'compilation')
                artist = get_tag_or_misc(tags, 'artist')
                album = get_tag_or_misc(tags, 'album')
                title = get_tag_or_misc(tags, 'title')

                if genre == 'Classical':
                    if compilation == '1':
                        classical_dir = os.path.join(output_dir, 'Classical')
                        album_dir = os.path.join(classical_dir, album)
                        os.makedirs(album_dir, exist_ok=True)

                        dst_file = os.path.join(album_dir, f"{title}.mp3")
                        move_file(src_file, dst_file)
                        print(f"Moved {src_file}")
                        print(f"   to {dst_file}")
                        continue
                    else:
                        classical_dir = os.path.join(output_dir, 'Classical')
                        artist_dir = os.path.join(classical_dir, artist)
                        album_dir = os.path.join(artist_dir, album)
                        os.makedirs(album_dir, exist_ok=True)

                        dst_file = os.path.join(album_dir, f"{title}.mp3")
                        move_file(src_file, dst_file)
                        print(f"Moved {src_file}")
                        print(f"   to {dst_file}")
                        continue

                if genre == 'Instrumental':
                    if compilation == '1':
                        classical_dir = os.path.join(output_dir, 'Instrumental')
                        album_dir = os.path.join(classical_dir, album)
                        os.makedirs(album_dir, exist_ok=True)

                        dst_file = os.path.join(album_dir, f"{title}.mp3")
                        move_file(src_file, dst_file)
                        print(f"Moved {src_file}")
                        print(f"   to {dst_file}")
                        continue
                    else:
                        classical_dir = os.path.join(output_dir, 'Instrumental')
                        artist_dir = os.path.join(classical_dir, artist)
                        album_dir = os.path.join(artist_dir, album)
                        os.makedirs(album_dir, exist_ok=True)

                        dst_file = os.path.join(album_dir, f"{title}.mp3")
                        move_file(src_file, dst_file)
                        print(f"Moved {src_file}")
                        print(f"   to {dst_file}")
                        continue

                if compilation == 1:
                    album_dir = os.path.join(output_dir, album)
                    os.makedirs(album_dir, exist_ok=True)

                    dst_file = os.path.join(album_dir, f"{title}.mp3")
                    move_file(src_file, dst_file)
                    print(f"Moved {src_file}")
                    print(f"   to {dst_file}")
                    continue
                else:
                    artist_dir = os.path.join(output_dir, artist)
                    album_dir = os.path.join(artist_dir, album)
                    os.makedirs(album_dir, exist_ok=True)

                    dst_file = os.path.join(album_dir, f"{title}.mp3")
                    move_file(src_file, dst_file)
                    print(f"Moved {src_file}")
                    print(f"   to {dst_file}")
                    continue

if __name__ == "__main__":
    root_directory   = "/Users/barry/mp3category/ToProcess"  # Replace with your MP3 folder path
    output_directory = "/Users/barry/Music/Store"  # Replace with your output folder path
    special_folder   = "/Users/barry/mp3category/ToBeUpdated"  # Folder for files with comment "ToBeUpdate"
    organize_music_files(root_directory, output_directory, special_folder)
