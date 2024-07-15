#!/bin/bash

usage() {
  echo "Usage : $0 \"message to be converted to audio\""
  echo " break / pause : {b<millisecond>}"
  echo " characters    : {c<characters>}"
  echo " date          : {d<dd-mm-yy>}"
  echo " verbatim      : {v<characters>}"
  echo " cardinal      : {n<number>}"
  echo " time          : {t<hh:mm:ssam/pm>}"
  echo " currency/price: {p<$/£xx.xx>}"
  echo " emphasis      : {e<your word>}"
  echo " high pitch    : {h<words in high pitch>}"
  echo " low pitch     : {l<words in low pitch>}"
  echo " fast 130%     : {f<words faster>}"
  echo " slow 80%      : {s<words slower>}"
  exit 1
}

get-jsonToken() {
  local token_json="$1"
  # Extract necessary information from the service account file
  local PROJECT_ID=$(jq -r '.project_id' <$token_json)
  local PRIVATE_KEY=$(jq -r '.private_key' <$token_json)
  local CLIENT_EMAIL=$(jq -r '.client_email' <$token_json)

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

  printf "%s" "${ACCESS_TOKEN}"

}

capitalize_and_clean() {
  local input_string="$1"

  # Capitalize the first character of each word
  local capitalized_string=$(echo "$input_string" |
    awk '{ for (i=1; i<=NF; i++) $i = toupper(substr($i, 1, 1)) tolower(substr($i, 2)) } 1')

  # Remove all punctuation and spaces
  local cleaned_string=$(echo "$capitalized_string" | tr -d '[:punct:]' | tr -d ' ')

  printf "%s" "$cleaned_string"
}

clean_text() {
  local input="$1"
  local output=""

  while [[ "$input" =~ \{([bcdenvtphlfs])([^}]*)\} ]]; do
    output+="${input%%\{*}"
    local tag="${BASH_REMATCH[1]}"
    local content="${BASH_REMATCH[2]}"

    case "$tag" in
    b) ;;                    # Do nothing for {b} tags
    *) output+="$content" ;; # Add content for other tags
    esac
    input="${input#*\}}"
  done
  output+="$input"
  printf "%s" "$output"
}

convert_to_ssml() {
  local input="$1"
  local output=""

  while [[ "$input" =~ \{([bcdevntphlfs])([^}]*)\} ]]; do
    output+="${input%%\{*}"
    local tag="${BASH_REMATCH[1]}"
    local content="${BASH_REMATCH[2]}"

    case "$tag" in
    b) output+="<break time=\"${content}ms\"/>" ;;
    c) output+="<say-as interpret-as=\"characters\">$content</say-as>" ;;
    d) output+="<say-as interpret-as=\"date\" format=\"dmy\">$content</say-as>" ;;
    e) output+="<emphasis>$content</emphasis>" ;;
    v) output+="<say-as interpret-as=\"verbatim\">$content</say-as>" ;;
    n) output+="<say-as interpret-as=\"cardinal\">$content</say-as>" ;;
    t) output+="<say-as interpret-as=\"time\" format=\"hms12\">$content</say-as>" ;;
    p) output+="<say-as interpret-as=\"currency\" language=\"$TTS_LANG\">$content</say-as>" ;;
    h) output+="<prosody pitch=\"high\">$content</prosody>" ;;
    l) output+="<prosody pitch=\"low\">$content</prosody>" ;;
    f) output+="<prosody rate=\"130%\">$content</prosody>" ;;
    s) output+="<prosody pitch=\"80%\">$content</prosody>" ;;
    esac

    input="${input#*\}}"
  done

  output+="$input"
  echo "$output"
}

clean_text_utf8() {
  local input="$1"
  local output=""

  # Convert to UTF-8 if not already
  input=$(echo "$input" | iconv -f UTF-8 -t UTF-8//IGNORE)

  # Loop to process tags
  while [[ "$input" =~ \{([bcdenvtphlfs])([^}]*)\} ]]; do
    output+="${input%%\{*}" # Add text before the tag to the output
    local tag="${BASH_REMATCH[1]}" # Extract tag type
    local content="${BASH_REMATCH[2]}" # Extract tag content

    case "$tag" in
    b) ;;                    # Ignore {b} tags
    *) output+="$content" ;; # Add content for other tags
    esac

    input="${input#*\}}" # Remove processed part from input
  done

  output+="$input" # Add remaining input to output
  printf "%s" "$output"
}

capitalize_and_clean_utf8() {
  local input_string="$1"

  # Convert to UTF-8 if not already
  input_string=$(echo "$input_string" | iconv -f UTF-8 -t UTF-8//IGNORE)

  # Capitalize the first character of each word (assuming spaces separate words)
  capitalized_string=$(echo "$input_string" | gawk '{
    for (i=1; i<=NF; i++) {
      $i = toupper(substr($i, 1, 1)) tolower(substr($i, 2))
    }
    print
  }')

  # Remove all punctuation and spaces, preserving multi-byte characters
  cleaned_string=$(echo "$capitalized_string" | tr -d '[:punct:]' | tr -d '[:space:]')

  printf "%s" "$cleaned_string"
}


main() {

  if [[ -z "$TTS_VOICE" || -z "$TTS_LANG" ]]; then
    echo "Error: Both TTS_VOICE and TTS_LANG must be set."
    exit 1
  fi
  text="$1"
  # https://cloud.google.com/text-to-speech/docs/ssml
  # https://www.w3.org/TR/speech-synthesis11/#S3.2.4

  # Your text, voice, and language settings
  #text="$1"
  #text='This is an {eimportant} notice announced on {d01-02-2024} by {cw h o} or {vw h o} at {t12:05pm}. {b200}Compared to the death toll of {n1997} in year 2003. Type {cget-this-number} or {vget-this-number} price {p£20.39}'
  #text='Come to LIDL, {esainsburys or morrisons Saturday} and {henjoy} a super discount.'
  #text="大家好，歡迎來到我的頻道。今日係{d13-07-2024}，天氣{e真}係好"
  #text="大家好，歡迎來到我的頻道。今日是{d13-07-2024}，天氣{e真}好"

  ACCESS_TOKEN=$(get-jsonToken "${GOOGLE_TOKEN_JSON}")

  ssml_content=$(convert_to_ssml "$text")

  ssml_json=$(jq -n \
    --arg ssml "$ssml_content" \
    --arg lang "$TTS_LANG" \
    --arg voice "$TTS_VOICE" \
    '{
    "input": {
      "ssml": "<speak>\($ssml)</speak>"
    },
    "voice": {
      "languageCode": $lang,
      "name": $voice
    },
    "audioConfig": {
      "audioEncoding": "MP3"
    }
  }')

  printf "ssml: \n%s\n\n" "$ssml_content"
  printf "ssml json: \n%s\n\n" "$ssml_json"

  tempAudio=$(mktemp)
  # Send request to API
  curl -X POST \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "$ssml_json" \
    "https://texttospeech.googleapis.com/v1/text:synthesize" >$tempAudio 2>/dev/null

  # Check if the output contains an error
  if grep -q "error" $tempAudio; then
    cat $tempAudio
  else
    cleaned_text=$(clean_text_utf8 "$text")
    identifier=$(capitalize_and_clean_utf8 "$cleaned_text")
    identifier="${identifier:0:40}"

    now=$(date +"%H%M%S")
    #identifier=$(echo $text | awk -F'[, .?]' '{print $1}')
    output="${now}-${identifier}.mp3"

    # Decode the base64 audio content
    cat $tempAudio | jq -r '.audioContent' | base64 -d >$output
    echo "Audio file created: $output"
  fi

  rm $tempAudio
}

GOOGLE_TOKEN_JSON="$HOME/.config/keyvault/keys/tts_secret.json"
#main  'Come to LIDL, {esainsburys or morrisons Saturday} and {henjoy} a super discount.'
main  "$1"

