from google.cloud import speech
from google.oauth2 import service_account
import io


# https://cloud.google.com/text-to-speech/docs/libraries#client-libraries-install-python
# https://cloud.google.com/text-to-speech/docs/voices
# https://cloud.google.com/text-to-speech/docs/voice-types

def transcribe_streaming(audio_file_path):
    json_file_path = "tts_secret.json"
    credentials = service_account.Credentials.from_service_account_file(json_file_path)
    client = speech.SpeechClient(credentials=credentials)

    def generate_chunks(audio_file_path, chunk_size=1024*32):
        with io.open(audio_file_path, "rb") as audio_file:
            while True:
                chunk = audio_file.read(chunk_size)
                if not chunk:
                    break
                yield speech.StreamingRecognizeRequest(audio_content=chunk)

    # langcode = "yue-HK"
    langcode = "en-US"

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=langcode,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True  # This enables interim results
    )

    requests = generate_chunks(audio_file_path)
    responses = client.streaming_recognize(
        config=streaming_config,
        requests=requests,
    )

    for response in responses:
        for result in response.results:
            if result.is_final:
                print("Final transcript: {}".format(result.alternatives[0].transcript))
            #else:
            #    print("Interim transcript: {}".format(result.alternatives[0].transcript))

# Use the function
transcribe_streaming("output-audio.wav")