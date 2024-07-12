from gtts import gTTS
import os


text = "Hello love"

#tts = gTTS(text=text, lang='en-us')
tts = gTTS(text=text, lang='en', slow=False, tld='com.au')
tts.save("hello_en.mp3")

#tts = gTTS(text=text, lang='en-gb', slow=True)
#tts.save("hello_gb.mp3")

