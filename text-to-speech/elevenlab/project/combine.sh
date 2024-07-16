
ls *.mp3 | sort | sed "s/^/file '/; s/$/'/" > filelist.txt


ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp3

