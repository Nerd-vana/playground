import os
from PIL import Image
import imagehash
import piexif
import sys

def generate_hashes(img_path):
    """Generate multiple perceptual hashes for an image."""
    img = Image.open(img_path)
    ahash = imagehash.average_hash(img)
    phash = imagehash.phash(img)
    dhash = imagehash.dhash(img)
    whash = imagehash.whash(img)
    combined_hash = f'a:{ahash},p:{phash},d:{dhash},w:{whash}'
    return combined_hash

def add_hashes_to_exif(image_path, combined_hash):
    """Embed the combined hashes into the EXIF metadata of the image."""
    img = Image.open(image_path)
    exif_dict = piexif.load(img.info.get('exif', b''))
    exif_dict['Exif'][piexif.ExifIFD.UserComment] = combined_hash.encode()
    exif_bytes = piexif.dump(exif_dict)
    img.save(image_path, "jpeg", exif=exif_bytes)

def main():
    if len(sys.argv) != 2:
        print("Usage: python embed_hash.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    combined_hash = generate_hashes(image_path)
    add_hashes_to_exif(image_path, combined_hash)
    print(f"Combined hash {combined_hash} added to EXIF metadata of the image {image_path}")

if __name__ == "__main__":
    main()
