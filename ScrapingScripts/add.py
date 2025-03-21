import pandas as pd
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

# Provided async crawl function
async def crawl_website(url):
    browser_config = BrowserConfig()  # Default browser configuration
    run_config = CrawlerRunConfig()     # Default crawl run configuration
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=url,
            config=run_config
        )
        return result.markdown.raw_markdown

async def process_dataframe(df, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = []
    indices = []

    async def sem_task(idx, url):
        async with semaphore:
            return idx, await crawl_website(url)
    
    # Loop over the DataFrame rows
    for idx, row in df.iterrows():
        print(row.get('Name', ''))
        if not row['status'] and str(row.get('Activity_Status', '')).strip().lower() == "active":
            if str(row.get('Batch', '')).strip() != "W25" and str(row.get('Batch', '')).strip() != "F24" and str(row.get('Batch', '')).strip() != "W24" and str(row.get('Batch', '')).strip() != "S24":
                website = row.get('Website', '')
                url = None
                
                if pd.notnull(website) and str(website).strip():
                    url = str(website).strip()

                if url:
                    tasks.append(sem_task(idx, url))
                else:
                    print(f"No valid URL found for row index {idx}.")

    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Update DataFrame with results.
    for res in results:
        idx, result = res if not isinstance(res, Exception) else (None, res)
        if idx is None:
            print(f"Error processing a task: {result}")
        else:
            df.at[idx, 'markdown'] = result
            df.at[idx, 'status'] = True
            print(f"Processed row {idx} successfully.")

    return df

def main():
    print(asyncio.run(crawl_website("https://www.leeroo.com/")))
if __name__ == "__main__":
    main()
