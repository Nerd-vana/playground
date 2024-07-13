input="$1"

output="testing.mp3"

ffmpeg -i $input compare.mp3

#timecode="-ss 00:00:20 -t 00:00:5"
#timecode="-ss 00:05:00 -t 00:10:00"

#ffmpeg -i $input -ac 1 -b:a 64k \
#-filter:a "highpass=f=80, lowpass=f=1500" $output