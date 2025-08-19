
KEY=$(get-keyvalue.sh "GEMINI_API_KEY")
VER="gemini-2.5-flash"
# VER="gemini-2.0-flash"
# PROMPT="Explain how AI works in a few words"
PROMPT="What is the English level of the word 'Enterprise'"

curl "https://generativelanguage.googleapis.com/v1beta/models/${VER}:generateContent?key=${KEY}" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d "{
    \"contents\": [
      {
        \"parts\": [
          {
            \"text\": \"${PROMPT}\"
          }
        ]
      }
    ]
  }"
