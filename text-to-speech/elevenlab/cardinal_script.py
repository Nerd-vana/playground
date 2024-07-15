import re
import sys
from num2words import num2words
from datetime import datetime

# Provided functions
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

# Function to process the sentence
def process_sentence(sentence):
    def convert(match):
        type_ = match.group(1)
        value = match.group(2)
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

    pattern = r'\{(\w)([^}]+)\}'
    return re.sub(pattern, convert, sentence)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py '<sentence>'")
        sys.exit(1)

    input_sentence = sys.argv[1]
    processed_sentence = process_sentence(input_sentence)
    print(f"The processed sentence is: {processed_sentence}")

# python cardinal_script.py "Meeting at {t14:05} {b2.5} on {d2024-07-15}. Your number is {n324}. Spell {cwho}. Ordinal {o33}."
