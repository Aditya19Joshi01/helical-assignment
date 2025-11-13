# 🧬 Helical Geneformer Workflow — Airflow Orchestrated ML Pipeline

This repository demonstrates a **containerized machine learning pipeline** for running and orchestrating fine-tuning of the **Helical Geneformer** model using **Docker** and **Apache Airflow**.

It was built as part of a technical assignment to showcase containerization, orchestration, and reproducible ML workflows.

---

## 🚀 Overview

The setup includes:
* **Helical Model Container (`helical-model/`)**
    A self-contained Python environment with the Helical library and dependencies installed.
* **Apache Airflow Orchestration (`airflow/`)**
    Runs as a separate service (via `docker-compose`) to manage and execute the Helical workflow as a DAG.
* **Local Data Integration**
    Uses a local `.h5ad` dataset instead of downloading from the web.
* **Automated Output Storage**
    Each run generates results in a timestamped directory under `/outputs`, ensuring all runs are archived separately.

---

## ⚙️ Setup Guide

### 1️⃣ Build the Model Container

```bash
cd helical-model
docker build -t helical-model:latest .
````

### 2️⃣ Run the Model Container Manually (for testing)

```bash
docker run -it --rm \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/outputs:/app/outputs" \
  -v "$(pwd)/scripts:/app/scripts" \
  helical-model
```

### 3️⃣ Set Up Airflow Environment

Move into the `airflow/` directory and run:

```bash
cd ../airflow
docker-compose up airflow-init
docker-compose up
```

This starts:

  * Airflow Webserver at **http://localhost:8080** (default credentials: `airflow` / `airflow`)
  * Scheduler, Worker, Redis, and Postgres containers.

### 4️⃣ Running the Helical DAG

Once Airflow is up:

1.  Open the Airflow UI → DAGs page.
2.  Enable and trigger the DAG named `helical_fine_tune_dag`.
3.  Monitor logs and progress live from the Airflow UI.

Outputs will appear under `helical-model/outputs/<filename_timestamp>/`.

-----

## 📁 Outputs Generated

Each run produces:

  * `raw_logits.csv` — Model logits for each sample.
  * `predicted_celltypes.csv` — True vs predicted cell type mapping.
  * `fine_tuned_embeddings.npy` — Embedding vectors post fine-tuning.
  * `embedding_plot.png` — PCA visualization of embeddings.

All stored under:

```bash
helical-model/outputs/<input_file_timestamp>/
```

-----

## 🧠 Key Features Demonstrated

✅ Containerized ML environment
✅ Airflow DAG orchestration
✅ Local data mounting
✅ Timestamp-based run directories
✅ Successful end-to-end workflow execution

-----

## 📌 Next Steps

  * Add Airflow task for result summarization
  * Add observability using Prometheus/Grafana
  * Push outputs to S3 / cloud storage
  * Introduce scheduled DAG runs
  * Add metadata logging (run duration, dataset stats)

-----

## 👨‍💻 Author

Aditya Joshi

