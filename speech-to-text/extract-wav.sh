
input="$1"

output="output-audio.wav"

#timecode="-ss 00:00:20 -t 00:00:5"
timecode="-ss 00:05:00 -t 00:10:00"

ffmpeg -i $input $timecode -ac 1 -ar 16000 \
-filter:a "highpass=f=300, lowpass=f=3000" \
-vn $output
