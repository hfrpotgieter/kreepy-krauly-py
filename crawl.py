from fake_useragent import UserAgent
import requests
import re
from bs4 import BeautifulSoup

def remove_duplicates(data):
    return list(set(data))

def get_email(html):
    email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    return set(re.findall(email_pattern, html))

def get_phone(html):
    phone_patterns = [
        r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,3}?\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        r"\d{2,3}[-.\s]?\d{3}[-.\s]?\d{4}",
        r"((?:\d{2,3}|\(\d{2,3}\))?(?:\s|-|\.)?\d{3,4}(?:\s|-|\.)?\d{4})",
        r"\d{4}[-.\s]?\d{3}[-.\s]?\d{3}",
        r"(\+\d{1,3}[- ]?)?\(?\d{1,4}?\)?[- ]?\d{1,4}[- ]?\d{1,4}[- ]?\d{1,4}",
    ]
    return set(num for pattern in phone_patterns for num in re.findall(pattern, html))


def find_contact_links(soup):
    return [a['href'] for a in soup.find_all('a', string=re.compile('contact', re.IGNORECASE)) if 'href' in a.attrs]

def extract_facebook_url(soup):
    fb_links = [a['href'] for a in soup.find_all('a', href=re.compile('facebook.com', re.IGNORECASE)) if 'href' in a.attrs]
    return fb_links[0] if fb_links else None

def fetch_site(url: str):
    try:
        headers = {
            "User-Agent": UserAgent().chrome,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        res = requests.get(url, headers=headers)
       
        res.raise_for_status()
        return res
    except requests.exceptions.RequestException as e:
        print(e)

def crawl_site(url: str):
    res = fetch_site(url)
    
    info = BeautifulSoup(res.text, 'lxml')
    company_name = info.title.string if info.title else "Not found (404)"

    contact_info = {
            'name': company_name,
            'link': res.url,
            'email': remove_duplicates(list(get_email(info.get_text()))),
            'phone': remove_duplicates(list(get_phone(info.get_text())))
    }

    return contact_info

    