import os
from google.cloud import speech
from google.oauth2 import service_account

# to detect frequency
# import wave

def get_sample_rate(audio_file_path):
    with wave.open(audio_file_path, 'rb') as wav_file:
        return wav_file.getframerate()

def transcribe_audio(audio_file_path):
    json_file_path = "tts_secret.json"
    credentials = service_account.Credentials.from_service_account_file(json_file_path)
    client = speech.SpeechClient(credentials=credentials)

    # Read the audio file
    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()

#    sample_rate = get_sample_rate(audio_file_path)    
    sample_rate = 16000

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))

# Use the function
transcribe_audio("output-audio.wav")