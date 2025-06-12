import requests
import os
from dotenv import load_dotenv
import json
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

load_dotenv()

API_KEY = os.getenv("FIRECRAWL_API_KEY")

BASE = "https://api.firecrawl.dev/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def scrape_metadata(url: str) -> dict:
    try:
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
    except (requests.RequestException, json.JSONDecodeError, Exception) as e:
        print(f"[ERROR] Failed to scrape {url}: {e}")
        return {
            "published_time": "n/a",
            "modified_time": "n/a",
            "author": "n/a"
        }

def parallel_scrape(urls: List[str], cache: Dict[str, dict], max_workers: int = 8) -> Dict[str, dict]:
    """Scrape metadata for a list of URLs in parallel, updating the cache."""
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(scrape_metadata, url): url
            for url in urls if url not in cache
        }
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            meta = future.result()
            print(f"[INFO] Scraped metadata for {url}: {meta}")
            results[url] = meta
    return results

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

    # Read all rows and collect unique URLs
    with open(input_csv, "r", encoding="utf-8", newline='') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        unique_urls = set(row.get("source url", "").strip() for row in rows if row.get("source url", "").strip())
    print(f"[INFO] Found {len(unique_urls)} unique URLs to process.")

    # Scrape uncached URLs in parallel
    uncached_urls = [url for url in unique_urls if url not in cache]
    if uncached_urls:
        print(f"[INFO] Scraping {len(uncached_urls)} uncached URLs in parallel...")
        new_results = parallel_scrape(uncached_urls, cache)
        cache.update(new_results)
    else:
        print(f"[INFO] All URLs already cached.")

    # Write output CSV
    with open(output_csv, "w", encoding="utf-8", newline='') as outfile:
        original_fieldnames = rows[0].keys() if rows else []
        fieldnames = list(original_fieldnames) + [fn for fn in ["published_time", "modified_time", "author"] if fn not in original_fieldnames]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for idx, row in enumerate(rows, 1):
            url = row.get("source url", "").strip()
            meta = cache.get(url, {"published_time": "n/a", "modified_time": "n/a", "author": "n/a"})
            row["published_time"] = meta.get("published_time", "n/a")
            row["modified_time"] = meta.get("modified_time", "n/a")
            row["author"] = meta.get("author", "n/a")
            writer.writerow(row)
            print(f"[INFO] Wrote row {idx}/{len(rows)} to output.")
    # Save cache
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Finished processing. Output written to {output_csv}. Cache updated in {cache_file}.")

if __name__ == "__main__":
    # process_prompts_csv("prompts.csv", "enriched_prompts.csv")
    process_prompts_csv("subset.csv", "enriched_prompts.csv")