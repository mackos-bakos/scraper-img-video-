import os
import requests
from bs4 import BeautifulSoup
import random

url = "https://example.com"
#specify the website you want to traverse

def traverse_URL(URL):
    #download the HTML content of the website
    R = requests.get(URL)
    HTML_CONTENT = R.text

    #parse the HTML content
    SOUP = BeautifulSoup(HTML_CONTENT, 'html.parser')

    #find all the video tags
    VIDEOS = SOUP.find_all('video')

    #iterate over the video tags
    for i,VIDEO in enumerate(VIDEOS):
        #get the source of the video
        SOURCE = VIDEO.find('source')['src']
        #split the source in order to get the video name
        NAME = SOURCE.split('/')[-1]
        NAME = NAME[:-4] + ''.join(chr(random.randint(128, 512)) for _ in range(3)) + ".mp4"
        #download the video
        R = requests.get(SOURCE, stream=True)
        with open(NAME, 'wb') as F:
            for CHUNK in R.iter_content(chunk_size=1024):
                if CHUNK:
                    F.write(CHUNK)
            F.close()
        print(f"downloaded video {i} out of {len(VIDEOS)}")

traverse_url(url)
print("operation completed")
