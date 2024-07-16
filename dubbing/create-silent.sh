
folder="tmp"
mkdir -p "$folder"

fullpath="$(realpath $1)"
filename="${1%.*}"

duration="$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 ${1})"

ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=24000 -t "$duration" -ac 1 "$folder/silent.wav"
