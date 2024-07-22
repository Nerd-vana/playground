import os
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3

def list_files(root_dir):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.mp3'):
                src_file = os.path.join(subdir, file)
                try:
                    easy_tags = EasyID3(src_file)
                    id3_tags = ID3(src_file)

                    all_tags = {key: easy_tags.get(key) for key in easy_tags.keys()}
                    comments = id3_tags.getall("COMM")
                    
                    if comments and any("ToBeUpdate" in str(comment) for comment in comments):
                        print("========")
                    
                    all_tags['comment'] = [str(comment) for comment in comments]

                    print(f"{file} {all_tags}")

                except Exception as e:
                    print(f"Error reading tags from {src_file}: {e}")

if __name__ == "__main__":
#    root_directory = "/Users/barry/mp3category/check"  # Replace with your MP3 folder path
    root_directory = "/Users/barry/mp3category/check"  # Replace with your MP3 folder path
    
    list_files(root_directory)
