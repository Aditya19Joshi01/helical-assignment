# 🌬️ Apache Airflow Setup — Helical Workflow Orchestration

This directory contains the **Airflow environment** for orchestrating the Helical Geneformer model pipeline. It uses Docker Compose to manage the necessary services for a full Airflow installation.

---

## 🧱 Components

* `docker-compose.yml` — Spins up the core Airflow services: **webserver**, **scheduler**, **worker**, **Redis**, and **PostgreSQL** (metadata database).
* `dags/helical_dag.py` — Defines the main Airflow DAG (`helical_fine_tune_dag`) to execute the Helical model container.
* `logs/`, `plugins/`, `config/` — Standard Airflow support directories for logs, custom plugins, and configuration files.
* **Shared Docker Network** (`helical_network`) — Created in the main project `docker-compose` setup to enable secure communication between Airflow and the separate `helical-model` container.

---

## 🚀 Getting Started

### 1️⃣ Initialize Airflow

Run the first-time setup command. This initializes the metadata database and creates the default admin user:

```bash
docker-compose up airflow-init
````

> **Default Credentials:** The admin user is created with `username: airflow` / `password: airflow`.

### 2️⃣ Start the Airflow Environment

Start all Airflow services in detached mode:

```bash
docker-compose up -d
```

Access the Airflow Web UI:

👉 **http://localhost:8080**

-----

## 🧩 DAG Overview

**DAG ID:** `helical_fine_tune_dag`

This DAG is defined in `dags/helical_dag.py` and is responsible for reliably executing the machine learning workload. It uses the **DockerOperator** to run the separate model container.

The execution flow involves:

1.  **Spins up** the `helical-model:latest` container.
2.  **Mounts** local data and script directories (`/app/data`, `/app/scripts`, `/app/outputs`).
3.  **Executes** the `run_model.py` script inside the container.
4.  **Writes** outputs to timestamped directories inside the shared `/outputs` volume.

-----

## 🧭 Notes and Troubleshooting

  * The DAG can be triggered **manually** from the UI or configured for **scheduled runs** (`@daily`, `@hourly`, etc.) in the Python file.
  * Airflow logs for each task are essential for debugging and are visible in the **Logs tab** of the web UI.
  * The `docker_url="unix://var/run/docker.sock"` setting is necessary for the Airflow worker to launch new sibling containers (the model container).
  * The **Airflow container** communicates with the **model container** via the shared `helical_network`.

-----

## 📁 Useful Commands

| Command | Description |
| :--- | :--- |
| `docker ps` | List all running Docker containers in the environment. |
| `docker-compose down` | Stop and remove all containers defined in `docker-compose.yml`. |
| `docker-compose logs airflow-scheduler` | View detailed logs for the Airflow Scheduler service. |