from google.cloud import texttospeech
from google.oauth2.service_account import Credentials

# https://cloud.google.com/text-to-speech/docs/libraries#client-libraries-install-python
# https://cloud.google.com/text-to-speech/docs/voices
# https://cloud.google.com/text-to-speech/docs/voice-types
# pip install google-cloud-texttospeech

# Path to your service account key file
key_path = "tts_secret.json"

# Create credentials
credentials = Credentials.from_service_account_file(key_path)

# Create client
client = texttospeech.TextToSpeechClient(credentials=credentials)

# Set the text input to be synthesized
text = "umm.... This is some text to be converted to speech."
#text = "你好嗎"
synthesis_input = texttospeech.SynthesisInput(text=text)

# Build the voice request
#language_code = 'en-GB'  # Choose a supported language code
#voice_name = 'en-GB-Standard-C'

#language_code = 'yue-HK'  # Choose a supported language code
#voice_name = 'yue-HK-Standard-D'

# language_code = 'en-GB' 
voice_name = 'en-US-Journey-F'
language_code = voice_name.split('-')[0] + '-' + voice_name.split('-')[1]

voice = texttospeech.VoiceSelectionParams(
    language_code=language_code,
    name=voice_name  # Choose a voice from the documentation
)

# Select the type of audio file you want returned
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

# Perform the text-to-speech request
response = client.synthesize_speech(
    input=synthesis_input,
    voice=voice,
    audio_config=audio_config
)

outfile='output' + voice_name + '.mp3'

# The response's audio_content is binary
with open(outfile, "wb") as out:
    out.write(response.audio_content)

print("Text-to-speech audio saved as " + outfile)