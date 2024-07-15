import re
import sys
from num2words import num2words
from datetime import datetime
import requests
import os
import time

# Constants
CHUNK_SIZE = 1024

XI_API_KEY =  os.getenv("ELEVENLABS_API_KEY")  # Replace with your actual API key
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
INPUT_FILE = "script.txt"

# Cardinal conversion functions (from the first script)

def date_to_cardinal(date_string):
    date_object = datetime.strptime(date_string, '%Y-%m-%d')
    year_cardinal = num2words(date_object.year)
    month_cardinal = num2words(date_object.month)
    day_cardinal = num2words(date_object.day)
    cardinal_date = f"{day_cardinal} {date_object.strftime('%B')} {year_cardinal}"
    return cardinal_date

def number_to_cardinal(number):
    return num2words(number)

def char_to_cardinal(char):
    special_chars = {
        '-': 'dash',
        ' ': 'space',
        ',': 'comma',
        '&': 'and',
        '=': 'equal',
        '+': 'plus',
        '/': 'divided by',
        '*': 'times',
        '(': 'open bracket',
        ')': 'close bracket',
        '0': 'zero',
        '1': 'one',
        '2': 'two',
        '3': 'three',
        '4': 'four',
        '5': 'five',
        '6': 'six',
        '7': 'seven',
        '8': 'eight',
        '9': 'nine'
    }
    if char.isalpha():
        return char.upper()
    elif char.isdigit():
        return num2words(int(char))
    else:
        return special_chars.get(char, char)

def string_to_cardinal(string):
    return ' '.join(char_to_cardinal(char) for char in string)

def time_to_cardinal(time_string):
    time_object = datetime.strptime(time_string, '%H:%M')
    hours = time_object.hour
    minutes = time_object.minute
    period = "AM" if hours < 12 else "PM"
    if hours == 0:
        hours = 12
    elif hours > 12:
        hours -= 12
    hours_cardinal = num2words(hours)
    minutes_cardinal = "zero " + num2words(minutes) if minutes < 10 else num2words(minutes)
    if minutes == 0:
        return f"{hours_cardinal} {period}"
    else:
        return f"{hours_cardinal} {minutes_cardinal} {period}"

def number_to_ordinal(number):
    return num2words(number, to='ordinal')

def generate_filename(text):
    # Remove spaces and punctuation, capitalize each word
    cleaned_text = re.sub(r'[^\w\s]', '', text)
    capitalized_text = ''.join(word.capitalize() for word in cleaned_text.split())
    # Truncate to 40 characters
    truncated_text = capitalized_text[:40]
    # Add timestamp
    timestamp = datetime.now().strftime("%H%M%S")
    return f"{timestamp}-{truncated_text}.mp3"

def process_sentence(sentence):
    def convert(match):
        type_ = match.group(1)
        value = match.group(2)
        try:
            if type_ == 't':
                return time_to_cardinal(value)
            elif type_ == 'd':
                return date_to_cardinal(value)
            elif type_ == 'n':
                return number_to_cardinal(int(value))
            elif type_ == 'c':
                return string_to_cardinal(value)
            elif type_ == 'o':
                return number_to_ordinal(int(value))
            elif type_ == 'b':
                return f'<break time="{value}s"/>'
            else:
                return value
        except Exception as e:
            print(f"Error processing {type_}:{value}. {str(e)}")
            return value

    pattern = r'\{(\w)([^}]+)\}'
    return re.sub(pattern, convert, sentence)

# Text-to-Speech function (modified from the second script)

def text_to_speech(text, output_path):
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    print(f"ssml: {text}")
    response = requests.post(tts_url, headers=headers, json=data, stream=True)
    
    if response.ok:
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        print(f"Audio saved successfully: {output_path}")
    else:
        print(f"Error: {response.text}")
    time.sleep(1)  # To ensure unique filenames and avoid overwhelming the API

# Main execution

def main():
    with open(INPUT_FILE, 'r') as file:
        for line in file:
            processed_line = process_sentence(line.strip())
            filename = generate_filename(line.strip())
            output_file = f"{filename}"
            print(f"{output_file}")
            text_to_speech(processed_line, output_file)


if __name__ == "__main__":
    main()
