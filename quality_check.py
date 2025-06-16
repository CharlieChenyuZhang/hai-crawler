import csv
import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Load environment variables from .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment. Please add it to your .env file.")

# System prompt for GPT-4o
SYSTEM_PROMPT = (
    "A journal prompt is a question, statement, or idea designed to inspire reflection and guide someone in writing about their thoughts, feelings, experiences, or observations. "
    "It serves as a starting point for journaling, helping individuals explore personal insights, clarify emotions, or develop creativity.\n"
    "The criteria is that it should be a complete journaling prompt, it shouldn't be a theme or topic.\n"
    "Your task is to help me check if the following is a journaling prompt, answer yes or no only."
)

# Input and output files
INPUT_CSV = "enriched_prompts.csv"
OUTPUT_CSV = "filtered_enriched_prompts.csv"
INFERIOR_CSV = "inferior_list.csv"

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Locks for thread-safe file writing
filtered_lock = threading.Lock()
inferior_lock = threading.Lock()

def is_journaling_prompt(prompt_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=3,
            temperature=0
        )
        answer = response.choices[0].message.content.strip().lower()
        return answer.startswith("yes")
    except Exception as e:
        print(f"Error with OpenAI API: {e}. Retrying in 10 seconds...")
        time.sleep(10)
        return is_journaling_prompt(prompt_text)

def process_row(row, filtered_writer, inferior_writer):
    prompt = row['prompt']
    print(f"Checking: {prompt[:60]}...")
    if is_journaling_prompt(prompt):
        with filtered_lock:
            filtered_writer.writerow(row)
    else:
        with inferior_lock:
            inferior_writer.writerow(row)
    time.sleep(1.2)  # To avoid hitting rate limits

def main():
    with open(INPUT_CSV, newline='', encoding='utf-8') as infile, \
         open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as filteredfile, \
         open(INFERIOR_CSV, 'w', newline='', encoding='utf-8') as inferiorfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        filtered_writer = csv.DictWriter(filteredfile, fieldnames=fieldnames)
        inferior_writer = csv.DictWriter(inferiorfile, fieldnames=fieldnames)
        filtered_writer.writeheader()
        inferior_writer.writeheader()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for row in reader:
                # Submit each row to the thread pool
                futures.append(executor.submit(process_row, row, filtered_writer, inferior_writer))
            # Wait for all to complete
            for future in as_completed(futures):
                future.result()  # To raise exceptions if any

if __name__ == "__main__":
    main()

# Instructions:
# 1. Add your OpenAI API key to your .env file as OPENAI_API_KEY=sk-...
# 2. Run: pip install -r requirements.txt
# 3. Run: python quality_check.py
# Results will be in filtered_prompts.csv and inferior_list.csv 