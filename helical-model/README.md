## Data Requirements

This project requires a `.h5ad` (AnnData) file for training. 

**For reviewers/users:**
- Place your `.h5ad` dataset in `helical-model/data/` directory
- Rename it to `sample_data.h5ad` or update the path in `run_model.py`
- The dataset should contain:
  - Cell expression data (genes × cells)
  - Cell type labels in `.obs` (e.g., column named `LVL1`, `cell_type`, or `celltype`)

**Sample data sources:**
- [Human PBMC dataset](https://cf.10xgenomics.com/samples/cell-exp/3.0.0/pbmc_1k_v3/pbmc_1k_v3_filtered_feature_bc_matrix.h5)
- [Mouse brain dataset](https://cellxgene.cziscience.com/)
- Convert your own data using `scanpy.read_*()` functions

**Note:** The actual dataset is not included in this repository due to size constraints.