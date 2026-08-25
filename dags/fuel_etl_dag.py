from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from scripts.extract import extract
from scripts.transform import transform
from scripts.load import load

default_args = {
    "owner": "data_engineering",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="fuel_price_etl",
    default_args=default_args,
    description="ETL pipeline for fuel price data",
    start_date=datetime(2026, 8, 24),
    schedule="*/10 * * * *",     #"40 12 * * *",  # 1:20 PM WAT (UTC+1)
    catchup=False,
    tags=["ETL", "fuel-price"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract_fuel_price",
        python_callable=extract,
    )

    transform_task = PythonOperator(
        task_id="transform_fuel_price",
        python_callable=transform,
        op_kwargs={"df": extract_task.output},
    )

    load_task = PythonOperator(
        task_id="load_fuel_price",
        python_callable=load,
        op_kwargs={"df": transform_task.output},
    )

    extract_task >> transform_task >> load_task