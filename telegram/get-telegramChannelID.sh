#!/bin/bash
BOT_TOKEN=$(get-keyvalue.sh "stellarhub_bot")

# you can find the channel ID from the share link
# e.g. if share link is https://t.me/abcdefg
# channel ID is "abcdefg"
# chat_id="@you channel id"
chat_id="@us_news_demo"
message="Test only. Please ignore"
encoded_message="${message// /%20}"

urlstring="https://api.telegram.org/bot${BOT_TOKEN}/sendMessage?text=${encoded_message}&chat_id=${chat_id}"

response=$(curl -s -X POST "${urlstring}")

chat_id=$(echo "$response" | jq '.result.chat.id')

echo "chat_id: $chat_id"

