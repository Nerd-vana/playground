#!/bin/bash

# File containing the script for the YouTube video
input_file="script.txt"

# Temporary file to store processed lines
temp_file=$(mktemp)

# Read each line from the input file
while IFS= read -r line; do
    # Process the line using the external script
    #echo "./google-speech.sh \"$line\""
    ./google-speech.sh "${line}"
    # Add "x|" to the beginning of the line
    processed_line="x|$line"
    sleep 1
    # Save the processed line to the temporary file
    echo "$processed_line" >>"$temp_file"
done <"$input_file"

# Replace the original file with the processed content
mv "$temp_file" "$input_file-new"

# Clean up the temporary file
rm -f "$temp_file"
