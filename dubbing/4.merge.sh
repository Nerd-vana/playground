#!/bin/bash

project="$1"

timestamp_file="${project}/tmp/timestamp.txt"
silent_file="${project}/tmp/silent.wav"

# Function to process audio file
process_audio() {
    local pos=$1
    local audio_file=$2
    
    # Convert to milliseconds
    pos=$(echo "$pos * 1000" | bc | awk '{printf "%d\n", $1}')
    
    # Create a temporary file
    tempfile="$(mktemp).wav"

    # Overlay the audio file
    ffmpeg -i "$silent_file" -i "tmp/$audio_file" -filter_complex "[1:a]adelay=${pos}[delayed];[0:a][delayed]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[out]" -map "[out]" -hide_banner -loglevel error "$tempfile"

    # Move the temporary file to replace silent.wav
    mv "$tempfile" "$silent_file"
}

inputfile="${project}/input/video.mp4"

folder="${project}/tmp"
mkdir -p "$folder"

fullpath="$(realpath $inputfile)"
filename="${inputfile%.*}"

duration="$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 ${inputfile})"

ffmpeg  -hide_banner -loglevel error -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=24000 -t "$duration" -ac 1 "$folder/silent.wav"


awk -F'|' '{seen[$2]=$0} END {for (key in seen) print seen[key]}' "$timestamp_file" | sort -t'|' -k1,1n | while IFS='|' read -r pos audio_file
do
    printf "%s : %s\n" "$pos" "$audio_file"
    process_audio "$pos" "$audio_file"
done

mv "${project}/tmp/silent.wav" "${project}/output/merged.wav"
ffmpeg  -hide_banner -loglevel error -i "${project}/input/video.mp4" -i "${project}/output/merged.wav" -c:v copy -c:a aac -b:a 128k -ar 44100 -ac 1 -map 0:v:0 -map 1:a:0 "${project}/output/final.mp4"

