GOOGLE_API_KEY=$(get-keyvalue.sh GOOGLE_AI_STUDIO_API_acoustic-bridge-429209-h8)
MODEL="gemini-1.5-flash"

text="Please translate to Taiwan traditional Chinese.  Do not give pinyin. 'change directory into keyvault directory.'"

response="$(curl https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${GOOGLE_API_KEY} \
    -H 'Content-Type: application/json' \
    -d '{
            "contents":[{
                "parts":[
                    {"text": "'"${text}"'"}
                ]}
            ]
        }')"

response_test=$(echo "${response}" | jq '.candidates[0].content.parts[0].text' )
clean_text=$(echo "$response_test" | sed 's/\\"/"/g')
printf "%b" "$clean_text"

