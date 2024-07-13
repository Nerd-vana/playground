seconds="$1"

ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=16000 -t $seconds silent.mp3


