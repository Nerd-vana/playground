import requests
from bs4 import BeautifulSoup

# pip install requests beautifulsoup4 lxml

# URL of the web page
url = 'https://www.theguardian.com/football/article/2024/jul/18/hugo-lloris-enzo-fernandez-video-france-argentina-minister-sacked-julio-garro'  # Replace with the actual URL

# Fetch the content of the URL
response = requests.get(url)
html_content = response.content

# Parse the HTML
soup = BeautifulSoup(html_content, 'lxml')

# Find the div with data-gu-name="headline" and get its text
headline_div = soup.find('div', {'data-gu-name': 'headline'})
headline_text = headline_div.get_text(strip=True) if headline_div else None
print(headline_text)

standfirst_div = soup.find('div', {'data-gu-name': 'standfirst'})
standfirst_text = standfirst_div.get_text(strip=True) if standfirst_div else None
print(standfirst_text)
