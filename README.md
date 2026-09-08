# AI Tech News Aggregator & Sentiment Analyzer

## Project Goal:
This project is a fully containerized Extract, Transform, Load (ETL) pipeline. Its primary function is to automatically scrape the latest technology news from curated sources and analyze the sentiment of those articles before persisting them into a structured PostgreSQL data warehouse.
The entire stack—including the database and Airflow scheduler—is managed via Docker Compose, allowing for consistent deployment on any machine with Docker installed.

<img width="875" height="1218" alt="architecture-diagram" src="https://github.com/user-attachments/assets/4a509a78-77cc-482e-bd37-bf781750bf90" />

## Install & Setup:
  Install the following before attempting to run the container: 
  - Docker: The Docker runtime engine.
  - API Key: A valid NEWSAPI_KEY from [NewsAPI](https://newsapi.org/).
  - 
### Step 1:
  - git clone [https://github.com/](https://github.com/earthGuyYellow/news-sentiment.git)
    cd news-sentiment
    
### Step 2:
  - Create a .env file with the following:

    ### --- Database Credentials (PostgreSQL) ---
    POSTGRES_USER=airflow
    POSTGRES_PASSWORD= your password
    POSTGRES_DB=news_warehouse
    
    ### --- Airflow & Application Configuration ---
    NEWSAPI_KEY= the api you signed up for on NewsAPI
    AIRFLOW_UID = 50000
    AIRFLOW_ADMIN_USER=admin
    AIRFLOW_ADMIN_PASSWORD= another secure password
    AIRFLOW_FERNET_KEY= a_very_long_and_random_key_here
    
### Step 3: 
  - Launch docker:
  - **docker-compose up --build -d** or **docker compose up --build -d**
### Step 4:
  - Airflow UI: Use your favorite desktop web browser to view logs, monitor task status, and check DAG runs at http://localhost:8080.
  - Log in using the AIRFLOW_ADMIN_USER and AIRFLOW_ADMIN_PASSWORD you defined.
  - Data Warehouse: The database is running on port 5432.
    - Use  **docker exec -it news_postgres psql -U airflow -d news_warehouse -c "SELECT title, sentiment_score FROM staging.raw_stem_articles ORDER BY sentiment_score LIMIT 25;"

### Step 5:
- Stop the container with:
  - **docker compose down ** or **docker-compose down**

## Deep Dive (If you are gluttonous):
- Orchestration: Apache Airflow manages the workflow, ensuring that news fetching and sentiment analysis run reliably on a schedule.
    - Airflow Core (airflow-common): Defines shared configurations (Executor, logging, API settings) applied to all compute services.
    - Initialization (airflow-init): A one-time service responsible for bootstrapping the Airflow environment and creating necessary administrative users.
    - Webserver (airflow-webserver): The UI layer where DAG status, logs, and run history are monitored (accessible at http://localhost:8080).
    - Scheduler (airflow-scheduler): The core engine that runs the defined ETL workflows (DAG files), triggering news scraping, sentiment analysis, and database upserts.   
- Data Flow: RSS → Python Script (extract_news.py) → VADER Sentiment Analysis → PostgreSQL raw_stem_articles table (via upsert).
- Schema: The pipeline enforces data structure via Pydantic and stores it in the staging.raw_stem_articles table, ensuring high data quality.
  
## TL:DR;
  - Containerization: Deploy the entire stack (DB + Airflow) with a single **docker-compose up** command.
  - Workflow Management: Uses Apache Airflow to manage ETL dependencies and retries for scraping jobs.
  - Idempotency: The underlying Python logic uses PostgreSQL **ON CONFLICT** clauses, ensuring that rerunning the pipeline does not create duplicate records.
  - Secure Environment: All sensitive data (API keys, passwords) is managed via environment variables, adhering to industry standard best practices.



 

  
		
		
		
		
