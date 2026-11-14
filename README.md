# AI Tech News Aggregator & Sentiment Analyzer

## Project Goal:
This project is a fully containerized Extract, Transform, Load (ETL) pipeline. Its primary function is to automatically scrape the latest technology news from curated sources and analyze the sentiment of those articles before persisting them into a structured PostgreSQL data warehouse.
The entire stack—including the database and Airflow scheduler—is managed via Docker Compose, allowing for consistent deployment on any machine with Docker installed.

<img width="875" height="1218" alt="architecture-diagram" src="[https://github.com/user-attachments/assets/4a509a78-77cc-482e-bd37-bf781750bf90](https://github.com/user-attachments/assets/4a509a78-77cc-482e-bd37-bf781750bf90)" />

## Install & Setup:
Install the following before attempting to run the container:
- **Docker:** The Docker runtime engine and Docker Compose.
- **API Key:** A valid `NEWSAPI_KEY` from [NewsAPI](https://newsapi.org/).

### Step 1: Clone the Repository
```bash
git clone https://github.com/earthGuyYellow/news-sentiment.git
cd news-sentiment
