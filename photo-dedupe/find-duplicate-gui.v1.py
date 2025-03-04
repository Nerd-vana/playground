import os
import sys
from PIL import Image, ExifTags
import piexif
import imagehash
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import datetime

def get_image_files(directory):
    """Get list of JPEG and JPG files in the given directory."""
    image_files = []
    for file in os.listdir(directory):
        if file.lower().endswith(('.jpeg', '.jpg')):
            image_files.append(file)
    return image_files

def find_duplicates(directory):
    """Find duplicate images based on combined perceptual hashes."""
    image_files = get_image_files(directory)
    hashes = {}
    duplicates = []

    for image_file in image_files:
        img_path = os.path.join(directory, image_file)
        try:
            img = Image.open(img_path)
            exif_dict = piexif.load(img.info.get('exif', b''))
            combined_hash = exif_dict['Exif'].get(piexif.ExifIFD.UserComment, None)

            if combined_hash:
                combined_hash = combined_hash.decode()
            else:
                combined_hash = generate_hashes(img_path)
                add_hashes_to_exif(img_path, combined_hash)
        except Exception as e:
            print(f"Error processing file {img_path}: {e}")
            continue

        if combined_hash in hashes:
            duplicates.append((hashes[combined_hash], image_file))
        else:
            hashes[combined_hash] = image_file

    return duplicates

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

def extract_metadata(image_path):
    """Extract metadata from an image."""
    img = Image.open(image_path)
    exif_data = img._getexif()
    if not exif_data:
        return {}

    metadata = {}
    for tag, value in exif_data.items():
        tag_name = ExifTags.TAGS.get(tag, tag)
        metadata[tag_name] = value

    return metadata

def format_timestamp(timestamp):
    """Format the timestamp as yyyy-mm-dd hh:mm:ss."""
    if not timestamp:
        return "Unknown"
    try:
        dt = datetime.datetime.strptime(timestamp, '%Y:%m:%d %H:%M:%S')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return timestamp

class DuplicateResolver(QWidget):
    def __init__(self, duplicates):
        super().__init__()
        self.duplicates = duplicates
        self.current_index = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Duplicate Resolver')

        self.left_label = QLabel(self)
        self.right_label = QLabel(self)
        self.left_metadata_label = QLabel(self)
        self.right_metadata_label = QLabel(self)
        self.status_label = QLabel(self)

        self.keep_left_button = QPushButton('Keep Left', self)
        self.keep_right_button = QPushButton('Keep Right', self)

        self.keep_left_button.clicked.connect(self.keep_left)
        self.keep_right_button.clicked.connect(self.keep_right)

        hbox = QHBoxLayout()
        hbox.addWidget(self.left_label)
        hbox.addWidget(self.right_label)

        metadata_hbox = QHBoxLayout()
        metadata_hbox.addWidget(self.left_metadata_label)
        metadata_hbox.addWidget(self.right_metadata_label)

        left_vbox = QVBoxLayout()
        left_vbox.addLayout(metadata_hbox)
        left_vbox.addWidget(self.keep_left_button, alignment=Qt.AlignCenter)

        right_vbox = QVBoxLayout()
        right_vbox.addLayout(metadata_hbox)
        right_vbox.addWidget(self.keep_right_button, alignment=Qt.AlignCenter)

        outer_hbox = QHBoxLayout()
        outer_hbox.addLayout(left_vbox)
        outer_hbox.addLayout(right_vbox)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(outer_hbox)
        vbox.addWidget(self.status_label)

        self.setLayout(vbox)
        self.update_images()

    def update_images(self):
        if self.current_index < len(self.duplicates):
            left_image, right_image = self.duplicates[self.current_index]
            self.left_label.setPixmap(QPixmap(left_image).scaled(400, 400, Qt.KeepAspectRatio))
            self.right_label.setPixmap(QPixmap(right_image).scaled(400, 400, Qt.KeepAspectRatio))

            left_metadata = self.get_metadata_string(left_image)
            right_metadata = self.get_metadata_string(right_image)

            self.left_metadata_label.setText(left_metadata)
            self.right_metadata_label.setText(right_metadata)
            self.status_label.setText(f"Comparing {left_image} with {right_image}")
        else:
            self.status_label.setText("No more duplicates to resolve.")
            self.keep_left_button.setDisabled(True)
            self.keep_right_button.setDisabled(True)

    def get_metadata_string(self, image_path):
        metadata = extract_metadata(image_path)
        if not metadata:
            return "No metadata found."

        timestamp = format_timestamp(metadata.get('DateTimeOriginal'))
        gps_info = metadata.get('GPSInfo')
        resolution = Image.open(image_path).size
        last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(image_path)).strftime('%Y-%m-%d %H:%M:%S')

        metadata_str = f"Timestamp: {timestamp}\nResolution: {resolution}\nLast Modified: {last_modified}\n"
        if gps_info:
            gps_data = {
                'latitude': gps_info.get(2),
                'longitude': gps_info.get(4),
            }
            metadata_str += f"GPS: {gps_data}\n"

        additional_tags = ['Make', 'Model', 'LensModel', 'ExposureTime', 'FNumber', 'ISO', 'Flash', 'FocalLength', 'Software', 'Artist']
        for tag in additional_tags:
            value = metadata.get(tag)
            if value:
                metadata_str += f"{tag}: {value}\n"

        return metadata_str

    def keep_left(self):
        left_image, right_image = self.duplicates[self.current_index]
        os.remove(right_image)
        self.current_index += 1
        self.update_images()

    def keep_right(self):
        left_image, right_image = self.duplicates[self.current_index]
        os.remove(left_image)
        self.current_index += 1
        self.update_images()

def main():
    app = QApplication(sys.argv)
    
    if len(sys.argv) != 2:
        print("Usage: python find_duplicates.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    duplicates = find_duplicates(directory)
    
    if not duplicates:
        print("No duplicates found.")
        sys.exit(0)
    
    ex = DuplicateResolver(duplicates)
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
