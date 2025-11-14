# 🧬 Helical Model Container — Geneformer Fine-Tuning Environment

This directory defines a **Dockerized environment** for running the **Helical Geneformer** model locally or via Airflow. It encapsulates all necessary dependencies and scripts for a reproducible machine learning fine-tuning workflow.

---

## 📦 Contents

The directory structure is as follows:

```

helical-model/
├── Dockerfile
├── requirements-model.txt
├── scripts/
│ └── run\_model.py
├── data/
│ └── sample\_data.h5ad \# Your input dataset
└── outputs/ \# Generated results

````

---

## ⚙️ Dockerfile Summary

The `Dockerfile` is optimized for reproducibility and build speed:

* **Base image:** `python:3.11-slim` (minimal and efficient)
* Installs core dependencies listed in `requirements-model.txt`.
* Copies application code and sets `/app` as the working directory.
* The default entrypoint runs the fine-tuning script: `python scripts/run_model.py`.

---

## 🧩 Script: `scripts/run_model.py`

### Overview

This script contains the core logic for the fine-tuning process:

* **Data Loading:** Loads the required local `.h5ad` dataset from `/app/data/sample_data.h5ad`.
* **Preprocessing:** Reduces the feature count (e.g., to **3000 genes**) to speed up the fine-tuning process for demonstration.
* **Fine-Tuning:** Initializes and fine-tunes the **Geneformer** model on the loaded data.
* **Print Metadata:** Outputs dataset shape and other relevant information to the console for verification.
* **Artifact Generation:** Generates the following output files:
    * `raw_logits.csv`
    * `predicted_celltypes.csv`
    * `fine_tuned_embeddings.npy`
    * `embedding_plot.png` (PCA visualization)
* **Storage:** Stores all outputs inside a unique, timestamped directory under `/app/outputs`: `outputs/sample_data_<timestamp>/`.

---

## 🚀 Usage

### 1️⃣ Build the Image

Build the Docker image with the tag `helical-model:latest`:

```bash
docker build -t helical-model:latest .
````

### 2️⃣ Run the Container Manually

You can test the environment by running the container directly, mounting the required local directories:

```bash
docker run -it --rm \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/outputs:/app/outputs" \
  -v "$(pwd)/scripts:/app/scripts" \
  helical-model
```

You should see logs similar to:

```sql
📥 Loading local dataset...
✅ Loaded dataset with shape: (...)
🎉 Fine-tuning complete — outputs generated successfully!
```

-----

## 🧠 Features

✅ Uses local data only (no online download needed)
✅ Generates timestamped output directories to prevent overwriting
✅ Easily integrates with Airflow via shared network
✅ Minimal dependencies for fast build and reproducibility

### 🔍 Example Output Structure

After a successful run, the `outputs/` directory will look like this:

```markdown
outputs/
└── sample_data_20251112_174512/
    ├── raw_logits.csv
    ├── predicted_celltypes.csv
    ├── fine_tuned_embeddings.npy
```

-----

## 🧭 Notes

  * Each run produces a new timestamped directory to **preserve historical results**.
  * The container can be triggered manually (as shown above) or via **Airflow's DockerOperator** for automated orchestration.
  * For faster iteration, dependencies are **cached** in the Docker image layers—no need to reinstall dependencies between runs.

### 🧩 Next Steps

  * Log execution metrics (time taken, loss, accuracy, etc.) from `run_model.py`.
  * Extend the pipeline with post-processing or evaluation scripts to be run in subsequent Airflow tasks.