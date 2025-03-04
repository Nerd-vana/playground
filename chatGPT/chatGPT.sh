#!/bin/bash

# Set your API key here
OPENAI_API_KEY=$(get-keyvalue.sh OPENAI_KEY)

message="Hello, how can I use the ChatGPT API with bash?"


  response=$(curl -s https://api.openai.com/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
      "model": "text-ada-001",
      "messages": [{"role": "user", "content": "'"$message"'"}]
    }')

  echo "$response" | jq -r '.choices[0].message.content'

