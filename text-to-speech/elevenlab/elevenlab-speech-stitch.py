import os
import requests
from pydub import AudioSegment
import io
from datetime import datetime
import re

#pip install pydub
#pip install requests

YOUR_XI_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George

PARAGRAPHS = [
    "Today is <break time='1.0s' />01-02-2024" 
]

def generate_filename(text):
    # Remove spaces and punctuation, capitalize each word
    cleaned_text = re.sub(r'[^\w\s]', '', text)
    capitalized_text = ''.join(word.capitalize() for word in cleaned_text.split())
    # Truncate to 40 characters
    truncated_text = capitalized_text[:40]
    # Add timestamp
    timestamp = datetime.now().strftime("%H%M%S")
    return f"{timestamp}-{truncated_text}.mp3"

previous_request_ids = []

for i, paragraph in enumerate(PARAGRAPHS):
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream",
        json={
            "text": paragraph,
            "model_id": "eleven_multilingual_v2",
            "previous_request_ids": previous_request_ids[-3:],
        },
        headers={"xi-api-key": YOUR_XI_API_KEY},
    )
    
    if response.status_code != 200:
        print(f"Error encountered, status: {response.status_code}, "
               f"content: {response.text}")
        quit()
    
    print(f"Successfully converted paragraph {i + 1}/{len(PARAGRAPHS)}")
    previous_request_ids.append(response.headers["request-id"])
    
    # Generate filename
    filename = generate_filename(paragraph)
    
    # Save audio segment as individual file
    audio_segment = AudioSegment.from_mp3(io.BytesIO(response.content))
    audio_out_path = os.path.join(os.getcwd(), filename)
    audio_segment.export(audio_out_path, format="mp3")
    
    print(f"Saved audio file: {filename}")

print("All audio files have been saved successfully.")
