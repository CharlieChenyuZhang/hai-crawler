import csv
import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import logging
import argparse

# Load environment variables from .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment. Please add it to your .env file.")

# Initialize OpenAI client (must be done inside each process)
def get_openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt for date normalization
date_system_prompt = (
    "You are a helpful assistant. Convert the following date to ISO format (YYYY-MM-DD). "
    "If the date is already in ISO format, return it as is. If the date is missing or invalid, return 'n/a'. "
    "Only return the date, nothing else."
)

def normalize_date_with_openai(date_str):
    logger = logging.getLogger("normalize_date_with_openai")
    logger.debug(f"Normalizing date: {date_str}")
    client = get_openai_client()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": date_system_prompt},
                {"role": "user", "content": date_str}
            ],
            max_tokens=12,
            temperature=0
        )
        answer = response.choices[0].message.content.strip()
        logger.debug(f"Normalized '{date_str}' to '{answer}'")
        return answer
    except Exception as e:
        logger.error(f"Error with OpenAI API: {e}. Retrying in 10 seconds...")
        time.sleep(10)
        return normalize_date_with_openai(date_str)

def process_row(row):
    logger = logging.getLogger("process_row")
    row = row.copy()
    logger.info(f"Processing row: prompt='{row.get('prompt', '')[:40]}...' published_time='{row.get('published_time', '')}' modified_time='{row.get('modified_time', '')}'")
    row['published_time'] = normalize_date_with_openai(row['published_time'])
    row['modified_time'] = normalize_date_with_openai(row['modified_time'])
    return row

def process_chunk(rows, fieldnames, chunk_idx):
    logger = logging.getLogger("process_chunk")
    logger.info(f"Starting processing chunk {chunk_idx} with {len(rows)} rows...")
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        results = list(executor.map(process_row, rows))
    logger.info(f"Finished processing chunk {chunk_idx}.")
    return results

def main():
    parser = argparse.ArgumentParser(description="Normalize dates in CSV using OpenAI API.")
    parser.add_argument('--log-level', default='INFO', help='Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), None), format='%(asctime)s %(levelname)s %(name)s: %(message)s')

    INPUT_CSV = "filtered_enriched_prompts.csv"
    OUTPUT_CSV = "filtered_enriched_prompts_iso.csv"
    CHUNK_SIZE = 1000

    logger = logging.getLogger("main")
    logger.info(f"Reading from {INPUT_CSV}, writing to {OUTPUT_CSV}, chunk size {CHUNK_SIZE}")

    with open(INPUT_CSV, newline='', encoding='utf-8') as infile, \
         open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        chunk = []
        chunk_idx = 1
        for row in reader:
            chunk.append(row)
            if len(chunk) >= CHUNK_SIZE:
                processed = process_chunk(chunk, fieldnames, chunk_idx)
                writer.writerows(processed)
                chunk = []
                chunk_idx += 1
        # Process any remaining rows
        if chunk:
            processed = process_chunk(chunk, fieldnames, chunk_idx)
            writer.writerows(processed)
    logger.info("All done!")

if __name__ == "__main__":
    main() 