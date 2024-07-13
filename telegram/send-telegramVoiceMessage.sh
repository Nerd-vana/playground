#!/bin/bash

# Function to display usage instructions
usage() {
    echo "Usage: $0 <bot_token> <chat_id> <audio file>"
    echo "suggest audio file in ogg, otherwise mp3"
    echo "ffmpeg -i input.mp3 -c:a libopus output.ogg"
    exit 1
}

# Check if sufficient arguments are provided
if [ "$#" -ne 3 ]; then
    usage
fi

# Assign command-line arguments to variables
BOT_TOKEN="$1"
CHAT_ID="$2"
MESSAGE="$3"

# Function to send message
send_message() {
    local bot_token="$1"
    local chat_id="$2"
    local message="$3"

local response=$(curl -s -X POST "https://api.telegram.org/bot${bot_token}/sendVoice" \
    -F chat_id="${chat_id}" \
    -F voice="@${message}")

echo $response


    echo $response
}

# Send the message
send_message "${BOT_TOKEN}" "${CHAT_ID}" "${MESSAGE}"
