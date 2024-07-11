
JSON=$(cat <<EOF
{
    "key1": {
        "subkey1": "value1",
        "subkey2": "value2"
    },
    "key2": {
        "subkey3": "value3",
        "subkey4": "value4"
    }
}
EOF
)

add_key_value_to_json() {
    local parent=$1
    local subkey=$2
    local value=$3
    local file_location=$4

    # Create the JSON file if it doesn't exist
    if [ ! -f "$file_location" ]; then
        echo "{}" > "$file_location"
    fi

    # Create a temporary file securely
    local tmp_file
    tmp_file=$(mktemp)

    # Initialize the parent if it doesn't exist or isn't an object
    jq --arg parent "$parent" 'if .[$parent] == null then .[$parent] = {} elif .[$parent] | type != "object" then error("Parent key is not an object") else . end' "$file_location" > "$tmp_file"
    
    if [ $? -ne 0 ]; then
        echo "Error: Parent key is not an object." >&2
        rm "$tmp_file"
        return 1
    fi
    
    mv "$tmp_file" "$file_location"

    # Check if the subkey exists under the parent
    if jq -e --arg parent "$parent" --arg subkey "$subkey" '.[$parent] | has($subkey)' "$file_location" > /dev/null; then
        echo "Subkey already exists under parent. Overwrite? (yes/no)" >&2
        read -r overwrite
        while [[ "$overwrite" != "yes" && "$overwrite" != "no" ]]; do
            echo "Invalid input. Please enter yes or no: " >&2
            read -r overwrite
        done

        if [ "$overwrite" == "yes" ]; then
            jq --arg parent "$parent" --arg subkey "$subkey" --arg value "$value" \
               '.[$parent][$subkey] = $value' "$file_location" > "$tmp_file" && mv "$tmp_file" "$file_location"
            echo "Key value updated successfully." >&2
        else
            echo "Operation aborted." >&2
            rm "$tmp_file"
            exit 1
        fi
    else
        # Add the new subkey-value pair under the parent
        jq --arg parent "$parent" --arg subkey "$subkey" --arg value "$value" \
           '.[$parent][$subkey] = $value' "$file_location" > "$tmp_file" && mv "$tmp_file" "$file_location"
        echo "Key value added successfully." >&2
    fi
}


add_key_value_to_json_new() {
    local parent=$1 subkey=$2 value=$3 file_location=$4
    local tmp_file

    # Create the JSON file if it doesn't exist
    [ -f "$file_location" ] || echo "{}" > "$file_location"

    # Create a temporary file securely
    tmp_file=$(mktemp)

    # Initialize the parent if it doesn't exist or isn't an object
    if ! jq --arg parent "$parent" 'if .[$parent] == null then .[$parent] = {} elif .[$parent] | type != "object" then error("Parent key is not an object") else . end' "$file_location" > "$tmp_file"; then
        echo "Error: Parent key is not an object." >&2
        rm "$tmp_file"
        return 1
    fi

    mv "$tmp_file" "$file_location"

    # Check if the subkey exists under the parent
    if jq -e --arg parent "$parent" --arg subkey "$subkey" '.[$parent] | has($subkey)' "$file_location" > /dev/null; then
        read -rp "Subkey already exists under parent. Overwrite? (yes/no): " overwrite
        while [[ "$overwrite" != "yes" && "$overwrite" != "no" ]]; do
            read -rp "Invalid input. Please enter yes or no: " overwrite
        done
        if [ "$overwrite" != "yes" ]; then
            echo "Operation aborted." >&2
            return 1
        fi
    fi

    # Add or update the subkey-value pair under the parent
    if jq --arg parent "$parent" --arg subkey "$subkey" --arg value "$value" \
        '.[$parent][$subkey] = $value' "$file_location" > "$tmp_file" && mv "$tmp_file" "$file_location"; then
        echo "Key value ${overwrite:+updated}${overwrite:-added} successfully."
    else
        echo "Error: Failed to modify JSON file." >&2
        rm "$tmp_file"
        return 1
    fi
}


get_key_value_in_json_new() {
    local key=$1 subkey=$2 file_location=$3
    jq -r --arg key "$key" --arg subkey "$subkey" '.[$key][$subkey] // empty' "$file_location"
}

get_key_value_in_file() {
    local key=$1
    local subkey=$2
    local file_location=$3

    local value=$(jq -r --arg key "$key" --arg subkey "$subkey" '.[$key][$subkey] // empty' "$file_location")
    printf "%s" "$value"
}



# echo $JSON > test.json

add_key_value_to_json "key1" "subkey2" "abcde" "test.json"
add_key_value_to_json "key1" "subkey3" "absdfsdfcde" "test.json"
add_key_value_to_json "key1" "subkey1" "absdfsdfe" "test.json"
add_key_value_to_json "key1" "subkey3" "absdfsdfsdfsdcde" "test.json"
add_key_value_to_json "key2" "subkey4" "absdfsdfcde" "test.json"
add_key_value_to_json "key3" "subkey1" "abfsdfcde" "test.json"
echo $(get_key_value_in_file "key1" "subkey2" "test.json")



json_file="test.json"

fzf_list=""

while IFS='|' read -r key value; do
    echo "Processing $key.subkey1: $value"
    fzf_list+="$key $value"$'\n'
done < <(jq -r '
    to_entries[] |
    select(.value.subkey1 != null) |
    "\(.key)|\(.value.subkey1)"
' "$json_file")


echo "$fzf_list" | fzf
# echo "$fzf_list" | fzf

jq -r 'keys[]' $json_file 

jq -r 'keys | reverse[]' $json_file 
jq -r 'keys[]' $json_file | sort -r

jq -r 'keys | sort[]' $json_file 

