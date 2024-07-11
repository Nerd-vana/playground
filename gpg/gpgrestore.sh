#!/bin/bash

# Path to the shared list file
LIST_FILE="./list.txt"

# Check if the list file exists
if [ ! -f "$LIST_FILE" ]; then
    echo "The list file does not exist."
    exit 1
fi

# Read the list file and present options to the user
echo "Select a folder to restore:"
select folder in $(cat "$LIST_FILE"); do
    if [ -n "$folder" ]; then
        break
    else
        echo "Invalid selection. Please try again."
    fi
done

# Get the folder name
folder_name=$(basename "$folder")

# Check if the encrypted file exists
encrypted_file="${folder}/${folder_name}.tar.gz.gpg"
if [ ! -f "$encrypted_file" ]; then
    echo "Encrypted file not found: $encrypted_file"
    exit 1
fi

# Decrypt the file
decrypted_file="${folder}/${folder_name}.tar.gz"
gpg --decrypt --output "$decrypted_file" "$encrypted_file"

if [ $? -ne 0 ]; then
    echo "Decryption failed."
    exit 1
fi

# Check the contents of the tar file
# echo "Contents of the tar file:"
# tar -tvzf "$decrypted_file"

# Extract the contents
echo "Extracting files..."
tar -xzf "$decrypted_file" -C "$folder" --strip-components=1

if [ $? -ne 0 ]; then
    echo "Extraction failed."
    rm "$decrypted_file"
    exit 1
fi

# Remove the decrypted tar file
rm "$decrypted_file"
# mv "$encrypted_file" "$HOME/.Trash"
# osascript -e "tell application \"Finder\" to delete POSIX file \"$encrypted_file\""
osascript -e "tell application \"Finder\" to delete POSIX file \"$encrypted_file\" with replacing"
# Remove the entry from the list file
sed -i '' "\|^$folder$|d" "$LIST_FILE"

echo "Restoration completed for $folder"
echo "Entry removed from $LIST_FILE"