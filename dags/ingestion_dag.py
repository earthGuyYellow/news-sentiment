from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys

# Add scripts directory to path inside container
sys.path.append("/opt/airflow/scripts")
from extract_news import init_staging_table, fetch_and_stage_news

default_args = {
    "owner": "data_engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def run_ingestion():
    init_staging_table()
    fetch_and_stage_news()


with DAG(
    dag_id="stem_news_pipeline",
    default_args=default_args,
    description="Ingest STEM news, compute sentiment, and run dbt transformations",
    schedule_interval="0 */6 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["stem", "ingestion", "dbt"],
) as dag:
    ingest_task = PythonOperator(
        task_id="fetch_and_stage_stem_news",
        python_callable=run_ingestion,
    )

    dbt_run_task = BashOperator(
        task_id="dbt_run_transformations",
        bash_command='echo "dbt models will run here after dbt setup"',
    )

    ingest_task >> dbt_run_task
