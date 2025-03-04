import os
from PIL import Image
import piexif
import sys

def get_image_files(directory):
    """Get list of JPEG and JPG files in the given directory."""
    image_files = []
    for file in os.listdir(directory):
        if file.lower().endswith(('.jpeg', '.jpg')):
            image_files.append(file)
    return image_files

def find_duplicates(directory):
    """Find and print duplicate images based on combined perceptual hashes."""
    image_files = get_image_files(directory)
    hashes = {}

    for image_file in image_files:
        img_path = os.path.join(directory, image_file)

        try:
            img = Image.open(img_path)
            exif_dict = piexif.load(img.info.get('exif', b''))
            combined_hash = exif_dict['Exif'].get(piexif.ExifIFD.UserComment, None)

            if combined_hash:
                combined_hash = combined_hash.decode()
            else:
                print(f"No hash found in EXIF metadata for {img_path}")
                continue
        except Exception as e:
            print(f"Error processing file {img_path}: {e}")
            continue

        if combined_hash in hashes:
            hashes[combined_hash].append(image_file)
        else:
            hashes[combined_hash] = [image_file]

    for hash_str, files in hashes.items():
        if len(files) > 1:
            print(f"Hash: {hash_str}")
            print("Files:")
            for file in files:
                print(f"  - {file}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python find_duplicates.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    find_duplicates(directory)

if __name__ == "__main__":
    main()
