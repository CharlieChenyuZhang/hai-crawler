#!/usr/bin/env python3
"""
In this implementation, we use Firecrawl API to search and to scrape the pages.
However, firecrawl API search only returns the 100 results and does not currently support pagination.
For 10 web pages, there are 211 results. So we would need 1000 pages to get a good number of results.


firecrawl_prompt_extractor.py (v2025‑06‑11)
=========================================
A **zero‑dependency** script (just `requests` + optional `python‑dotenv`) that

1. **Discovers** pages with Firecrawl **/search**
2. **Scrapes & extracts** journaling prompts from each page via **/scrape**
   using Firecrawl's *prompt‑only JSON extraction* (no schema needed)
3. Prints a **JSON array** of unique prompts to **STDOUT**

Quick start
-----------
```bash
pip install requests python-dotenv  # if you haven't already

# put your key in .env or export directly
export FIRECRAWL_API_KEY="fc‑..."
python firecrawl_prompt_extractor.py  >  prompts.json
```
Environment variables
---------------------
| Var | Default | Purpose |
|-----|---------|---------|
| `FIRECRAWL_API_KEY` | *none* | Your Firecrawl key (required) |
| `QUERY` | "mindfulness journaling prompts" | Search term |
| `MAX_RESULTS` | `25` | 1‑100 results to fetch |

Firecrawl credits   🔎  + 🧹
------------------------------
* `/search` costs **1 credit per result** returned
* `/scrape` costs **1 credit per URL** (covers the integrated LLM call)

"""

from __future__ import annotations

import json
import os
import sys
from typing import List

import requests
from dotenv import load_dotenv
import csv

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

load_dotenv()

API_KEY = os.getenv("FIRECRAWL_API_KEY")
if not API_KEY:
    sys.stderr.write("[ERROR] FIRECRAWL_API_KEY not set. Export it or add to .env\n")
    sys.exit(1)

QUERY = os.getenv("QUERY", "mindfulness journaling prompts")
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "25"))
MAX_RESULTS = max(1, min(MAX_RESULTS, 100))  # hard Firecrawl cap

BASE = "https://api.firecrawl.dev/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# ---------------------------------------------------------------------------
# 1) Discover candidate URLs
# ---------------------------------------------------------------------------

def discover_urls(query: str, limit: int) -> List[str]:
    try:
        payload = {"query": query, "limit": limit}
        resp = requests.post(f"{BASE}/search", headers=HEADERS, json=payload, timeout=60)
        resp.raise_for_status()
        return [item["url"] for item in resp.json().get("data", [])]
    except Exception as e:
        sys.stderr.write(f"[ERROR] discover_urls failed: {e}\n")
        return []

# ---------------------------------------------------------------------------
# 2) Scrape each URL & extract prompts via LLM
# ---------------------------------------------------------------------------

def scrape_prompts(url: str) -> List[str]:
    payload = {
        "url": url,
        "formats": ["json"],
        "jsonOptions": {
            "prompt": (
                "Extract every mindfulness or journaling prompt from the page. "
                "Return them as an array called 'prompts'. Do **not** invent prompts."
            )
        },
    }
    resp = requests.post(f"{BASE}/scrape", headers=HEADERS, json=payload, timeout=120)
    resp.raise_for_status()
    page = resp.json().get("data", {})
    prompts = page.get("json", {}).get("prompts", [])
    return [p.strip() for p in prompts if isinstance(p, str) and p.strip()]

# ---------------------------------------------------------------------------
# 3) Orchestrate & output
# ---------------------------------------------------------------------------

def main() -> None:
    sys.stderr.write(f"[INFO] Script started. Query: '{QUERY}', Max results: {MAX_RESULTS}\n")
    urls = discover_urls(QUERY, MAX_RESULTS)
    sys.stderr.write(f"[INFO] Discovered {len(urls)} URLs for query '{QUERY}'.\n")

    # Check if prompts.csv exists and load existing prompt/url pairs
    existing_pairs = set()
    prompts_file = "prompts.csv"
    if os.path.exists(prompts_file):
        try:
            with open(prompts_file, "r", encoding="utf-8", newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    prompt = row.get("prompt", "").strip()
                    url = row.get("source url", "").strip()
                    if prompt and url:
                        existing_pairs.add((prompt, url))
        except Exception as e:
            sys.stderr.write(f"[WARN] Could not read existing prompts.csv: {e}\n")

    seen = set(existing_pairs)
    new_rows = []
    for idx, url in enumerate(urls, 1):
        sys.stderr.write(f"[INFO] ({idx}/{len(urls)}) Processing URL: {url}\n")
        try:
            prompts = scrape_prompts(url)
            sys.stderr.write(f"[INFO] Found {len(prompts)} prompts in {url}\n")
            for prompt in prompts:
                pair = (prompt, url)
                if pair not in seen:
                    seen.add(pair)
                    new_rows.append({"prompt": prompt, "source url": url})
            sys.stderr.write(f"[INFO] Finished processing {url}\n")
            # Write to prompts.csv after each URL
            write_header = not os.path.exists(prompts_file)
            with open(prompts_file, "a", encoding="utf-8", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["prompt", "source url"])
                if write_header:
                    writer.writeheader()
                for row in new_rows:
                    writer.writerow(row)
                new_rows.clear()
        except requests.HTTPError as e:
            sys.stderr.write(f"[WARN] {url} -> HTTP {e.response.status_code}\n")
        except Exception as e:
            sys.stderr.write(f"[WARN] {url} -> {e}\n")

    sys.stderr.write(f"[INFO] Collected {len(seen)} unique prompt/url pairs.\n")
    sys.stderr.write("[INFO] Script finished.\n")

if __name__ == "__main__":
    main()
