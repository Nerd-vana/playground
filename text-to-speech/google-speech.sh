#!/bin/bash

if [[ -z "$TTS_VOICE" || -z "$TTS_LANG" ]]; then
    echo "Error: Both TTS_VOICE and TTS_LANG must be set."
    exit 1
fi

# Your text, voice, and language settings
#text="$1"
text="Can you do this?"
voice_name=$TTS_VOICE
language_code=$TTS_LANG


get-jsonToken() {

  # Extract necessary information from the service account file
  local PROJECT_ID=$(jq -r '.project_id' < $SERVICE_ACCOUNT_FILE)
  local PRIVATE_KEY=$(jq -r '.private_key' < $SERVICE_ACCOUNT_FILE)
  local CLIENT_EMAIL=$(jq -r '.client_email' < $SERVICE_ACCOUNT_FILE)

  # Create JWT header and claim
  local HEADER=$(echo -n '{"alg":"RS256","typ":"JWT"}' | base64 | tr '+/' '-_' | tr -d '=')
  local NOW=$(($(date +%s)))
  local EXPIRY=$((NOW + 3600))
  local CLAIM=$(echo -n "{\"iss\":\"$CLIENT_EMAIL\",\"scope\":\
  \"https://www.googleapis.com/auth/cloud-platform\",\
  \"aud\":\"https://oauth2.googleapis.com/token\",\"exp\":\"$EXPIRY\",\"iat\":\"$NOW\"}" | 
  base64 | tr '+/' '-_' | tr -d '=')

  # Create JWT signature
  local SIGNATURE=$(echo -n "$HEADER.$CLAIM" | openssl dgst -binary -sha256 -sign <(echo "$PRIVATE_KEY") | 
  base64 | tr '+/' '-_' | tr -d '=')

  # Combine to form the full JWT
  local JWT="$HEADER.$CLAIM.$SIGNATURE"

  # Exchange JWT for Access Token
  local ACCESS_TOKEN=$(curl -s -d \
  "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=$JWT" \
  https://oauth2.googleapis.com/token | jq -r .access_token)

 echo -n "$ACCESS_TOKEN"

}

# Path to your service account JSON file
SERVICE_ACCOUNT_FILE="tts_secret.json"

ACCESS_TOKEN=$(get-jsonToken $SERVICE_ACCOUNT_FILE)


capitalize_and_clean() {
    local input_string="$1"

    # Capitalize the first character of each word
    capitalized_string=$(echo "$input_string" | awk '{ for (i=1; i<=NF; i++) $i = toupper(substr($i, 1, 1)) tolower(substr($i, 2)) } 1')

    # Remove all punctuation and spaces
    cleaned_string=$(echo "$capitalized_string" | tr -d '[:punct:]' | tr -d ' ')

    echo "$cleaned_string"
}



identifier=$(capitalize_and_clean "$text")

echo "$voice_name"

temp=$(mktemp)

now=$(date +"%H%M%S")
#identifier=$(echo $text | awk -F'[, .?]' '{print $1}')
output="${now}-${identifier}.mp3"

# Make the API request
curl -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{
    \"input\": {
      \"text\": \"$text\"
    },
    \"voice\": {
      \"languageCode\": \"$language_code\",
      \"name\": \"$voice_name\"
    },
    \"audioConfig\": {
      \"audioEncoding\": \"MP3\"
    }
  }" \
  "https://texttospeech.googleapis.com/v1/text:synthesize" > $temp 2>/dev/null

# Check if the output contains an error
if grep -q "error" $temp; then
  cat $temp
else
  # Decode the base64 audio content
  cat $temp | jq -r '.audioContent' | base64 -d > $output
  echo "Audio file created: $output"
fi

rm $temp
