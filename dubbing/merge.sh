#!/bin/bash

# Path to timestamp file
timestamp_file="tmp/timestamp.txt"
# Path to silent.wav
silent_file="tmp/silent.wav"

# Function to process audio file
process_audio() {
    local pos=$1
    local audio_file=$2
    
    # Convert to milliseconds
    pos=$(echo "$pos * 1000" | bc | awk '{printf "%d\n", $1}')
    
    # Create a temporary file
    tempfile="$(mktemp).wav"

 echo $pos
 echo $audio_file

    # Overlay the audio file
    ffmpeg -i "$silent_file" -i "tmp/$audio_file" -filter_complex "[1:a]adelay=${pos}[delayed];[0:a][delayed]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[out]" -map "[out]" -hide_banner -loglevel error "$tempfile"

    now=$(date +"%s")
    cp "$tempfile" "$now.wav"
    # Move the temporary file to replace silent.wav
    mv "$tempfile" "$silent_file"
}

# Read the timestamp file, sort it, and keep only the last occurrence of each audio file
sort -t'|' -k2,2 -k1,1rn "$timestamp_file" | sort -t'|' -k2,2 -u | while IFS='|' read -r pos audio_file
do
    process_audio "$pos" "$audio_file"
done
