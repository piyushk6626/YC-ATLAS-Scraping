import os
import json
import time
import pandas as pd
import asyncio
import argparse
import functools
from dotenv import load_dotenv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

# Import modules from ScrapingScripts
from ScrapingScripts.links import scrape_links
from ScrapingScripts.scrape import process_csv_to_json

# Import for AsyncWebCrawler
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

# For embeddings
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
def get_openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System and user prompts from summerizer/prompts.py
SYSTEM_PROMPT = """
You are a helpful assistant that generates a detailed yet simple summary of a given company's information. Your writing should be clear, engaging, and in the tone of Paul Graham—direct, insightful, and slightly conversational
"""

def tag_string_to_dict(tags):
    if isinstance(tags, float) or tags is None:
        return []
    tags = tags.split(";")
    try:
        tags = [tag.split(":")[1].strip() for tag in tags if ":" in tag]
        return tags
    except IndexError:
        return []

def generate_user_prompt(markdown, name, headline, batch, description, activity_status, 
                         website, founded_date, team_size, location, group_partner, tags):
    tags_formatted = tag_string_to_dict(tags)
    output = f"""
    Name of the Company is {name}
    mission of the {name} is {headline}
    The {name} initially started as {description} Website of the Company is {website}
    it was founded in {founded_date} and is part of Y Combinator Batch {batch}
    Located in {location} it has Team of {team_size} employees
    They have {group_partner} as their Group Partner
    it is tagged as {tags_formatted}
    The Company is currently Doing following things: {markdown}
    """
    return output

# Helper function to get file path for a company
def get_company_json_path(company, output_folder):
    """Generate the JSON file path for a company"""
    name = company.get('Name', 'Unknown')
    safe_name = "".join(c if c.isalnum() else "_" for c in str(name))
    batch = company.get('Batch', 'unknown')
    filename = f"{safe_name}_{batch}.json"
    return os.path.join(output_folder, filename)

# 1 & 2. Scraping YC page and getting company details
def scrape_yc_companies(batch_url, links_csv, details_json):
    """
    Scrapes YC companies from the given batch URL and saves details
    """
    print(f"Starting to scrape links from {batch_url}...")
    scrape_links(batch_url, links_csv)
    print(f"Links scraped and saved to {links_csv}")
    
    print("Processing links to get company details...")
    process_csv_to_json(links_csv, details_json)
    print(f"Company details scraped and saved to {details_json}")
    
    return details_json

# 3. Crawl company websites using crawl4ai
async def crawl_website(url):
    """Crawl a website and return its markdown content"""
    try:
        browser_config = BrowserConfig()
        run_config = CrawlerRunConfig()
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=run_config
            )
            return result.markdown.raw_markdown
    except Exception as e:
        print(f"Error crawling {url}: {e}")
        return None

async def crawl_all_websites(companies_data, output_folder, max_concurrent=10, skip_crawl=False):
    """Crawl all company websites in parallel, skip if already processed or if skipping crawl step"""
    if skip_crawl:
        print("Skipping website crawling as per configuration.")
        return companies_data

    semaphore = asyncio.Semaphore(max_concurrent)
    crawl_tasks = []
    
    async def crawl_with_semaphore(company):
        async with semaphore:
            # Check if company JSON already exists
            file_path = get_company_json_path(company, output_folder)
            if os.path.exists(file_path):
                print(f"Skipping {company.get('Name', 'Unknown')}: Already processed")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                    # Merge any new basic info but keep processed data
                    for key in company:
                        if key not in existing_data:
                            existing_data[key] = company[key]
                    return existing_data
                except Exception as e:
                    print(f"Error loading existing data for {company.get('Name', 'Unknown')}: {e}")
            
            website = company.get('Website')
            if website and isinstance(website, str) and website.strip():
                try:
                    markdown = await crawl_website(website)
                    if markdown:
                        company['markdown'] = markdown
                        company['crawl_status'] = True
                        print(f"Successfully crawled: {website}")
                    else:
                        company['markdown'] = None
                        company['crawl_status'] = False
                        print(f"Failed to crawl: {website}")
                except Exception as e:
                    company['markdown'] = None
                    company['crawl_status'] = False
                    print(f"Error crawling {website}: {e}")
            else:
                company['markdown'] = None
                company['crawl_status'] = False
                print(f"No valid website for company: {company.get('Name', 'Unknown')}")
            return company
    
    for company in companies_data:
        crawl_tasks.append(crawl_with_semaphore(company))
    
    return await asyncio.gather(*crawl_tasks)

# Generate embeddings for text
def generate_embedding(text):
    """Generate embedding for text using OpenAI API"""
    client = get_openai_client()
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-large"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

# 4. Generate summaries and embeddings, then save each company individually
def process_company(company, output_folder, skip_summary=False, skip_embedding=False):
    """Process a single company: optionally generate description, embedding, and save to JSON"""
    try:
        name = company.get('Name', 'Unknown')
        file_path = get_company_json_path(company, output_folder)
        
        # Check if already processed
        if os.path.exists(file_path):
            print(f"Skipping processing for {name}: Already exists")
            return company
        
        # If website was not crawled successfully and summary is desired, skip processing.
        if not skip_summary and not company.get('crawl_status', False):
            print(f"Skipping {name}: No crawl data available for summary generation")
            return company
        
        client = get_openai_client()
        
        # If summary is not desired, simply store the raw markdown (if available)
        if skip_summary:
            company['generated_description'] = company.get('markdown', '')
        else:
            # Extract required fields
            markdown = company.get('markdown', '')
            headline = company.get('Headline', '')
            batch = company.get('Batch', '')
            description = company.get('Description', '')
            activity_status = company.get('Activity_Status', '')
            website = company.get('Website', '')
            founded_date = company.get('Founded_Date', '')
            team_size = company.get('Team_Size', '')
            location = company.get('Location', '')
            group_partner = company.get('Group_Partner', '')
            tags = company.get('Tags', '')
            
            if not markdown:
                print(f"No markdown content for {name}, skipping summary generation")
                return company
            
            # Generate description using AI summary
            user_prompt = generate_user_prompt(
                markdown, name, headline, batch, description, activity_status,
                website, founded_date, team_size, location, group_partner, tags
            )
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # or another model of your choice
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            company['generated_description'] = response.choices[0].message.content
        
        # Generate embedding for the description if not skipped
        if not skip_embedding and company.get('generated_description'):
            company['embedding'] = generate_embedding(company['generated_description'])
            print(f"Generated embedding for {name}")
        else:
            company['embedding'] = None
        
        # Save as individual JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(company, f, ensure_ascii=False, indent=2)
        
        print(f"Saved processed data for {name}")
        return company
    except Exception as e:
        print(f"Error processing {company.get('Name', 'Unknown')}: {e}")
        return company

def process_all_companies(companies_data, output_folder, skip_summary=False, skip_embedding=False, num_processes=None):
    """Process all companies and save individual JSON files"""
    os.makedirs(output_folder, exist_ok=True)
    
    if num_processes is None:
        num_processes = max(1, int(cpu_count() * 0.75))
    
    process_func = functools.partial(
        process_company,
        output_folder=output_folder,
        skip_summary=skip_summary,
        skip_embedding=skip_embedding
    )
    
    with ThreadPoolExecutor(max_workers=num_processes) as executor:
        processed_companies = list(tqdm(
            executor.map(process_func, companies_data),
            total=len(companies_data),
            desc="Processing companies"
        ))
    
    return processed_companies

# Main pipeline function with extra configuration options
async def run_pipeline(batch_url, output_dir="data", skip_crawl=False, skip_summary=False, 
                       skip_embedding=False, output_format="json", max_concurrent=10):
    """Run the complete YC scraping and processing pipeline"""
    start_time = time.time()
    
    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    links_csv = os.path.join(output_dir, "yc_links.csv")
    details_json = os.path.join(output_dir, "yc_details.json")
    company_jsons_dir = os.path.join(output_dir, "company_descriptions")
    os.makedirs(company_jsons_dir, exist_ok=True)
    
    # Step 1 & 2: Scrape YC page for links and company details
    details_json = scrape_yc_companies(batch_url, links_csv, details_json)
    
    # Load company details
    with open(details_json, 'r', encoding='utf-8') as f:
        companies_data = json.load(f)
    
    print(f"Loaded details for {len(companies_data)} companies")
    
    # Step 3: Crawl company websites (unless skipping crawl)
    print("Crawling company websites...")
    companies_data = await crawl_all_websites(companies_data, company_jsons_dir, max_concurrent, skip_crawl)
    
    # Step 4: Process companies (generate summaries, embeddings, and save individual JSONs)
    print("Processing companies...")
    processed_companies = process_all_companies(companies_data, company_jsons_dir, skip_summary, skip_embedding)
    
    # Optionally, combine processed data into a CSV file if requested
    if output_format == "csv":
        combined_csv_path = os.path.join(output_dir, "companies_output.csv")
        df = pd.DataFrame(processed_companies)
        # For embeddings, convert list to string (if needed) so CSV cell is readable
        if 'embedding' in df.columns:
            df['embedding'] = df['embedding'].apply(lambda x: json.dumps(x) if x else None)
        df.to_csv(combined_csv_path, index=False)
        print(f"Combined CSV output saved to {combined_csv_path}")
    
    end_time = time.time()
    print(f"Complete pipeline executed in {end_time - start_time:.2f} seconds")
    
    processed_count = len([c for c in processed_companies if c.get('generated_description')])
    skipped_count = len(companies_data) - processed_count
    print(f"Processed {processed_count} companies, skipped {skipped_count} companies")

# Main entry point with additional options
def main():
    """Main entry point for running the YC scraper pipeline"""
    parser = argparse.ArgumentParser(description="YC Company Scraper Pipeline")
    parser.add_argument("--batch", type=str, default="X25", 
                        help="YC batch to scrape (e.g., W25, S24)")
    parser.add_argument("--output", type=str, default="data",
                        help="Output directory")
    parser.add_argument("--max-concurrent", type=int, default=10,
                        help="Maximum concurrent requests")
    parser.add_argument("--force-refresh", action="store_true",
                        help="Force refresh all companies, ignoring existing files")
    parser.add_argument("--skip-crawl", action="store_true",
                        help="Skip website crawling step")
    parser.add_argument("--skip-summary", action="store_true",
                        help="Skip AI summary generation step")
    parser.add_argument("--skip-embedding", action="store_true",
                        help="Skip embedding generation step")
    parser.add_argument("--output-format", type=str, choices=["json", "csv"], default="json",
                        help="Final output format (json or csv)")
    
    args = parser.parse_args()
    
    # If force-refresh is enabled, remove existing company JSON files
    company_jsons_dir = os.path.join(args.output, "company_descriptions")
    if args.force_refresh and os.path.exists(company_jsons_dir):
        for file in os.listdir(company_jsons_dir):
            os.remove(os.path.join(company_jsons_dir, file))
        print("Force refresh enabled: Existing company files removed.")
    
    # Construct batch URL
    batch_url = f"https://www.ycombinator.com/companies?batch={args.batch}"
    
    # Run the pipeline with the configured options
    asyncio.run(run_pipeline(
        batch_url,
        output_dir=args.output,
        skip_crawl=args.skip_crawl,
        skip_summary=args.skip_summary,
        skip_embedding=args.skip_embedding,
        output_format=args.output_format,
        max_concurrent=args.max_concurrent
    ))

if __name__ == "__main__":
    main()
