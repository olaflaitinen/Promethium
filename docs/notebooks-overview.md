# Promethium Notebooks Overview

This document provides a comprehensive guide to the Jupyter notebooks included in the Promethium repository.

## Installation

All notebooks require:

```bash
pip install promethium-seismic==1.0.4
```

**PyPI Package:** [https://pypi.org/project/promethium-seismic/1.0.4/](https://pypi.org/project/promethium-seismic/1.0.4/)

## Notebook Catalog

| Notebook | Title | Audience | Runtime | Description |
|----------|-------|----------|---------|-------------|
| 01 | Quickstart | Beginner | 2-3 min | Minimal end-to-end example |
| 02 | Data Ingestion | Beginner | 5 min | Loading SEG-Y, miniSEED, SAC formats |
| 03 | Signal Processing | Beginner | 5 min | Filters and transforms |
| 04 | Matrix Completion | Intermediate | 10 min | Classical recovery methods |
| 05 | U-Net Reconstruction | Intermediate | 10 min | Deep learning inference |
| 06 | GAN Reconstruction | Advanced | 10 min | GAN-based recovery |
| 07 | Evaluation Metrics | Intermediate | 5 min | SNR, PSNR, SSIM analysis |
| 08 | Kaggle/Colab | Beginner | 5 min | Cloud environment usage |
| 09 | Backend API | Advanced | 10 min | REST API integration |
| 10 | Synthetic Case Study | Intermediate | 10 min | End-to-end synthetic workflow |
| 11 | Real Data Case Study | Advanced | 15 min | Real-world data processing |
| 12 | Benchmarking | Advanced | 15-30 min | Method comparison and ablation |
| 13 | Batch Processing | Advanced | 10 min | Data engineering pipelines |
| 14 | Model Training | Advanced | 20+ min | Custom model development |
| 15 | Troubleshooting | All | 5 min | Common issues and solutions |

## Recommended Learning Path

### Getting Started
1. `01_quickstart_basic_usage.ipynb`
2. `02_data_ingestion_and_quality_control.ipynb`
3. `08_kaggle_and_colab_integration.ipynb`

### Building Skills
4. `03_signal_processing_basics.ipynb`
5. `04_matrix_completion_and_compressive_sensing.ipynb`
6. `05_deep_learning_unet_reconstruction.ipynb`
7. `07_evaluation_metrics_and_visualization.ipynb`

### Advanced Topics
8. `06_gan_based_high_fidelity_reconstruction.ipynb`
9. `10_end_to_end_case_study_synthetic_data.ipynb`
10. `11_end_to_end_case_study_real_world_data.ipynb`

### Research and Production
11. `12_benchmarking_and_ablation_studies.ipynb`
12. `13_data_engineering_pipelines_and_batch_jobs.ipynb`
13. `14_advanced_model_customization_and_training.ipynb`

### Reference
14. `15_troubleshooting_and_best_practices.ipynb`
15. `09_backend_api_and_job_system_demo.ipynb`

## Resource Requirements

| Category | GPU Required | Estimated RAM |
|----------|--------------|---------------|
| Beginner (01-03, 08) | No | 4 GB |
| Intermediate (04-07, 10) | Recommended | 8 GB |
| Advanced (09, 11-14) | Recommended | 16 GB |

## API Reference

All notebooks use the following import pattern:

```python
import promethium
from promethium import (
    load_segy,
    SeismicRecoveryPipeline,
    evaluate_reconstruction,
    generate_synthetic_traces,
    add_noise,
    set_seed,
    get_device,
)
```
