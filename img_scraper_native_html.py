#import necessary libraries
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import random

#specify the url
url = 'https://example.com'
def traverse_URL(URL):
    #download the HTML content of the website
    R = requests.get(URL)
    HTML_CONTENT = R.text

    #parse the HTML content
    SOUP = BeautifulSoup(HTML_CONTENT, 'html.parser')

    #find all the img tags
    IMAGES = SOUP.find_all('img')

    #iterate over the img tags
    for IMG in IMAGES:
        #print(IMG)
        #get the source of the img
        SOURCE = IMG.get("src")
        if not SOURCE:
            continue
        NAME = SOURCE.split('/')[-1]
        print(f"downloading {SOURCE} in {URL}:")
        NAME = NAME[:-4] + ''.join(chr(random.randint(128, 512)) for _ in range(3)) + NAME[-4:]
        try:
            R = requests.get(SOURCE, stream=True)
            with open(NAME, 'wb') as F:
                for CHUNK in R.iter_content(chunk_size=1024):
                    if CHUNK:
                        F.write(CHUNK)
                F.close()
        except:
            continue

def find_traversable(URL):
    #download the HTML content of the website
    R = requests.get(URL)
    HTML_CONTENT = R.text

    #parse the HTML content
    SOUP = BeautifulSoup(HTML_CONTENT, 'html.parser')

    #find all the img tags
    LINKS = SOUP.find_all('a')
    Links = []
    for LINK in LINKS:
        #get the source of the img
        SOURCE = LINK.get("href")
        if not SOURCE:
            continue
        Links.append(SOURCE)
    return Links


traverse_URL(url)
