input="$1"

# ffmpeg -i $input -af "silenceremove=start_periods=1:start_duration=1:start_threshold=-50dB:stop_periods=1:stop_duration=1:stop_threshold=-50dB" $1-trimed.mp3

ffmpeg -i $input -af "silenceremove=stop_periods=-1:stop_duration=1:stop_threshold=-50dB" $1-trim.mp3
