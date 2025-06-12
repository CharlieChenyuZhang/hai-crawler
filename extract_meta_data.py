import requests
import os
from dotenv import load_dotenv
import json
import csv

from typing import List

load_dotenv()

API_KEY = os.getenv("FIRECRAWL_API_KEY")

BASE = "https://api.firecrawl.dev/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def scrape_prompts(url: str) -> dict:
    payload = {
        "url": url,
        "formats": ["json"],
        "jsonOptions": {
            "prompt": (
                "Extract the published time, modified time, author from the website."
            )
        },
    }
    resp = requests.post(f"{BASE}/scrape", headers=HEADERS, json=payload, timeout=120)
    resp.raise_for_status()
    page = resp.json().get("data", {})
    json_data = page.get("json", {})
    published_time = json_data.get("publishedTime") or "n/a"
    modified_time = json_data.get("modifiedTime") or "n/a"
    author = json_data.get("author") or "n/a"
    return {
        "published_time": published_time,
        "modified_time": modified_time,
        "author": author,
    }

def process_prompts_csv(input_csv: str, output_csv: str, cache_file: str = "scrape_cache.json"):
    print(f"[INFO] Starting processing: {input_csv} -> {output_csv}")
    # Load cache if exists
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            cache = json.load(f)
        print(f"[INFO] Loaded cache with {len(cache)} entries from {cache_file}")
    else:
        cache = {}
        print(f"[INFO] No cache found, starting fresh.")

    # Prepare to write output
    with open(input_csv, "r", encoding="utf-8", newline='') as infile, \
         open(output_csv, "w", encoding="utf-8", newline='') as outfile:
        reader = csv.DictReader(infile)
        # Keep all original columns and add the new ones
        original_fieldnames = reader.fieldnames if reader.fieldnames else []
        fieldnames = original_fieldnames + [fn for fn in ["published_time", "modified_time", "author"] if fn not in original_fieldnames]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        total = 0
        for row in reader:
            total += 1
        infile.seek(0)
        next(reader)  # skip header
        processed = 0
        for row in reader:
            processed += 1
            url = row.get("source url", "").strip()
            print(f"[INFO] Processing row {processed}/{total}: {url}")
            if not url:
                print(f"[WARN] Row {processed} missing source url, skipping.")
                continue
            if url in cache:
                meta = cache[url]
                print(f"[INFO] Using cached metadata for {url}")
            else:
                print(f"[INFO] Calling scrape_prompts for {url}")
                try:
                    meta = scrape_prompts(url)
                    print(f"[INFO] Scraped metadata for {url}: {meta}")
                except Exception as e:
                    meta = {"published_time": "n/a", "modified_time": "n/a", "author": f"error: {e}"}
                    print(f"[ERROR] Failed to scrape {url}: {e}")
                cache[url] = meta
            # Add the new fields to the row
            row["published_time"] = meta.get("published_time", "n/a")
            row["modified_time"] = meta.get("modified_time", "n/a")
            row["author"] = meta.get("author", "n/a")
            writer.writerow(row)
            print(f"[INFO] Wrote row {processed}/{total} to output.")
    # Save cache
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Finished processing. Output written to {output_csv}. Cache updated in {cache_file}.")

if __name__ == "__main__":
    process_prompts_csv("prompts.csv", "output.csv")