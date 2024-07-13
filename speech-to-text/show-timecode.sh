input="$1"

ffplay -i $input -vf "drawtext=text='%{pts \:hms} ':fontsize=24:fontcolor=white:x=10:y=10"
