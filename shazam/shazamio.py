import asyncio
import pyaudio
import numpy as np
from shazamio import Shazam

async def record_audio(duration=5, sample_rate=44100):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=1024)
    
    print("Recording...")
    frames = []
    for _ in range(0, int(sample_rate / 1024 * duration)):
        data = stream.read(1024)
        frames.append(np.frombuffer(data, dtype=np.float32))
    
    print("Finished recording")
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    return np.concatenate(frames)

async def identify_song(audio_data):
    shazam = Shazam()
    sample_rate = 44100
    return await shazam.recognize_song(audio_data.tobytes(), sample_rate)

async def main():
    audio_data = await record_audio()
    print("Identifying song...")
    result = await identify_song(audio_data)
    
    if 'track' in result:
        track = result['track']
        print(f"Song: {track['title']}")
        print(f"Artist: {track['subtitle']}")
        print(f"Genre: {track.get('genres', {}).get('primary', 'N/A')}")
    else:
        print("Song not identified.")

if __name__ == "__main__":
    asyncio.run(main())