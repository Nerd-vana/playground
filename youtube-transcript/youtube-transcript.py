from youtube_transcript_api import YouTubeTranscriptApi

# pip install youtube-transcript-api

#For the URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
#The video ID is dQw4w9WgXcQ

video_id = 'zijUjJdegI8&t'
transcript = YouTubeTranscriptApi.get_transcript(video_id)

for entry in transcript:
    print(entry['text'])
