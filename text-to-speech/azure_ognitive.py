import azure.cognitiveservices.speech as speechsdk
import os

# Replace with your own subscription key and region
#speech_key = "YOUR_SUBSCRIPTION_KEY"
#service_region = "YOUR_SERVICE_REGION"

speech_key = os.getenv('SPEECH_KEY', '')
service_region = "westeurope"


# Configure speech synthesizer
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Set the voice name, e.g., "en-GB-RyanNeural" for a British male voice
speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"

# Create a speech synthesizer
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

# Text to synthesize
text = "Hello love"

# Synthesize speech
result = speech_synthesizer.speak_text_async(text).get()

# Check result
if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized for text [{}]".format(text))
    # Save the synthesized audio to a file
    audio_data = result.audio_data
    file_name = "output.wav"
    with open(file_name, "wb") as audio_file:
        audio_file.write(audio_data)
    print("Audio saved to {}".format(file_name))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))

