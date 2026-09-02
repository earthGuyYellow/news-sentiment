FROM apache/airflow:2.8.1-python3.10

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install ingestion, schema validation, sentiment analysis, and dbt dependencies
RUN pip install --no-cache-dir \
    requests==2.31.0 \
    pydantic==2.6.1 \
    feedparser==6.0.11 \
    vaderSentiment==3.3.2 \
    psycopg2-binary==2.9.9 \
    dbt-core==1.7.8 \
    dbt-postgres==1.7.8 \
    'sqlalchemy>=1.4.36,<2.0.0'