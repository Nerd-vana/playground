

import os
from mutagen.id3 import ID3, UFID

# Define the root folder
root_folder = '/Users/barry/Music/MissingID'

def extract_metadata_from_mp3(directory):
    files_metadata = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                try:
                    audio = ID3(file_path)
                    ufid_frames = audio.getall('UFID')
                    ufid_values = [uf.data.decode('utf-8') for uf in ufid_frames] if ufid_frames else None
                    metadata = {
                        "file_path": file_path,
                        "ufid": ufid_values,
                        # Add other ID3 tags here as needed
                    }
                    files_metadata.append(metadata)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return files_metadata

# Example usage
all_metadata = extract_metadata_from_mp3(root_folder)
for metadata in all_metadata:
    print(metadata)



