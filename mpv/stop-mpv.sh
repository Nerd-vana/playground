
#echo '{ "command": ["set_property", "pause", true] }' | nc -U /tmp/mpvsocket

echo '{ "command": ["cycle", "pause"] }' | nc -U /tmp/mpvsocket
