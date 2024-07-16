#!/bin/bash

# Check if the input and tmp directories exist, if not create them
mkdir -p input tmp

# Iterate over all mp3 files in the input directory
for file in input/*.mp3; do
  if [[ -f "$file" ]]; then
    # Extract the filename without the extension
    filename=$(basename "$file" .mp3)
    # Convert mp3 to wav using ffmpeg
    ffmpeg -i "$file" -ac 1 -ar 24000 "tmp/${filename}.wav"
  fi
done

ls tmp/*.wav | xargs -n 1 basename | sort > tmp/wav.txt

echo "Conversion completed."
