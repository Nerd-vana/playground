#!/bin/bash

# Replace with your GitHub personal access token
TOKEN=$(gh auth token)
#TOKEN=$(get-keyvalue SUPER_GIST)

# Replace with your Gist ID
GIST_ID="6210ce668e923bd7b478ff9f965debee"

# First, let's check if we can access the Gist
gist_info=$(curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/gists/$GIST_ID")


if echo "$gist_info" | jq -e '.message == "Not Found"' > /dev/null; then
  echo "Error: Gist not found. Please check your Gist ID."
  exit 1
fi

# Get list of revisions
revisions=$(curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/gists/$GIST_ID/commits" | jq -r '.[].sha')

if [ -z "$revisions" ]; then
  echo "No revisions found or unable to fetch revisions."
  exit 1
fi

curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/gists/$GIST_ID/commits"  | jq '.[].url'

exit
# Loop through revisions
for revision in $revisions
do
  echo "Found revision: $revision"
  
     curl -X DELETE -H "Authorization: token $TOKEN" \
     "https://api.github.com/gists/$GIST_ID/$revision"

  # Uncomment the following lines when you're ready to delete revisions
  # curl -X DELETE -H "Authorization: token $TOKEN" \
  #   "https://api.github.com/gists/$GIST_ID/$revision"
  # 
  # echo "Attempted to delete revision $revision"
done

