# 🚀 YC Company Scraper Pipeline + YC ATLAS Search  

## 🔎 Explore YC Startups Instantly: [YC ATLAS](https://yc-atlas.lovable.app/)  

Use **[YC ATLAS](https://yc-atlas.lovable.app/)** to instantly **search, filter, and explore** Y Combinator startups with AI-powered insights. This tool makes finding relevant YC companies faster and more efficient.  

---

## 📌 Overview  

YC Company Scraper is a complete pipeline for **scraping, crawling, summarizing, and embedding** Y Combinator (YC) startup data. Whether you're a **founder, investor, researcher, or AI developer**, this tool provides structured YC data at scale.  

### 🔥 Why Use This?  
✅ **AI-Powered YC Search** – Use [YC ATLAS](https://yc-atlas.lovable.app/) for instant startup discovery.  
✅ **Comprehensive Scraper** – Extracts YC startup details from the official site.  
✅ **Web Crawler for Deep Insights** – Uses `crawl4ai` to fetch company website content.  
✅ **AI Summaries** – Get **instant, structured insights** for each startup.  
✅ **Semantic Search Ready** – Embed data for advanced search and analysis.  
✅ **Export in JSON & CSV** – Flexible formats for research and data science.  

---

## 🚀 Quick Start Guide  

### 📌 Installation  

#### Prerequisites:  
- Python **3.8+**  
- `pip` installed  
- OpenAI API key (store in `.env` as `OPENAI_API_KEY`)  

#### Install Dependencies:  
```bash
pip install -r requirements.txt
```

### ▶️ Running the Pipeline  
```bash
python main.py --batch W25 --output data
```

### 🔧 Command-Line Options  

| Argument            | Description |
|---------------------|-------------|
| `--batch`          | Specify YC batch (e.g., `W25`, `S24`). |
| `--output`         | Output directory (default: `data/`). |
| `--max-concurrent` | Set max concurrent requests for crawling (default: `10`). |
| `--force-refresh`  | Refresh all data, ignoring cached files. |
| `--skip-crawl`     | Skip website crawling. |
| `--skip-summary`   | Skip AI-generated summaries. |
| `--skip-embedding` | Skip embedding generation. |
| `--output-format`  | Choose output format (`json` or `csv`). |

Example: Run without crawling and embedding:  
```bash
python main.py --batch W25 --skip-crawl --skip-embedding
```

---

## 🔍 How the Pipeline Works  

### 1️⃣ Scraping YC Companies  
Extracts company names, descriptions, and links from YC’s website.  

### 2️⃣ Crawling Startup Websites  
Uses `crawl4ai` to extract text content for deeper insights.  

### 3️⃣ AI-Powered Summaries  
Generates concise summaries using OpenAI’s GPT models.  

### 4️⃣ Embedding for Search & Analysis  
Creates vector embeddings for **semantic search** and advanced analytics.  

### 5️⃣ Saving the Data  
Data is stored as structured **JSON files** and **CSV exports**.  

---

## 📂 Output Structure  

```
/data
 ├── yc_links.csv          # Scraped YC startup links
 ├── yc_details.json       # Full YC company details
 ├── company_descriptions/ # JSON summaries per startup
 ├── companies_output.csv  # Merged CSV dataset
```

---

## 🔑 Environment Variables  

Create a `.env` file with your OpenAI API key:  

```
OPENAI_API_KEY=your_api_key_here
```

---

## 📦 Dependencies  

- `pandas`  
- `asyncio`  
- `argparse`  
- `crawl4ai`  
- `openai`  
- `dotenv`  
- `tqdm`  

---

## 🌎 Try **YC ATLAS** for Instant YC Startup Search  

Looking for a **faster way to find YC startups?** Use [YC ATLAS](https://yc-atlas.lovable.app/) to:  

🔍 **Search & Filter** startups by batch, category, and keywords.  
🤖 **AI-Generated Summaries** for quick insights.  
📊 **Semantic Search** using embeddings for deep analysis.  

🚀 Try it now: **[YC ATLAS](https://yc-atlas.lovable.app/)**  

---

## 🛠 License & Contribution  

This project is licensed under the **MIT License**. Contributions are welcome! Feel free to **open an issue** or **submit a pull request** on GitHub.  

📩 **Have questions?** Reach out via GitHub Issues! 🚀  

🔗 **[Star This Repo on GitHub!](https://github.com/your-repo-link)** 🌟  

---

### 🚀 Why Use This YC Startup Scraper?  

✅ **AI-Powered Search via YC ATLAS** – Find startups instantly.  
✅ **All-in-One Data Pipeline** – Scrape, crawl, summarize, and analyze YC companies.  
✅ **AI-Powered Insights** – Get structured summaries powered by GPT.  
✅ **Semantic Search Ready** – Transform text into embeddings for intelligent retrieval.  
✅ **SEO-Optimized** – Discover YC startups faster with structured data.  

