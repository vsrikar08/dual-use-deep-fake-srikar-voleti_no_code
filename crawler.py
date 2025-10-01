import argparse
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
TOR_BROWSER_UA= "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
TOR_HOST = "127.0.0.1"
TOR_PORT = 9050 #for safety
#we need to seperate it here. Now what
TEST_URL="https://www.cnn.com/"
proxies = {
   "http": f"socks5h://{TOR_HOST}:{TOR_PORT}",
   "https" : f"socks5h://{TOR_HOST}:{TOR_PORT}"
}
headers={"User-Agent": TOR_BROWSER_UA}
def main():
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

if __name__ == "__main__":
    main()