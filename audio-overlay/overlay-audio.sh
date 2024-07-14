position_seconds="$1"
overlay_audio="$2"
base_audio="$3"
sample_rate=44100  # Define the sample rate here

# Convert the position from seconds to milliseconds
position_millisecond=$(echo "$position_seconds * 1000" | bc)

ffmpeg -i "$base_audio" -i "$overlay_audio" \
-filter_complex "[1]adelay=${position_millisecond}|${position_millisecond}[a1];[0]aresample=${sample_rate}[base];[a1]aresample=${sample_rate}[overlay];[base][overlay]amix=inputs=2" \
-c:a libmp3lame combined-overlay.mp3
