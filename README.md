# **`AI Tech News Aggregator & Sentiment Analyzer`**

# **`Project Goal:`**

This project is a fully containerized Extract, Transform, Load (ETL) pipeline. Its primary function is to automatically scrape the latest technology news from curated sources and analyze the sentiment of those articles before persisting them into a structured PostgreSQL data warehouse.  
The entire stack—including the database and Airflow scheduler—is managed via Docker Compose, allowing for consistent deployment on any machine with Docker installed.

[architecture-diagram](https://github.com/user-attachments/assets/4a509a78-77cc-482e-bd37-bf781750bf90)

# **`Install & Setup:`**

Install the following before attempting to run the container:

* **Docker:** The Docker runtime engine and Docker Compose.  
* **API Key:** A valid `NEWSAPI_KEY` from [NewsAPI](https://newsapi.org/).

## **`Step 1: Clone the Repository`**

```
git clone https://github.com/earthGuyYellow/news-sentiment.git
cd news-sentiment
```

## **`Step 2: Configure Environment Variables`**

Create a `.env` file in the project root with the following variables (no spaces around `=`):

```
# --- Database Credentials (PostgreSQL) ---
POSTGRES_USER=airflow
POSTGRES_PASSWORD=your_secure_postgres_password
POSTGRES_DB=airflow

WAREHOUSE_DB_NAME=news_warehouse
WAREHOUSE_DB_USER=airflow
WAREHOUSE_DB_PASSWORD=your_secure_postgres_password

# --- Airflow & Application Configuration ---
NEWSAPI_KEY=your_newsapi_key_here
AIRFLOW_UID=50000
AIRFLOW_ADMIN_USER=admin
AIRFLOW_ADMIN_PASSWORD=your_secure_admin_password
AIRFLOW_FERNET_KEY=your_32_byte_base64_fernet_key
AIRFLOW_WEBSERVER_SECRET_KEY=your_random_hex_secret_key
```

**Tip:** Generate valid cryptographic keys for `AIRFLOW_FERNET_KEY` and `AIRFLOW_WEBSERVER_SECRET_KEY` by running:

```
python -c "import secrets, base64; print('AIRFLOW_FERNET_KEY=' + base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()); print('AIRFLOW_WEBSERVER_SECRET_KEY=' + secrets.token_hex(32))"
```

## **`Step 3: Launch the Stack`**

```
docker compose up --build -d
```

## **`Step 4: Verify the Pipeline & Query the Warehouse`**

* **Airflow UI:** Open `http://localhost:8080` in your browser to view logs, monitor task status, and check DAG runs. Log in using the `AIRFLOW_ADMIN_USER` and `AIRFLOW_ADMIN_PASSWORD` you defined in `.env`.  
* **Data Warehouse:** PostgreSQL runs on `localhost:5432`. Query the ingested sentiment data directly with:

```
docker exec -it news_postgres psql -U airflow -d news_warehouse -c "SELECT title, sentiment_score FROM staging.raw_stem_articles ORDER BY sentiment_score LIMIT 25;"
```

## **`Step 5: Stop the Containers`**

```
docker compose down
```

# **`Deep Dive (If you are gluttonous):`**

* **Orchestration:** Apache Airflow manages the workflow, ensuring that news fetching, sentiment analysis, and dbt transformations run reliably on a schedule.  
  * **Airflow Core (`airflow-common`):** Defines shared configurations (Executor, logging, API settings) applied to all compute services.  
  * **Initialization (`airflow-init`):** A one-time service responsible for bootstrapping the Airflow metadata database and creating the administrative user.  
  * **Webserver (`airflow-webserver`):** The UI layer where DAG status, logs, and run history are monitored (accessible at `http://localhost:8080`).  
  * **Scheduler (`airflow-scheduler`):** The core engine that runs the defined ETL workflows (DAG files), triggering news scraping, sentiment analysis, and database upserts.  
* **Data Flow:** NewsAPI / RSS → Python Script (`extract_news.py`) → VADER Sentiment Analysis → PostgreSQL `staging.raw_stem_articles` table (via upsert) → dbt transformations (`dbt_stem`).  
* **Schema:** The pipeline enforces data structure via Pydantic and stores records in the `staging.raw_stem_articles` table, ensuring high data quality.

# **`TL;DR:`**

* **Containerization:** Deploy the entire stack (PostgreSQL \+ Airflow \+ dbt) with a single `docker compose up --build -d` command.  
* **Workflow Management:** Uses Apache Airflow to manage ETL dependencies and retries for scraping jobs.  
* **Idempotency:** The underlying Python logic uses PostgreSQL `ON CONFLICT` clauses, ensuring that rerunning the pipeline does not create duplicate records.  
* **Secure Environment:** All sensitive data (API keys, passwords, encryption keys) is managed via environment variables and excluded from version control, adhering to industry-standard best practices.

