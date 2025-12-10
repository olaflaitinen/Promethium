# How to Add a New Dataset to the Registry

This guide explains how to add new seismic datasets to the Promethium dataset registry for easy discovery and download.

---

## Overview

The dataset registry (`datasets/registry.yaml`) contains metadata about available datasets, including:
- Description and documentation
- Download URLs
- File format information
- License information
- Checksums for verification

---

## Step 1: Prepare Your Dataset

### Format Requirements

Datasets should be provided in one of these formats:
- **SEG-Y** (`.sgy`, `.segy`) - Industry standard
- **NumPy** (`.npy`, `.npz`) - For pre-processed data
- **HDF5** (`.h5`, `.hdf5`) - For large datasets
- **Zarr** (`.zarr`) - For cloud-native storage

### Packaging

Package your dataset as a compressed archive:
- ZIP format for cross-platform compatibility
- Include a README with dataset description
- Include license information

Example structure:
```
my_dataset.zip
  ├── README.md
  ├── LICENSE
  ├── data/
  │   ├── shots_001.sgy
  │   ├── shots_002.sgy
  │   └── ...
  └── metadata.json
```

---

## Step 2: Host the Dataset

### Hosting Options

1. **GitHub Releases** (recommended for small datasets)
   ```
   https://github.com/olaflaitinen/Promethium/releases/download/datasets-v1/my_dataset.zip
   ```

2. **Zenodo** (recommended for persistent DOI)
   ```
   https://zenodo.org/record/XXXXXXX/files/my_dataset.zip
   ```

3. **Cloud Storage** (for large datasets)
   ```
   https://storage.googleapis.com/promethium-datasets/my_dataset.zip
   ```

### Generate Checksum

```bash
sha256sum my_dataset.zip
```

---

## Step 3: Add to Registry

Edit `datasets/registry.yaml` and add your dataset entry:

```yaml
datasets:
  # ... existing datasets ...
  
  my_new_dataset:
    name: "My New Dataset"
    description: "Brief description of the dataset, its source, and intended use."
    url: "https://example.com/path/to/my_dataset.zip"
    format: "segy"
    size: "150MB"
    
    # Data dimensions
    traces: 500
    samples: 1000
    sample_rate_ms: 4
    
    # Licensing
    license: "CC BY-NC 4.0"
    source: "Institution or data provider"
    reference: "https://link-to-paper-or-documentation"
    
    # Verification
    checksum_sha256: "abc123def456..."
    
    # Optional metadata
    acquisition_type: "marine"
    region: "North Sea"
    year: 2023
```

---

## Step 4: Test the Entry

Verify your entry works correctly:

```python
from tools.dataset_downloader import DatasetManager

manager = DatasetManager()

# List datasets (should include your new one)
for ds in manager.list_datasets():
    print(f"{ds['id']}: {ds['name']}")

# Get info
info = manager.get_info("my_new_dataset")
print(info)

# Test download
manager.download("my_new_dataset", output_dir="test_data/")
```

Or via CLI:

```bash
promethium datasets list
promethium datasets download my_new_dataset --output-dir data/
```

---

## Step 5: Document the Dataset

Create documentation in `docs/datasets/`:

```markdown
# My New Dataset

## Overview
Description of the dataset...

## Acquisition Parameters
- Source type: ...
- Receiver spacing: ...
- Sample rate: ...

## Usage Example
\`\`\`python
from promethium import SeismicDataset
from tools.dataset_downloader import download_dataset

# Download
path = download_dataset("my_new_dataset")

# Load
dataset = SeismicDataset.from_file(path / "data" / "shots_001.sgy")
\`\`\`

## Citation
If you use this dataset, please cite:
...
```

---

## Registry Schema Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Human-readable name |
| `description` | string | Brief description |
| `url` | string | Download URL |
| `format` | string | File format (segy, npy, hdf5) |
| `license` | string | License identifier |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `size` | string | Approximate size (e.g., "150MB") |
| `traces` | integer | Number of traces |
| `samples` | integer | Samples per trace |
| `sample_rate_ms` | float | Sample rate in milliseconds |
| `checksum_sha256` | string | SHA256 hash for verification |
| `source` | string | Data provider |
| `reference` | string | Link to documentation |

---

## License Guidelines

Use standard license identifiers:
- `CC BY 4.0` - Attribution only
- `CC BY-NC 4.0` - Non-commercial use
- `CC0` - Public domain
- `MIT` - Permissive open source
- `Apache-2.0` - Permissive with patent grant

For proprietary datasets, specify access restrictions clearly.

---

## See Also

- [Dataset Registry](../../datasets/registry.yaml)
- [Data Ingestion Guide](./howto_run_cli.md)
- [API Reference: I/O Functions](../api-reference.md#io)
