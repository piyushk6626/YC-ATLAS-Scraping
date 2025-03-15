# YC Company Scraper Pipeline

## Overview
This project is a complete pipeline for scraping, crawling, summarizing, and embedding YC startup data. The pipeline:

1. **Scrapes Y Combinator (YC) company data** from the official YC website.
2. **Crawls company websites** using `crawl4ai` to extract textual content.
3. **Generates AI-powered summaries** using OpenAI's GPT models.
4. **Creates text embeddings** for semantic search and analysis.
5. **Saves data** as individual JSON files and optionally as a CSV.

## Features
- **Multi-step scraping process**: Extracts YC company links, details, and website content.
- **Asynchronous crawling**: Uses `crawl4ai` for efficient and scalable web crawling.
- **AI-generated summaries**: Provides clear and concise company overviews.
- **OpenAI embeddings**: Enables advanced search and analysis capabilities.
- **Parallel processing**: Uses `ThreadPoolExecutor` for efficient batch processing.
- **Configurable execution**: Options to skip crawling, summarization, or embeddings.

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- `pip` for package management
- An OpenAI API key (stored in `.env` file as `OPENAI_API_KEY`)

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage
### Running the Full Pipeline
```bash
python main.py --batch W25 --output data
```

### Command-Line Arguments
| Argument             | Description |
|----------------------|-------------|
| `--batch`           | YC batch (e.g., W25, S24) |
| `--output`          | Output directory (default: `data/`) |
| `--max-concurrent`  | Max concurrent requests for crawling (default: 10) |
| `--force-refresh`   | Ignore existing files and refresh all data |
| `--skip-crawl`      | Skip website crawling step |
| `--skip-summary`    | Skip AI summary generation step |
| `--skip-embedding`  | Skip embedding generation step |
| `--output-format`   | Output format (`json` or `csv`) |

### Example: Skip Crawling and Embedding
```bash
python main.py --batch W25 --skip-crawl --skip-embedding
```

## Pipeline Steps
### 1. Scraping YC Companies
Extracts company links and details from YC's website.

### 2. Crawling Company Websites
Uses `crawl4ai` to extract text content from company websites.

### 3. AI Summarization
Generates structured summaries using OpenAI GPT models.

### 4. Embedding Generation
Converts summaries into numerical representations for semantic search.

### 5. Saving Processed Data
Stores data in JSON files and optionally as a CSV.

## Output Structure
```
/data
 ├── yc_links.csv          # Scraped YC company links
 ├── yc_details.json       # Company details
 ├── company_descriptions/ # Processed JSONs per company
 ├── companies_output.csv  # Optional combined CSV output
```

## Environment Variables
Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Dependencies
- `pandas`
- `asyncio`
- `argparse`
- `crawl4ai`
- `openai`
- `dotenv`
- `tqdm`

## License
This project is licensed under the MIT License.

## Contact
For any issues or feature requests, feel free to open an issue on GitHub.

