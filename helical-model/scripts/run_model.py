import scanpy as sc
from helical.models.geneformer import Geneformer
import numpy as np
import torch
from torch.utils.data import Dataset
import os

DATA_PATH = "/app/data/sample_data.h5ad"
OUTPUT_DIR = "/app/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("📥 Loading dataset...")
adata = sc.read_h5ad(DATA_PATH)

# Convert sparse or dense matrix to numpy array
data_array = adata.X.toarray() if hasattr(adata.X, "toarray") else adata.X


class GeneformerDataset(Dataset):
    def __init__(self, data):
        self.data = data
        self.device = torch.device("cpu")
        self.format = "numpy"

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        if self.format == "torch":
            return torch.tensor(item, dtype=torch.float32, device=self.device)
        return item

    def select(self, indices):
        return GeneformerDataset(self.data[indices])

    def set_format(self, *, type=None, device=None):
        if type:
            self.format = type
        if device:
            self.device = torch.device(device)


print("🧠 Initializing Geneformer model...")
model = Geneformer()

print("🔧 Preparing data dataset for Geneformer...")
dataset = GeneformerDataset(data_array)

print("⚙️ Running inference to generate embeddings...")
embeddings = model.get_embeddings(dataset)

np.save(os.path.join(OUTPUT_DIR, "cell_embeddings.npy"), embeddings)
print(f"✅ Saved embeddings to {OUTPUT_DIR}/cell_embeddings.npy")
