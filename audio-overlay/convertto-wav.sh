
folder="wav"
mkdir -p "$folder"

filename="${1%.*}"

# filename=$(basename "$1" .mp3)

ffmpeg -i "$1" -ac 1 -ar 24000 "$folder/${filename}.wav"

# ffmpeg -i "$1" -ac 1 -acodec pcm_s16le "$folder/${filename}_pcm.wav"
