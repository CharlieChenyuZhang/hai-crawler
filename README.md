# llm-crawler

# what it does

The code extracts mindfullness journal prompts on the internet. It can be re-purposed to extract any contents just simply change the search queries in the file `serp_firecrawl_prompt_extractor.py`

# what's in discovered_urls

it saves the search results including a list of URLs returned by the search query.

# how does it work

It uses SerpAPI (Google Search) to find 200 results (you can chagne this number if you want) per search query and use FireCrawl to crawl each of the web link to extract the web contents. Here, we don't return the raw HTML, isntead, we use a prompt to extract the information that inerests us. (in this case, the journaling prompt)

# how to run the it

Set up the environment variables. In .env file

```
FIRECRAWL_API_KEY=<replac_it_with_your_own_key>
SERPAPI_API_KEY=<replac_it_with_your_own_key>
```

Then, run the following in your terminal.

`conda create -n web_crawl python=3.11`

`conda activate web_crawl`

`npm install -r requirements.txt`

`python serp_firecrawl_prompt_extractor.py`

# processing steps

[1] run `python serp_firecrawl_prompt_extractor.py` to get the `prompts.csv` with the prmopts

[2] run `python extract_meta_data.py` to get `enriched_prompts.csv` with metadata (e.g. name of the author)

[3] run `python quality_check.py` to get `filtered_prompts.csv` and `inferior_list.csv` (this is the list of prompts that did not pass the quality check)
