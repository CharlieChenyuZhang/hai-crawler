import csv

# Path to the CSV file
csv_file = 'prompts.csv'

unique_urls = set()
unique_query = set()
list_3_things_count = 0

with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        url = row['source url'].strip()
        query = row['query'].strip()
        prompt = row['prompt'].strip()
        if url:
            unique_urls.add(url)
        if query:
            unique_query.add(query)
        if prompt:
            if prompt.startswith("List 3 things"):
                list_3_things_count += 1

print(f"Number of unique URLs: {len(unique_urls)}") 
print(f"Number of unique prompts: {len(unique_query)}") 
print(f"Number of prompts starting with 'List 3 things': {list_3_things_count}") 