
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
from phonenumbers import PhoneNumberMatcher, PhoneNumberFormat
import idna
#need to use socks 5h
TOR_BROWSER= "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
TOR_HOST = "127.0.0.1"
TOR_PORT = 9050 #for safety
#we need to seperate it here. Now what
TEST_URL="https://www.cnn.com/"
DEFAULT_PHONE_REGION = "US"

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
    text=soup.get_text(" ", strip= True)
    #we need 
    return title, text, soup
    

def load_rules(path:str):
    with open(path, "r", encoding="utf-8") as f:
        data=json.load(f).get("page_filter", {})

    all_of = [s.casefold() for s in data.get("all_of", [])]
    any_of = [s.casefold() for s in data.get("any_of", [])]
    none_of = [s.casefold() for s in data.get("none_of", [])]
    regexes = [re.compile(s, re.IGNORECASE) for s in data.get("regexes", [])]

    return all_of,any_of,none_of, regexes
def match_page(title:str, text:str, all_of,any_of,none_of, regexes):
    total=(title+ " "+ text).casefold()
    #we need to cehck if it already exists or not so that means we have to do all of if not of 
    if all_of and not all(a in total for a in all_of):
        return False
    if none_of and not any(a in total for a in none_of):
        return False
    if any_of and not any(a in total for a in any_of):
        return False
    for r in regexes:
        if not (r.search(title) or r.search(text)):
            return False
    return True

email_regex=re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
#username_regex=re.compile()
username_regex=re.compile(r'@(\w[\w._-]{2,20})"')

def extract_emails(text:str, soup: BeautifulSoup)-> List[str]:
    found_emails=set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))
    for a in soup.select('a[href^="mailto:"]'):
        found_emails.add(a.get('href', '').replace('mailto:', ''))
    return sorted(list(found_emails))
                
def extract_usernames(text:str, soup: BeautifulSoup)-> List[str]:
    found_usernames=set(re.findall(r"@(\w[\w._-]{2,20})", text))
    return sorted(list(found_usernames))

def extract_phone_numbers(text: str, soup):
    found_numbers = set()
    for a in soup.select('a[href^="tel:"]'):
        raw = a.get('href', '')[4:]
        try:
            num = phonenumbers.parse(raw, DEFAULT_PHONE_REGION)
            if phonenumbers.is_possible_number(num) and phonenumbers.is_valid_number(num):
                found_numbers.add(phonenumbers.format_number(num, PhoneNumberFormat.E164))
        except Exception:
            continue
    for match in phonenumbers.PhoneNumberMatcher(text, DEFAULT_PHONE_REGION):
        num = match.number
        if phonenumbers.is_possible_number(num) and phonenumbers.is_valid_number(num):
            found_numbers.add(phonenumbers.format_number(num, PhoneNumberFormat.E164))
    return sorted(found_numbers)

def print_findings(url: str, title: str, emails: list, phones: list, usernames: list):
    print(f"📄 Results for: {url}")
    print(f"   Title: {title}")
    print("-" * 30 + "\n")
    if emails:
         print(f" Emails: {', '.join(emails)}")
    if usernames:
         print(f" useernames: {', '.join(emails)}")
    if phones:
         print(f" Phones: {', '.join(phones)}")
    print("-" * 30 + "\n")


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
    all_of, any_of, none_of, regexes = load_rules("rules.json")
    results = []

    for idx,url in enumerate(urls,1):
        try:
            resp=requests.get(url, proxies=proxies, headers=headers, timeout=20)
            resp.raise_for_status()
            #print(f"[{idx}/{len(urls)}] {url} -> Status {resp.status_code}, Length {len(resp.text)}")
            title, text, soup = parser(resp.text)
            text = text.replace("[at]", "@").replace("[dot]", ".")

            if not match_page(title, text, all_of,any_of,none_of, regexes):
                print(f"[{idx}/{len(urls)}] {url} -> Skipped (did not match filter)")
                continue
    
            emails=extract_emails(text, soup)
            usernames=extract_usernames(text, soup)
            phones=extract_phone_numbers(text, soup)
            #print_findings(url, title, emails, phones, usernames)
            result ={
                "url": url,
                "emails": emails,
                "usernames": usernames,
                "phone_numbers": phones

            }
            results.append(result)
            print(json.dumps(result,indent=2))
            print(f"[{idx}/{len(urls)}] {url}")
            print (f"Title:{title}")
            print(f"Visible text snippet: {text[:100]}...\n")
        except Exception as e:
            print(f"[{idx}/{len(urls)}] {url} -> Error: {e}")

#step 3 now what should we do?


if __name__ == "__main__":
    main()