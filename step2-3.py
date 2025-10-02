
from argparse import ArgumentParser
import gzip
import hashlib
import json
import os
import random
import re
import socket
import sys
import time
import unicodedata
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict
from urllib.parse import urlparse, urlsplit
import requests
from bs4 import BeautifulSoup
import phonenumbers
import idna
#need to use socks 5h
TOR_BROWSER= "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
TOR_HOST = "127.0.0.1"
TOR_PORT = 9050 #for safety
#we need to seperate it here. Now what
TEST_URL="https://www.cnn.com/"
headers = {"User-Agent": TOR_BROWSER}
proxies = {
    "http": f"socks5h://{TOR_HOST}:{TOR_PORT}",
    "https": f"socks5h://{TOR_HOST}:{TOR_PORT}"
}
#we using command line prompts 
"""
def read_urls(path:str):
    urls=[]
    with open(path, "r", encoding= "utf-8") as f:
        url = line.strip()
        urls.append(url)
    return urls
"""
def parser(html:str):
    soup = BeautifulSoup(html, 'lxml')
    title=soup.title.string.strip() if soup.title and soup.title.string else ""
    for t in soup(['script', 'style', 'noscript']):
        t.extract()
    text=soup.get_text(" ", strip= True),soup
    #we need 
    return title, text

    






def main():

    """
    try: 
        r= requests.get(TEST_URL, proxies=proxies, timeout=10)
        r.raise_for_status()
        print ("Status", r.status_code)
        try:
            print("Tor proxy works!, your exit ip is:", r.json())
        except Exception:
            print ("Response\n:", r.text[:100])

    except Exception as e:
        print("Tor failed lol")
        sys.exit(1)
    """
    with open("urls.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]
    for idx,url in enumerate(urls,1):
        try:
            resp=requests.get(url, proxies=proxies, headers=headers, timeout=20)
            resp.raise_for_status()
            #print(f"[{idx}/{len(urls)}] {url} -> Status {resp.status_code}, Length {len(resp.text)}")
            title, text= parser(resp.text)
            print(f"[{idx}/{len(urls)}] {url}")
            print (f"Title:{title}")
            print(f"Visible text snippet: {text[:100]}...\n"
            )
        except Exception as e:
            print(f"[{idx}/{len(urls)}] {url} -> Error: {e}")

#step 3 now what should we do?


if __name__ == "__main__":
    main()