# Kaggle Integration Guide

Promethium is designed to be **Kaggle-native**, meaning it can be used seamlessly in Kaggle notebooks both with and without internet access.

This guide explains how to use Promethium in Kaggle competitions and kernels using **Pip-less Source Imports** or **Offline Wheel Installation**.

---

## 1. Dataset Strategy

To use Promethium without downloading it from PyPI every time (or for offline competitions), you should attach one of the following Kaggle Datasets to your notebook.

### A. Wheel Dataset (Recommended for Stability)
This dataset contains the pre-built `.whl` file.

*   **Dataset Name**: `promethium-seismic-wheel-1.0.4` (or current version)
*   **Contents**:
    *   `promethium_seismic-1.0.4-py3-none-any.whl`
*   **Path in Kernel**: `../input/promethium-seismic-wheel-100/`

### B. Source Dataset (Recommended for Development)
This dataset contains the raw source code.

*   **Dataset Name**: `promethium-seismic-source-1.0.4`
*   **Contents**:
    *   `promethium/` (The package directory)
*   **Path in Kernel**: `../input/promethium-seismic-source-100/`

---

## Notebook Templates

We provide a **Universal Loader** notebook that handles all scenarios automatically.

### `03_auto_fallback_import.ipynb`
This notebook implements a robust hybrid import strategy:
1.  **Online/Dev**: Checks for standard `pip install`.
2.  **Offline Wheel**: Automatically installs from the attached Wheel Dataset.
3.  **Source Fallback**: Automatically adds the Source Dataset to `sys.path`.

**Usage**:
Copy the `load_promethium()` function from this notebook into your own Kaggle kernel. This ensures your code works seamlessly across local development and Kaggle's offline environment.

---

## 3. Best Practices for Kaggle

### GPU Selection
Promethium automatically detects GPUs. You can explicitly manage devices using:
```python
import torch
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
```

### Memory Management
Kaggle kernels often have limited RAM (13-30GB).
*   Use `SeismicRecoveryPipeline` with `batch_size` configurations if processing large surveys.
*   Avoid loading entire SEG-Y files into memory if possible; use memmapped reading (default in `segyio`).

### Output Data
Always write your results to `/kaggle/working/`.
```python
output_path = "/kaggle/working/reconstructed_data.sgy"
promethium.io.write_segy(data, output_path)
```
