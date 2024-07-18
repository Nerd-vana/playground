import requests
import uuid
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Your Azure subscription key and endpoint
subscription_key = os.getenv('AZURE_TRANSLATOR_KEY')
location = os.getenv('AZURE_TRANSLATOR_LOCATION')

endpoint = "https://api.cognitive.microsofttranslator.com"

path = '/translate'
constructed_url = endpoint + path

# list of language code can be found here
# https://learn.microsoft.com/en-us/azure/ai-services/translator/language-support

params = {
    'api-version': '3.0',
    'from': 'en',
    'to': ['es', 'zh-tw']  # You can specify multiple target languages
}

    #'to': ['zh-hk','zh-tw']  # You can specify multiple target languages

headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Ocp-Apim-Subscription-Region': location,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

# You can pass more than one object in body.
body = [{
    'text': "The Covid inquiry report makes it clear: Britain was completely and fatally unprepared"
}]

request = requests.post(constructed_url, params=params, headers=headers, json=body)
response = request.json()

print(response)