#!/bin/bash

VLC_PASSWORD="123456"
LOGFILE="vlc_timestamps.txt"
VLC_URL="http://localhost:8080/requests/status.xml"

echo "VLC Controller and Timestamp Logger"
echo "Press any key to log the current timestamp."
echo "Press 'UP ARROW' to skip back 5 seconds."
echo "Press 'q' to quit."

# Function to get current time from VLC
get_vlc_time() {
    curl -s -u :$VLC_PASSWORD "$VLC_URL" | xmllint --xpath "//time/text()" - 2>/dev/null
}

# Function to format seconds to HH:MM:SS
format_time() {
    local seconds=$1
    printf "%02d:%02d:%02d" $((seconds / 3600)) $((seconds % 3600 / 60)) $((seconds % 60))
}

# Function to send command to VLC
send_vlc_command() {
    local command=$1
    local response=$(curl -s -u :$VLC_PASSWORD "$VLC_URL?command=$command")

    if [[ $response != *"<state>paused</state>"* ]] &&
        [[ $response != *"<state>playing</state>"* ]]; then
        echo "Failed to send command or VLC is not in playing state"
    else
        local timecode="$(echo  "$response" | xmllint --xpath "//time/text()" - 2>/dev/null)"
        echo -n "$(format_time $timecode) "
    fi
}

while true; do
    read -s -n 1 key

    if [[ $key == "q" ]]; then
        echo "Quitting..."
        break
    elif [[ $key == $'\e' ]]; then
        timestamp=$(get_vlc_time)
        read -s -n 2 arrow
        if [[ $arrow == "[A" ]]; then # Up arrow
            send_vlc_command "seek&val=-5"
        fi
    elif [[ $key == "a" ]]; then
        send_vlc_command "seek&val=-5"
    elif [[ $key == "s" ]]; then
        send_vlc_command "seek&val=-2"
    elif [[ $key == "d" ]]; then
        send_vlc_command "seek&val=+1"
    elif [[ $key == "f" ]]; then
        send_vlc_command "pl_pause"
        response=$(curl -s -u :$VLC_PASSWORD "$VLC_URL")
        if [[ $response == *"<state>paused</state>"* ]]; then
            echo "paused"
        elif [[ $response == *"<state>playing</state>"* ]]; then
            echo "resumed >>>>"
        fi
    elif [[ $key == "j" ]]; then
        timestamp=$(get_vlc_time)

        if [ -n "$timestamp" ]; then
            formatted_time=$(format_time $timestamp)
            echo "$formatted_time" >>"$LOGFILE"
            echo "Logged timestamp: $formatted_time"
        else
            echo "Failed to get timestamp from VLC"
        fi
    elif [[ $key == "k" ]]; then
            timestamp=$(get_vlc_time)

        if [ -n "$timestamp" ]; then
            formatted_time=$(format_time $timestamp)
            echo "$formatted_time" >>"$LOGFILE"
            echo "Logged timestamp: $formatted_time"
        else
            echo "Failed to get timestamp from VLC"
        fi
    fi
done
