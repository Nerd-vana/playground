#!/bin/bash

subtitles_file="subtitles.txt"
output_file="timestamped_subtitles.txt"
mpv_socket="/tmp/mpvsocket"

function send_mpv_command() {
    echo "$1" | nc -U -w 1 $mpv_socket > /dev/null
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

fzf_command="cat \"$subtitles_file\" | fzf --bind \"ctrl-q:abort\" \
    --bind \"t:execute-silent(process_key t {})\" \
    --bind \"p:execute-silent(process_key p {})\" \
    --bind \"b:execute-silent(process_key b {})\" \
    --bind \"f:execute-silent(process_key f {})\" \
    --bind \"[:execute-silent(process_key [ {})\" \
    --bind \"]:execute-silent(process_key ] {})\" \
    --bind \"m:execute-silent(process_key m {})\" \
    --bind \"enter:execute-silent(process_key enter {})+accept\" \
    --header 'Keys: t (timestamp), p (pause), b (back 3s), f (forward 3s), [ (prev frame), ] (next frame), m (mute), enter (seek), ctrl-q (quit)' \
    --no-mouse \
    --layout=reverse-list"

eval "$fzf_command"