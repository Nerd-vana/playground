import pyaudio
import wave
import io
from ShazamAPI import Shazam

def record_audio(filename="output.wav", duration=10, sample_rate=44100):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=1024)
    
    print("Recording...")
    frames = []
    for _ in range(0, int(sample_rate / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)
    
    print("Finished recording")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save as WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    return filename

def identify_song(filename):
    with open(filename, 'rb') as file:
        audio_bytes = file.read()
    
    shazam = Shazam(audio_bytes)
    recognize_generator = shazam.recognizeSong()
    return next(recognize_generator)

def main():
    audio_file = record_audio()
    print("Identifying song...")
    try:
        result = identify_song(audio_file)
        if 'track' in result[1]:
            track = result[1]['track']
            print(f"Song: {track['title']}")
            print(f"Artist: {track['subtitle']}")
            print(f"Genre: {track.get('genre', 'N/A')}")
        else:
            print("Song not identified.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()