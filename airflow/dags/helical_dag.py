from datetime import datetime
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
from docker.types import Mount

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 0,
}

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
            Mount(
                source="C:/Users/ajhas/Desktop/Projects/helical-assignment/helical-model/data",
                target="/app/data",
                type="bind",
            ),
            Mount(
                source="C:/Users/ajhas/Desktop/Projects/helical-assignment/helical-model/outputs",
                target="/app/outputs",
                type="bind",
            ),
            Mount(
                source="C:/Users/ajhas/Desktop/Projects/helical-assignment/helical-model/scripts",
                target="/app/scripts",
                type="bind",
            ),
        ],

        environment={
            "ENV_VAR": "default_value",
        },
    )

    end = EmptyOperator(task_id="end")

    start >> run_helical_container >> end
