1. Put all mp3s into ToProcess folder
2. Use MusicBrainz to adding tags.
    genre : Instrumental / Classical
    remove Comment:n
    add acoustid, musicbrainz recording id
3. python categorize.py 
4. python remove-duplicates.py (this script use acoustid and musicbrainz id to check for duplciates, you may need to run it multiple times)
5. Fidn empty folders find /path/to/search -type d -empty -not -name ".DS_Store"
