from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="helical_dag",
    start_date=datetime(2025, 11, 12),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    start = BashOperator(task_id="start", bash_command="echo 'Helical DAG started'")
    end = BashOperator(task_id="end", bash_command="echo 'Helical DAG ended'")
    start >> end
