
echo "{ \"command\": [\"seek\", \"$1\"] }" | nc -U /tmp/mpvsocket
