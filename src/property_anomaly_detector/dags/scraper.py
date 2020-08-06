import datetime

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from property_anomaly_detector.scraper.zoopla import zoopla

default_args = {
    "depends_on_past": False,
    "start_date": datetime.datetime.utcnow(),
    "retries": 3,
    "retry_delay": datetime.timedelta(minutes=1)
}

dag = DAG(
    "update_data",
    description="Gets the daily properties using zoopla API",
    schedule_interval="0 0 * * *",
    default_args=default_args,
    catchup=False
)

t1 = PythonOperator(task_id="update_data", python_callable=zoopla.main, dag=dag)