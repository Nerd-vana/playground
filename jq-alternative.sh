get_json_value() {
    local json="$1"
    echo "$json" | awk -F'[{},:]' '{
        for (i=2; i<=NF; i++) {
                print $(i)
        }
    }'  | sed 's/^"// s/"$//'
}

json='{"abbreviation":"BST","day_of_year":192,"dst_offset":3600,"raw_offset":0,"timezone":"Europe/London","unixtime":1720627655,"utc_offset":"+01:00","week_number":28}'

timezone=$(get_json_value "$json" )
echo "$timezone"

