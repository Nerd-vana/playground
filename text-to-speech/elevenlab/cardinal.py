from num2words import num2words
from datetime import datetime

# pip-install num2words


def date_to_cardinal(date_string):
    # Parse the date string
    date_object = datetime.strptime(date_string, '%Y-%m-%d')
    
    # Convert each part of the date to its cardinal form
    year_cardinal = num2words(date_object.year)
    month_cardinal = num2words(date_object.month)
    day_cardinal = num2words(date_object.day)
    
    # Format the cardinal date
    cardinal_date = f"{day_cardinal} {date_object.strftime('%B')} {year_cardinal}"
    return cardinal_date

def number_to_cardinal(number):
    return num2words(number)

def char_to_cardinal(char):
    # Dictionary for special characters
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
    # Parse the time string
    time_object = datetime.strptime(time_string, '%H:%M')
    
    # Extract hours and minutes
    hours = time_object.hour
    minutes = time_object.minute
    
    # Determine AM or PM
    period = "AM" if hours < 12 else "PM"
    
    # Convert hours to 12-hour format
    if hours == 0:
        hours = 12
    elif hours > 12:
        hours -= 12
    
    # Convert hours and minutes to cardinal form
    hours_cardinal = num2words(hours)
    minutes_cardinal = "oh " + num2words(minutes) if minutes < 10 else num2words(minutes)
    
    if minutes == 0:
        return f"{hours_cardinal} {period}"
    else:
        return f"{hours_cardinal} {minutes_cardinal} {period}"

def number_to_ordinal(number):
    return num2words(number, to='ordinal')

# Example usage
number = 21
ordinal_form = number_to_ordinal(number)
print(f"The ordinal form of {number} is: {ordinal_form}")


# Example usage
time_string = '23:25'
cardinal_form = time_to_cardinal(time_string)
print(f"The cardinal form of the time {time_string} is: {cardinal_form}")

# Example usage
input_string = 'get-me (7)'
cardinal_form = string_to_cardinal(input_string)
print(f"The cardinal form of '{input_string}' is: {cardinal_form}")

# Example usage
date_string = '2024-07-15'
cardinal_form = date_to_cardinal(date_string)
print(f"The cardinal form of the date {date_string} is: {cardinal_form}")

# Example usage
number = 123
cardinal_form = number_to_cardinal(number)
print(f"The cardinal form of {number} is: {cardinal_form}")

