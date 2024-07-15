#!/bin/bash

main() {

# Define the CSV file path
CSV_FILE="./azure-voices.csv"

# Check if the CSV file exists
if [[ ! -f "$CSV_FILE" ]]; then
    echo "CSV file not found: $CSV_FILE"
    return 1
fi

# Remove carriage return characters from the CSV file
cleaned_csv=$(mktemp)
tr -d '\r' < "$CSV_FILE" > "$cleaned_csv"

# Define the fixed width for each column
COL1_WIDTH=30
COL2_WIDTH=20
COL3_WIDTH=10
COL4_WIDTH=10
COL5_WIDTH=2

# Format the cleaned CSV file with fixed-width columns and use a pipe as a delimiter for fzf selection
selected_row=$(awk -F',' -v OFS='|' -v col1_width=$COL1_WIDTH -v col2_width=$COL2_WIDTH -v col3_width=$COL3_WIDTH -v col4_width=$COL4_WIDTH -v col5_width=$COL5_WIDTH '
NR > 1 {
    printf "%-*s|%-*s|%-*s|%-*s|%-*s\n", col1_width, $1, col2_width, $2, col3_width, $3, col4_width, $4, col5_width, $5
}' "$cleaned_csv" | fzf --delimiter='|' )

# Remove the temporary cleaned CSV file
rm "$cleaned_csv"

# Check if a row was selected
if [[ -z "$selected_row" ]]; then
    echo "No row selected"
    return 1
fi

# Parse the selected row into variables using pipe as a delimiter
IFS='|' read -r col1 col2 col3 col4 col5 <<< "$selected_row"

# Trim leading and trailing spaces from each variable
col1=$(echo "$col1" | xargs)
col2=$(echo "$col2" | xargs)
col3=$(echo "$col3" | xargs)
col4=$(echo "$col4" | xargs)

# Set environment variables
export TTS_NAME="$col1"
export TTS_VOICE="$col2"
export TTS_GENDER="$col3"
export TTS_LANG="$col4"

# Print the set environment variables
echo
echo "Environment variables set:"
echo "TTS_LANG   =$TTS_LANG"
echo "TTS_VOICE  =$TTS_VOICE"
echo "TTS_GENDER =$TTS_GENDER"
echo "TTS_NAME   =$TTS_NAME"

}

main

echo
if [[ "$0" =~ (zsh|bash)$ ]]; then
echo "Environment should have been set"
else
    echo "Don't forget to \"source\""
    echo "source $0"
    return 1 2>/dev/null || exit 1
fi

