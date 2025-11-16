from datetime import datetime
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
from docker.types import Mount
import os

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 0,
}

# Load environment variables passed from docker-compose
DATA_DIR = os.getenv("HELICAL_DATA_PATH")
OUTPUT_DIR = os.getenv("HELICAL_OUTPUT_PATH")
SCRIPTS_DIR = os.getenv("HELICAL_SCRIPTS_PATH")

with DAG(
    dag_id="helical_fine_tune_dag",
    default_args=default_args,
    description="Run Helical Geneformer fine-tuning inside container",
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=["helical", "geneformer", "demo"],
) as dag:

    start = EmptyOperator(task_id="start")

    run_helical_container = DockerOperator(
        task_id="run_helical_model",
        image="helical-model:latest",
        container_name="helical-model-run",
        api_version="auto",
        auto_remove="success",
        mount_tmp_dir=False,
        command="python /app/scripts/run_model.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="airflow-network",

        mounts=[
            Mount(source=DATA_DIR, target="/app/data", type="bind"),
            Mount(source=OUTPUT_DIR, target="/app/outputs", type="bind"),
            Mount(source=SCRIPTS_DIR, target="/app/scripts", type="bind"),
        ],

        environment={
            "ENV_VAR": "default_value",
        },
    )

    end = EmptyOperator(task_id="end")

    start >> run_helical_container >> end
