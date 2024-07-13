#!/bin/bash

# Azure Text-to-Speech API endpoint and credentials
#SUBSCRIPTION_KEY="your_subscription_key_here"
#REGION="your_azure_region_here"

SUBSCRIPTION_KEY=$(get-keyvalue.sh "azure speech service key 1")
REGION="westeurope"

ENDPOINT="https://${REGION}.tts.speech.microsoft.com/cognitiveservices/v1"

# Text to be converted to speech
#TEXT="Hello, this is a test of Azure Text-to-Speech service."
TEXT="你係唔係有問題"
TEXT="下一班列車將於三分鐘到站"

# Output audio file
OUTPUT_FILE="output.wav"

#https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech?tabs=streaming#convert-text-to-speech

#https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts

#langcode="en-GB"


#voice="en-GB-RyanNeural"
# voice="en-HK-SamNeural"
# voice="zh-TW-YunJheNeural"
voice="zh-HK-WanLungNeural"
voice='zh-TW-YunJheNeural'

sex="Male"  # match this with the information in the link above
langcode=$(echo "$voice" | cut -d '-' -f 1-2)

# Make the API request
HTTP_STATUS=$(curl -s -o "${OUTPUT_FILE}" -w "%{http_code}" \
    -X POST "${ENDPOINT}" \
    -H "Ocp-Apim-Subscription-Key: ${SUBSCRIPTION_KEY}" \
    -H "Content-Type: application/ssml+xml" \
    -H "X-Microsoft-OutputFormat: riff-24khz-16bit-mono-pcm" \
    -d "<speak version='1.0' xml:lang='${langcode}'>
        <voice xml:lang='en-US' xml:gender='${sex}' name='${voice}'>
        <prosody rate='+30%'>${TEXT}</prosody>
        </voice>
    </speak>")

: <<EOF
            <prosody rate='-20%' pitch='+15%'>
                ${TEXT}
            </prosody>
EOF

# Check HTTP status code
if [ ${HTTP_STATUS} -eq 200 ]; then
    echo "Text-to-Speech conversion successful. Output saved to ${OUTPUT_FILE}"
    echo "File size: $(wc -c < ${OUTPUT_FILE}) bytes"
else
    echo "Error occurred during Text-to-Speech conversion. HTTP Status: ${HTTP_STATUS}"
    echo "Response body:"
    cat "${OUTPUT_FILE}"
fi

