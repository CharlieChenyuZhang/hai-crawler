# llm-crawler

# what it does

The code extracts mindfullness journal prompts on the internet. It can be re-purposed to extract any contents just simply change the search queries in the file `serp_firecrawl_prompt_extractor.py`

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
