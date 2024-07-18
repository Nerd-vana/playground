#!/bin/bash

# Set your Google Cloud project ID and the path to your service account key file
PROJECT_ID="acoustic-bridge-429209-h8"
KEY_FILE="$HOME/.config/keyvault/keys/acoustic-bridge-429209-h8-e0b2329daffc.json"

# Set your source and target languages
SOURCE_LANG="en"
TARGET_LANG="es"

# The text you want to translate
TEXT="Hello, world!"

# Get an access token
ACCESS_TOKEN=$(curl -s -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=$(
    openssl base64 -in ${KEY_FILE} | tr -d '\n'
  )" \
  "https://oauth2.googleapis.com/token" | jq -r .access_token)

# Make the API request
RESPONSE=$(curl -s -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  "https://translation.googleapis.com/v3/projects/${PROJECT_ID}:translateText" \
  -d @- <<EOF
{
  "sourceLanguageCode": "${SOURCE_LANG}",
  "targetLanguageCode": "${TARGET_LANG}",
  "contents": ["${TEXT}"]
}
EOF
)
echo $RESPONSE

# Extract the translated text
TRANSLATED=$(echo $RESPONSE | jq -r '.translations[0].translatedText')

echo "Original: $TEXT"
echo "Translated: $TRANSLATED"
