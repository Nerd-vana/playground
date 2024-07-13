#!/bin/bash

# Function to display usage instructions
usage() {
    echo "Usage: $0 <bot_token> <chat_id> <message>"
    exit 1
}

# Check if sufficient arguments are provided
if [ "$#" -ne 3 ]; then
    usage
fi

# Assign command-line arguments to variables
BOT_TOKEN="$1"
CHAT_ID="$2"
MESSAGE=$(echo -e "$3")

# Function to send message
send_message() {
    local bot_token="$1"
    local chat_id="$2"
    local message="$3"

    local response=$(curl -s -X POST "https://api.telegram.org/bot${bot_token}/sendMessage" \
        -d chat_id="${chat_id}" \
        -d text="${message}")

    # echo $response
}

# Send the message
send_message "${BOT_TOKEN}" "${CHAT_ID}" "${MESSAGE}"
