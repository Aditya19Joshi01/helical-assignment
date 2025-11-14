from datetime import datetime
import os
import numpy as np
import pandas as pd
import anndata as ad

from helical.models.geneformer import GeneformerConfig, GeneformerFineTuningModel


# =====================================================================
# 1. INPUT / OUTPUT SETUP
# =====================================================================

LOCAL_DATA_PATH = "/app/data/sample_data.h5ad"
BASE_OUTPUT_DIR = "/app/outputs"

# Timestamped directory
input_name = os.path.splitext(os.path.basename(LOCAL_DATA_PATH))[0]
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_OUTPUT_DIR = os.path.join(BASE_OUTPUT_DIR, f"{input_name}_{timestamp}")
os.makedirs(RUN_OUTPUT_DIR, exist_ok=True)

print(f"\n📁 Output directory: {RUN_OUTPUT_DIR}\n")


# =====================================================================
# 2. LOAD AND PREPROCESS DATA
# =====================================================================

print(f"📥 Loading dataset: {LOCAL_DATA_PATH}")
adata = ad.read_h5ad(LOCAL_DATA_PATH)
print(f"✅ Loaded dataset — shape: {adata.shape}")

# Reduce to first 3000 genes for speed
adata = adata[:, :3000]
print(f"🔹 Reduced to 3000 genes → shape: {adata.shape}")

# Detect label column
print("\n🔍 Detecting label column in cell metadata...")
label_col = next(
    (col for col in ["LVL1", "cell_type", "celltype", "label"] if col in adata.obs),
    None
)

if label_col is None:
    raise ValueError("❌ No suitable label column found in adata.obs")

cell_types = list(adata.obs[label_col])
label_set = sorted(set(cell_types))

print(f"🧬 Label column: {label_col}")
print(f"🧬 Unique labels ({len(label_set)}): {label_set}\n")


# =====================================================================
# 3. MODEL CONFIGURATION
# =====================================================================

print("🧠 Initializing Geneformer...")

config = GeneformerConfig(
    model_name="gf-12L-38M-i4096",
    batch_size=4
)

model = GeneformerFineTuningModel(
    geneformer_config=config,
    fine_tuning_head="classification",
    output_size=len(label_set)
)


# =====================================================================
# 4. DATA PROCESSING FOR MODEL
# =====================================================================

print("🔧 Processing dataset for Geneformer...")
dataset = model.process_data(adata)

# Add labels
dataset = dataset.add_column("cell_types", cell_types)

# Convert labels to integer IDs
class_to_id = {cls: i for i, cls in enumerate(label_set)}
id_to_class = {v: k for k, v in class_to_id.items()}

dataset = dataset.map(
    lambda ex: {**ex, "cell_types": class_to_id[ex["cell_types"]]},
    num_proc=1
)

# Smaller subset for speed
dataset = dataset.select(range(min(200, len(dataset))))
print(f"⚡ Using {len(dataset)} samples\n")


# =====================================================================
# 5. PRINT MODEL + DATA METADATA
# =====================================================================

print("\n==================== MODEL METADATA ====================")
cfg = config
model_name = cfg.config["model_name"]

print(f"Model Name:               {model_name}")
print(f"Batch Size:               {cfg.config['batch_size']}")
print(f"Embedding Layer:          {cfg.config['emb_layer']}")
print(f"Embedding Mode:           {cfg.config['emb_mode']}")
print(f"Device:                   {cfg.config['device']}")
print(f"Nproc (Workers):          {cfg.config['nproc']}")

info = cfg.model_map[model_name]
print("\n--- Model Architecture ---")
print(f"Input Size:               {info['input_size']}")
print(f"Embedding Size:           {info['embsize']}")
print(f"Special Token:            {info['special_token']}")
print(f"Model Version:            {info['model_version']}")

print("\n--- Dataset Info ---")
print(f"Classes:                  {len(label_set)}")
print(f"Labels:                   {label_set}")
print(f"Samples Used:             {len(dataset)}")
print(f"Input File:               {LOCAL_DATA_PATH}")
print(f"Output Directory:         {RUN_OUTPUT_DIR}")
print("=========================================================\n")


# =====================================================================
# 6. TRAINING
# =====================================================================

print("🚀 Starting fine-tuning...")
model.train(train_dataset=dataset, label="cell_types")
print("✅ Fine-tuning complete\n")


# =====================================================================
# 7. INFERENCE (LOGITS + LABELS)
# =====================================================================

print("⚙️ Running inference...")
outputs = model.get_outputs(dataset)
outputs_df = pd.DataFrame(outputs)
outputs_df.to_csv(os.path.join(RUN_OUTPUT_DIR, "raw_logits.csv"), index=False)

pred_ids = outputs_df.values.argmax(axis=1)
pred_labels = [id_to_class[i] for i in pred_ids]

results_df = pd.DataFrame({
    "True_Cell_Type": [id_to_class[x] for x in dataset["cell_types"]],
    "Predicted_Cell_Type": pred_labels
})
results_df.to_csv(os.path.join(RUN_OUTPUT_DIR, "predicted_celltypes.csv"), index=False)

print("📄 Saved prediction files\n")


# =====================================================================
# 8. EMBEDDINGS
# =====================================================================

print("🔮 Extracting embeddings...")
embeddings = model.get_embeddings(dataset)
np.save(os.path.join(RUN_OUTPUT_DIR, "fine_tuned_embeddings.npy"), embeddings)

print("📄 Saved fine_tuned_embeddings.npy\n")
print("🎉 All tasks completed successfully!")
