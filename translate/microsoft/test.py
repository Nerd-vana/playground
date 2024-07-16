import requests
import uuid
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Your Azure subscription key and endpoint
subscription_key = os.getenv('AZURE_TRANSLATOR_KEY')
endpoint = "https://api.cognitive.microsofttranslator.com"

# Location, also known as region.
# Required if you're using a multi-service or regional (not global) resource.
location = os.getenv('AZURE_TRANSLATOR_LOCATION')

path = '/translate'
constructed_url = endpoint + path

params = {
    'api-version': '3.0',
    'from': 'en',
    'to': ['es', 'fr']  # You can specify multiple target languages
}

headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Ocp-Apim-Subscription-Region': location,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

# You can pass more than one object in body.
body = [{
    'text': 'Hello, world!'
}]

request = requests.post(constructed_url, params=params, headers=headers, json=body)
response = request.json()

print(response)