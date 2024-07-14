#!/bin/bash

# Check if a filename is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <csv_file>"
    exit 1
fi

input_file="$1"

# Check if the file exists
if [ ! -f "$input_file" ]; then
    echo "Error: File $input_file not found"
    exit 1
fi

# Declare a global array
declare -a global_array

# Function to parse a CSV line
parse_csv_line() {
    local line="$1"
    local fields=()
    local field=""
    local in_quotes=false

    while IFS= read -r -n1 char; do
        if [[ $char == '"' && $in_quotes == false ]]; then
            in_quotes=true
        elif [[ $char == '"' && $in_quotes == true ]]; then
            in_quotes=false
        elif [[ $char == ',' && $in_quotes == false ]]; then
            fields+=("$field")
            field=""
        else
            field+="$char"
        fi
    done < <(echo -n "$line")

    # Add the last field
    fields+=("$field")

    # Append to global array
    global_array+=("${fields[@]}")
}

# Read the CSV file line by line
line_number=0
while IFS= read -r line; do
    ((line_number++))
    
    # Parse the line and store fields in the global array
    parse_csv_line "$line"
    
    # Print each field on a separate line
    echo "Line $line_number:"
    start_index=$((line_number - 1)) * 4  # Assuming 4 fields per line
    for i in {0..3}; do
        echo "  Field $((i+1)): ${global_array[start_index + i]}"
    done
    echo "" # Print a blank line between each CSV line for readability
done < "$input_file"

# Print the entire array
echo "Printing entire array:"
printf "%s\n" "${global_array[@]}"

echo "Printing array elements one by one:"
for element in "${global_array[@]}"; do
    printf "%s\n" "$element"
done