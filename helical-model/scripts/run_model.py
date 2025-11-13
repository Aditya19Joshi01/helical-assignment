from datetime import datetime
import anndata as ad
import numpy as np
import pandas as pd
import os
from helical.models.geneformer import GeneformerConfig, GeneformerFineTuningModel
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# === INPUT / OUTPUT SETUP ===
LOCAL_DATA_PATH = "/app/data/sample_data.h5ad"
BASE_OUTPUT_DIR = "/app/outputs"

# Extract base name of input file (without extension)
input_name = os.path.splitext(os.path.basename(LOCAL_DATA_PATH))[0]

# Create unique run directory using timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_OUTPUT_DIR = os.path.join(BASE_OUTPUT_DIR, f"{input_name}_{timestamp}")
os.makedirs(RUN_OUTPUT_DIR, exist_ok=True)

print(f"📁 Creating new output directory for this run: {RUN_OUTPUT_DIR}")

# === LOAD DATASET ===
print(f"📥 Loading local dataset: {LOCAL_DATA_PATH}")
adata = ad.read_h5ad(LOCAL_DATA_PATH)
print(f"✅ Loaded dataset with shape: {adata.shape}")

# 🔹 Reduce number of genes for speed
adata = adata[:, :3000]
print(f"🔹 Reduced dataset shape: {adata.shape}")

# === PREPARE LABELS ===
print("Checking obs columns:", adata.obs.columns)
label_col = None
for candidate in ["LVL1", "cell_type", "celltype", "label"]:
    if candidate in adata.obs.columns:
        label_col = candidate
        break

if label_col is None:
    raise ValueError("❌ Could not find a valid label column in adata.obs!")

cell_types = list(adata.obs[label_col])
label_set = sorted(set(cell_types))
print(f"🧬 Found {len(label_set)} unique cell types: {label_set}")

# === MODEL CONFIGURATION ===
print("🧠 Creating GeneformerConfig...")
geneformer_config = GeneformerConfig(
    model_name="gf-12L-38M-i4096",
    batch_size=4
)

print("🧠 Initializing fine-tuning model...")
geneformer_fine_tune = GeneformerFineTuningModel(
    geneformer_config=geneformer_config,
    fine_tuning_head="classification",
    output_size=len(label_set)
)

# === DATA PROCESSING ===
print("🔧 Processing data...")
dataset = geneformer_fine_tune.process_data(adata)

print("➡️ Adding cell_types column to dataset...")
dataset = dataset.add_column("cell_types", cell_types)

class_id_dict = {cls: i for i, cls in enumerate(label_set)}
reverse_class_dict = {v: k for k, v in class_id_dict.items()}

def classes_to_ids(example):
    example["cell_types"] = class_id_dict[example["cell_types"]]
    return example

print("➡️ Mapping cell types to numeric IDs...")
dataset = dataset.map(classes_to_ids, num_proc=1)

# 🔹 Keep limited samples for speed
dataset = dataset.select(range(min(200, len(dataset))))
print(f"✅ Using {len(dataset)} samples for lightweight fine-tuning")

# === TRAIN ===
print("🚀 Starting fine-tuning (short demo run)...")
geneformer_fine_tune.train(train_dataset=dataset, label="cell_types")

# === INFERENCE ===
print("⚙️ Getting logits from fine-tuned model...")
outputs = geneformer_fine_tune.get_outputs(dataset)
outputs_df = pd.DataFrame(outputs)
outputs_df.to_csv(os.path.join(RUN_OUTPUT_DIR, "raw_logits.csv"), index=False)

# === POST-PROCESS LOGITS TO LABELS ===
print("🧩 Converting logits to predicted cell types...")
predicted_ids = outputs_df.values.argmax(axis=1)
predicted_labels = [reverse_class_dict[i] for i in predicted_ids]

results_df = pd.DataFrame({
    "True_Cell_Type": [reverse_class_dict[c] for c in dataset["cell_types"]],
    "Predicted_Cell_Type": predicted_labels
})
results_df.to_csv(os.path.join(RUN_OUTPUT_DIR, "predicted_celltypes.csv"), index=False)
print(f"✅ Saved readable predictions → {RUN_OUTPUT_DIR}/predicted_celltypes.csv")

# === EMBEDDINGS ===
print("⚙️ Getting embeddings from fine-tuned model...")
embeddings = geneformer_fine_tune.get_embeddings(dataset)
np.save(os.path.join(RUN_OUTPUT_DIR, "fine_tuned_embeddings.npy"), embeddings)

# === VISUALIZATION ===
print("📊 Running PCA for quick visualization...")

mask = np.isfinite(embeddings).all(axis=1)
clean_embeddings = embeddings[mask]

if clean_embeddings.shape[0] < 2:
    print("⚠️ Not enough valid embedding points for PCA visualization.")
else:
    clean_embeddings = np.nan_to_num(clean_embeddings, nan=0.0, posinf=0.0, neginf=0.0)
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(clean_embeddings)

    plt.figure(figsize=(6, 5))
    plt.scatter(
        reduced[:, 0],
        reduced[:, 1],
        s=20,
        alpha=0.7,
        c=np.arange(len(reduced)),
        cmap="viridis"
    )
    plt.title("Geneformer Cell Embeddings (PCA Projection)")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.tight_layout()
    plt.savefig(os.path.join(RUN_OUTPUT_DIR, "embedding_plot.png"))
    print(f"✅ Saved embedding_plot.png → {RUN_OUTPUT_DIR}/embedding_plot.png")

print("🎉 Fine-tuning complete — outputs generated successfully!")
