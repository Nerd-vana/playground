

mpv --osd-level=3 --osd-fractions --osd-status-msg='${time-pos} / ${duration}' --input-ipc-server=/tmp/mpvsocket --geometry=1200+100+50 --osd-fractions "$1"
