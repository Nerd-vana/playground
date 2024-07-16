#!/bin/bash

subtitles_file="subtitles.txt"
output_file="timestamped_subtitles.txt"
mpv_socket="/tmp/mpvsocket"

function send_mpv_command() {
    echo "$1" | nc -U -w 1 $mpv_socket
}

function get_mpv_time() {
    send_mpv_command '{ "command": ["get_property", "time-pos"] }' | awk -F'"' '{print $4}'
}

function timestamp_subtitle() {
    local time=$(get_mpv_time)
    local subtitle="$1"
    echo "$time|$subtitle" >> "$output_file"
}

function process_key() {
    local key="$1"
    local selection="$2"
    case "$key" in
        t) timestamp_subtitle "$selection" ;;
        p) send_mpv_command '{ "command": ["cycle", "pause"] }' ;;
        b) send_mpv_command '{ "command": ["seek", "-3"] }' ;;
        f) send_mpv_command '{ "command": ["seek", "3"] }' ;;
        '[') send_mpv_command '{ "command": ["frame-back-step"] }' ;;
        ']') send_mpv_command '{ "command": ["frame-step"] }' ;;
        m) send_mpv_command '{ "command": ["cycle", "mute"] }' ;;
        enter) send_mpv_command "{ \"command\": [\"seek\", \"$selection\", \"absolute\"] }" ;;
    esac
}

export -f send_mpv_command get_mpv_time timestamp_subtitle process_key

cat "$subtitles_file" | fzf \
    --bind "ctrl-q:abort" \
    --expect "t,p,b,f,[,],m,enter" \
    --preview "echo 'Press: t (timestamp), p (pause), b (back 3s), f (forward 3s), [ (prev frame), ] (next frame), m (mute)'" \
    --preview-window "up:1" \
    --no-mouse \
    --layout=reverse-list \
    | while read -r key; read -r selection; do
        if [[ $key != enter ]]; then
            process_key "$key" "$selection"
        else
            process_key "$key" "$selection"
            break
        fi
    done

# Clean up
send_mpv_command '{ "command": ["quit"] }'