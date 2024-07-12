from google.cloud import texttospeech
from google.oauth2.service_account import Credentials

# Path to your service account key file
key_path = "tts_secret.json"

# Create credentials
credentials = Credentials.from_service_account_file(key_path)

# Create client
client = texttospeech.TextToSpeechClient(credentials=credentials)

# Performs the list voices request
voices = client.list_voices()

for voice in voices.voices:
    print(f"Name: {voice.name}")
    print(f"  Language codes: {voice.language_codes}")
    print(f"  Gender: {texttospeech.SsmlVoiceGender(voice.ssml_gender).name}")
    print(f"  Natural Sample Rate Hertz: {voice.natural_sample_rate_hertz}")