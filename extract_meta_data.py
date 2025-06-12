import requests
import os

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
url_to_scrape = "https://example.com"

headers = {
    "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "url": url_to_scrape,
    "prompt": "Extract all metadata from the website including meta tags, Open Graph, Twitter cards, JSON-LD, and publication date if available.",
    "mode": "json"
}

res = requests.post("https://api.firecrawl.dev/v1/scrape", headers=headers, json=payload)
print(res.json())
