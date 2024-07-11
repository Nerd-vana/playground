#!/bin/bash

# Check if a folder path is provided as an argument
if [ $# -eq 0 ]; then
    echo "Please provide the folder path as an argument."
    exit 1
fi

# Set the folder path
folder_path="$1"

# Check if the folder exists
if [ ! -d "$folder_path" ]; then
    echo "The specified folder does not exist."
    exit 1
fi

# Get the folder name
folder_name=$(basename "$folder_path")

# Create a temporary directory within the folder
temp_dir="${folder_path}/.temp_backup_$(date +%s)"
mkdir "$temp_dir"

# Create the tar.gz file in the temporary directory, excluding the temp directory itself
tar_file="${temp_dir}/${folder_name}.tar.gz"
tar -czpf "$tar_file" -C "$folder_path" --exclude="./$(basename "$temp_dir")" .

# Encrypt the tar.gz file
encrypted_file="${folder_name}.tar.gz.gpg"
gpg --encrypt --recipient ECC-pass --output "${temp_dir}/${encrypted_file}" "$tar_file"

# Remove all files in the original folder except the temp directory
find "$folder_path" -maxdepth 1 -type f -delete

# Remove all subdirectories in the original folder except the temp directory
find "$folder_path" -mindepth 1 -maxdepth 1 -type d ! -name "$(basename "$temp_dir")" -exec rm -rf {} +

# Move the encrypted file to the original folder
mv "${temp_dir}/${encrypted_file}" "$folder_path/"

# Remove the temporary directory
rm -rf "$temp_dir"

# Add the folder path to the shared list
echo "$folder_path" >> ./list.txt

echo "Backup and encryption completed for $folder_path"