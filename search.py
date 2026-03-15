from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, parse_qs, unquote

def google_search(query: str):
    """
    NOTE: Google SERP HTML is frequently blocked (consent/captcha/unusual traffic),
    which makes "no-key" scraping unreliable.

    This function keeps the same interface but now uses DuckDuckGo's HTML endpoint
    to provide titles/links without any API key, instead of scraping Google.
    """
    headers = {
        "User-Agent": UserAgent().chrome,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    def _request(url: str, params: dict):
        last_resp = None
        for delay in (0, 1.0, 2.0):
            if delay:
                time.sleep(delay)
            try:
                last_resp = requests.get(url, params=params, headers=headers, timeout=12)
            except requests.RequestException as e:
                return None, str(e)
            if last_resp.status_code not in (202, 429):
                break
        return last_resp, None

    resp, err = _request("https://duckduckgo.com/html/", {"q": query})
    if err:
        print(f"[search] request exception for query '{query}': {err}")
        return [{"title": "Search request failed", "link": err}]

    if resp is not None and resp.status_code in (202, 429):
        resp, err = _request("https://lite.duckduckgo.com/lite/", {"q": query})
        if err:
            print(f"[search] lite request exception for query '{query}': {err}")
            return [{"title": "Search request failed", "link": err}]

    if resp is None or resp.status_code != 200:
        status = getattr(resp, "status_code", "no_response")
        print(f"[search] non-200 status {status} for query '{query}'")
        snippet = (getattr(resp, "text", "") or "")[:200]
        return [{"title": f"Search error {status}", "link": snippet}]

    soup = BeautifulSoup(resp.text, "lxml")

    links = soup.select("a.result__a")
    lite_mode = False
    if not links:
        links = soup.select("a.result-link")
        lite_mode = True

    results = []
    for a in links:
        title = (a.get_text() or "").strip()
        href = a.get("href")
        if not title or not href:
            continue

        link = href
        if "/l/?" in href or href.startswith("//duckduckgo.com/l/?"):

            if href.startswith("//"):
                href = "https:" + href
            parsed = urlparse(href)
            qs = parse_qs(parsed.query)
            target = qs.get("uddg", [None])[0]
            if target:
                link = unquote(target)
            else:
                continue
        elif lite_mode and href.startswith("//"):
            link = "https:" + href

        if not (link.startswith("http://") or link.startswith("https://")):
            continue

        results.append({"title": title, "link": link})

    print(f"[search] query '{query}' -> {len(results)} result links parsed")

    if not results:
        return [{
            "title": "No results",
            "link": "The search provider returned no parsable results for this query.",
        }]

    return results
