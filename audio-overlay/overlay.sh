
pos=$(echo "$3 * 1000" | bc)

tempfile="$(mktemp).wav"

short="$(realpath $1)"
long="$(realpath $2)"

#ffmpeg -i "$long" -i "$short" -filter_complex "[1:a]adelay=$pos[delayed];[0:a][delayed]amix=inputs=2:duration=first:weights=1 1[out]" -map "[out]" "$tempfile"


ffmpeg -i "$long" -i "$short" -filter_complex \
"[1:a]adelay=$pos[delayed];[0:a][delayed]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[out]" \
-map "[out]" -hide_banner -loglevel error "$tempfile" 

mk-version.sh "$long"

mv "$tempfile" "$long"


