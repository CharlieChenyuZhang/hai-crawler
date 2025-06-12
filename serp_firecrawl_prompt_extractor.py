#!/usr/bin/env python3
"""
In this implementation, we use Serp API to search (1000 results) and to scrape the pages.
For 10 web pages, there are 211 results. So we 1000 pages would give us 21,100 results.


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
from datetime import datetime

import requests
from dotenv import load_dotenv
import csv
from serpapi import GoogleSearch
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

load_dotenv()

API_KEY = os.getenv("FIRECRAWL_API_KEY")
if not API_KEY:
    sys.stderr.write("[ERROR] FIRECRAWL_API_KEY not set. Export it or add to .env\n")
    sys.exit(1)

# QUERY = os.getenv("QUERY")
QUERIES = [
    # 🧘 Mindfulness & Well-being
    "mindfulness journaling prompts",
    "daily mindfulness questions",
    "journal prompts for presence and awareness",
    "introspective journaling prompts",
    "journaling prompts for grounding and calm",
    "self-care journal prompts",
    "mindful reflection prompts",
    # 💭 Emotional Awareness & Mental Health
    "emotional awareness journaling prompts",
    "journaling prompts for anxiety and stress",
    "trauma-informed journal prompts",
    "mental health journaling questions",
    "healing journal prompts",
    "gratitude journal prompts",
    "self-compassion journal prompts",
    # 🌱 Personal Growth & Self-Discovery
    "personal development journaling prompts",
    "journal prompts for self-discovery",
    "journaling prompts to get to know yourself",
    "identity and values journaling prompts",
    "deep reflection journal questions",
    "self-growth journal prompts",
    # 🎯 Goals, Habits & Productivity
    "journaling prompts for goal setting",
    "prompts for planning your day/week",
    "journaling prompts for productivity",
    "habit tracking journal prompts",
    "prompts to reflect on your achievements",
    # 📝 Creativity & Inspiration
    "creative writing journal prompts",
    "prompts for inspired journaling",
    "morning pages prompts",
    "journal prompts for artists and creatives",
]
# MAX_RESULTS = int(os.getenv("MAX_RESULTS", "25"))
# MAX_RESULTS = max(1, min(MAX_RESULTS, 100))  # hard Firecrawl cap
MAX_RESULTS = 200 # FIXME: hard code to 1000 results for now

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
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        sys.stderr.write("[ERROR] SERPAPI_API_KEY not set. Export it or add to .env\n")
        return []
    all_links = []
    for start in range(0, limit, 100):
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "start": start,
            "num": 100
        }
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            links = [res["link"] for res in results.get("organic_results", [])]
            if not links:
                break
            all_links.extend(links)
            if len(all_links) >= limit:
                break
        except Exception as e:
            sys.stderr.write(f"[ERROR] discover_urls failed at start={start}: {e}\n")
            break
    return all_links[:limit]

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
    sys.stderr.write(f"[INFO] Script started. Running {len(QUERIES)} queries. Max results per query: {MAX_RESULTS}\n")
    
    # Check if prompts.csv exists and load existing prompt/url pairs
    existing_pairs = set()
    visited_urls = set()
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
                        visited_urls.add(url)
        except Exception as e:
            sys.stderr.write(f"[WARN] Could not read existing prompts.csv: {e}\n")

    seen = set(existing_pairs)
    for query in QUERIES:
        sys.stderr.write(f"[INFO] Query: '{query}'\n")
        urls = discover_urls(query, MAX_RESULTS)
        sys.stderr.write(f"[INFO] Discovered {len(urls)} URLs for query '{query}'.\n")

        # Save discovered URLs to a text file with a timestamp and query
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = ''.join(c if c.isalnum() or c in (' ', '-') else '_' for c in query)[:50].replace(' ', '_')
        urls_file = f"discovered_urls_{safe_query}_{timestamp}.txt"
        try:
            with open(urls_file, "w", encoding="utf-8") as f:
                f.write(f"Query: {query}\n")
                for url in urls:
                    f.write(url + "\n")
            sys.stderr.write(f"[INFO] Saved discovered URLs to {urls_file}\n")
        except Exception as e:
            sys.stderr.write(f"[WARN] Could not write URLs to {urls_file}: {e}\n")

        new_rows = []
        # Parallelize URL processing
        with ThreadPoolExecutor(max_workers=8) as executor:  # 8 threads
            future_to_url = {
                executor.submit(scrape_prompts, url): (idx, url)
                for idx, url in enumerate(urls, 1)
                if url not in visited_urls
            }
            for future in as_completed(future_to_url):
                idx, url = future_to_url[future]
                sys.stderr.write(f"[INFO] ({idx}/{len(urls)}) Processing URL: {url}\n")
                try:
                    prompts = future.result()
                    sys.stderr.write(f"[INFO] Found {len(prompts)} prompts in {url}\n")
                    for prompt in prompts:
                        pair = (prompt, url)
                        if pair not in seen:
                            seen.add(pair)
                            new_rows.append({"prompt": prompt, "source url": url, "query": query})
                    sys.stderr.write(f"[INFO] Finished processing {url}\n")
                    # Write to prompts.csv after each URL
                    write_header = not os.path.exists(prompts_file)
                    with open(prompts_file, "a", encoding="utf-8", newline='') as f:
                        fieldnames = ["prompt", "source url", "query"]
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        if write_header:
                            writer.writeheader()
                        for row in new_rows:
                            writer.writerow(row)
                        new_rows.clear()
                    visited_urls.add(url)
                except requests.HTTPError as e:
                    sys.stderr.write(f"[WARN] {url} -> HTTP {e.response.status_code}\n")
                except Exception as e:
                    sys.stderr.write(f"[WARN] {url} -> {e}\n")

    sys.stderr.write(f"[INFO] Collected {len(seen)} unique prompt/url pairs.\n")
    sys.stderr.write("[INFO] Script finished.\n")

if __name__ == "__main__":
    main()
