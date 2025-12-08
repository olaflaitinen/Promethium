# User Guide

This document provides comprehensive instructions for using the Promethium framework, covering common workflows from data ingestion to result export.

## Table of Contents

- [Getting Started](#getting-started)
- [Data Management](#data-management)
- [Reconstruction Workflows](#reconstruction-workflows)
- [Visualization](#visualization)
- [Job Management](#job-management)
- [Model Selection](#model-selection)
- [Result Export](#result-export)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Getting Started

### Accessing Promethium

After deployment, access Promethium through your web browser:

- **Local Development**: http://localhost:4200
- **Production**: Your configured domain (e.g., https://promethium.example.com)

### First-Time Login

1. Navigate to the login page.
2. Enter your credentials (provided by your administrator).
3. Upon first login, you may be prompted to change your password.
4. Review and accept the terms of use if applicable.

### Dashboard Overview

The dashboard provides:

- **Recent Jobs**: Status of your most recent processing jobs
- **Quick Actions**: Common operations accessible with one click
- **System Status**: Current system health and capacity
- **Notifications**: Important alerts and messages

---

## Data Management

### Supported Formats

Promethium supports the following seismic data formats:

| Format | Extensions | Read | Write | Notes |
|--------|------------|------|-------|-------|
| SEG-Y | .sgy, .segy | Yes | Yes | Rev 0, 1, 2 supported |
| SEG-2 | .sg2, .seg2 | Yes | No | Near-surface surveys |
| miniSEED | .mseed, .ms | Yes | Yes | Continuous data |
| SAC | .sac | Yes | Yes | Single traces |
| GCF | .gcf | Yes | No | Guralp format |

### Uploading Data

#### Web Interface Upload

1. Navigate to **Data** in the sidebar.
2. Click the **Upload** button.
3. Drag and drop files or click to browse.
4. Select one or more files (maximum 10 GB per upload).
5. Optional: Add description and tags.
6. Click **Upload** to begin transfer.

#### Large File Upload

For files exceeding 10 GB:

1. Use the **Chunked Upload** option.
2. Files are uploaded in 100 MB segments.
3. Upload can be paused and resumed.
4. Progress is preserved if the browser is closed.

#### Bulk Upload via API

```bash
# Upload single file
curl -X POST "http://localhost:8000/api/v1/data/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@survey.sgy"

# Upload with metadata
curl -X POST "http://localhost:8000/api/v1/data/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@survey.sgy" \
  -F "metadata={\"description\":\"Field survey 2025\",\"tags\":[\"exploration\"]}"
```

### Dataset Browser

The dataset browser displays all uploaded datasets:

| Column | Description |
|--------|-------------|
| Name | Dataset filename |
| Format | Detected file format |
| Traces | Number of traces |
| Samples | Samples per trace |
| Size | File size |
| Uploaded | Upload timestamp |
| Status | Processing status |

**Filtering Options:**
- Search by name
- Filter by format
- Filter by date range
- Filter by tags

### Dataset Details

Click on a dataset to view details:

- **Header Summary**: Key header values
- **Statistics**: Min, max, mean, RMS amplitude
- **Geometry**: Source and receiver positions (if available)
- **Quality Report**: Automated QC findings
- **Preview**: Visual thumbnail of data

---

## Reconstruction Workflows

### Standard Reconstruction Workflow

#### Step 1: Select Input Dataset

1. Navigate to **Jobs** > **New Job**.
2. Select **Reconstruction** as the job type.
3. Choose the input dataset from the list.
4. Click **Next**.

#### Step 2: Configure Missing Data

Specify which data requires reconstruction:

**Automatic Detection:**
- Enable **Auto-detect missing traces**
- System identifies null or anomalous traces

**Manual Specification:**
- Provide trace numbers: `10, 15, 23` or ranges: `100-150`
- Upload a mask file defining missing regions
- Draw regions on the preview display

#### Step 3: Select Model

Choose a reconstruction model:

| Model | Use Case | Speed | Quality |
|-------|----------|-------|---------|
| UNet-Fast | Quick preview | Fast | Good |
| UNet-Accurate | Production use | Medium | Excellent |
| VAE-Uncertainty | Uncertainty estimation | Medium | Excellent |
| GAN-HighRes | Maximum fidelity | Slow | Superior |
| PINN-Physics | Physical consistency | Slow | Excellent |

#### Step 4: Configure Parameters

Common parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| Patch Size | Processing window size | 256 |
| Overlap | Patch overlap percentage | 50% |
| Batch Size | Inference batch size | 8 |
| Ensemble | Number of ensemble runs | 1 |

#### Step 5: Submit Job

1. Review the configuration summary.
2. Optional: Enable email notification.
3. Click **Submit Job**.
4. Note the assigned Job ID for tracking.

### Denoising Workflow

For noise reduction without missing data:

1. Select **Denoising** as job type.
2. Choose input dataset.
3. Select denoising strength (Low/Medium/High).
4. Submit job.

### Batch Processing

Process multiple datasets with identical parameters:

1. Select **Batch Processing** mode.
2. Add multiple datasets to the batch.
3. Configure parameters once.
4. Submit batch as a single job group.
5. Results are organized by input dataset.

---

## Visualization

### Trace Viewer

The trace viewer displays seismic data interactively:

**Navigation:**
- Scroll to pan vertically (time)
- Shift+Scroll to pan horizontally (trace)
- Ctrl+Scroll to zoom
- Click and drag to select region

**Display Options:**
- **Wiggle**: Traditional wiggle trace display
- **Variable Density**: Color-mapped amplitude
- **Variable Area**: Filled wiggle traces

**Tools:**
- Trace picking
- Amplitude measurement
- Spectrum analysis (right-click)

### Gather Viewer

For prestack data display:

- CMP gather organization
- NMO/moveout display options
- Offset or angle axis selection
- AGC and gain controls

### Comparison View

Compare input and output data:

- **Side by Side**: Two panels with synchronized navigation
- **Overlay**: Transparency-blended overlay
- **Difference**: Displays input minus output
- **Flicker**: Toggle rapidly between views

### Color Palettes

Available color scales:

| Palette | Use Case |
|---------|----------|
| Gray | Standard seismic display |
| Seismic | Red-white-blue diverging |
| Rainbow | Amplitude mapping |
| Phase | Phase-sensitive display |
| Custom | User-defined colors |

---

## Job Management

### Job Status

Jobs progress through these states:

| Status | Description |
|--------|-------------|
| Pending | Job queued, awaiting worker |
| Running | Job actively processing |
| Completed | Job finished successfully |
| Failed | Job encountered error |
| Cancelled | Job cancelled by user |

### Monitoring Jobs

The Jobs page displays all submitted jobs:

- **In Progress**: Active and pending jobs
- **Completed**: Finished jobs (last 30 days)
- **Failed**: Jobs requiring attention

**Job Details:**
- Configuration summary
- Progress percentage
- Elapsed time
- Log output (expandable)
- Resource usage

### Cancelling Jobs

To cancel a running job:

1. Open job details.
2. Click **Cancel Job**.
3. Confirm cancellation.
4. Partial results may be available.

### Job History

View historical job information:

- Filter by date range
- Search by job ID or dataset name
- Export job history CSV

---

## Model Selection

### Model Registry

Available models are listed in the model registry:

| Information | Description |
|-------------|-------------|
| Name | Model identifier |
| Version | Model version number |
| Type | Architecture family |
| Training Data | Description of training data |
| Metrics | Validation performance |

### Model Comparison

Compare model performance:

1. Select multiple models.
2. Choose comparison dataset.
3. Run comparison job.
4. View side-by-side results with metrics.

### Custom Models

Upload custom-trained models:

1. Navigate to **Models** > **Upload**.
2. Provide model file (PyTorch .pt format).
3. Provide configuration YAML.
4. Complete metadata form.
5. Model becomes available after validation.

---

## Result Export

### Export Formats

Export reconstructed data in supported formats:

| Format | Description |
|--------|-------------|
| SEG-Y | Industry standard, full header preservation |
| miniSEED | For seismological applications |
| NumPy | .npy files for Python workflows |
| HDF5 | Hierarchical data format |
| CSV | For non-seismic consumers |

### Export Options

Configure export:

- **Format**: Output format selection
- **Compression**: Enable LZF/GZIP compression
- **Subset**: Export selected traces only
- **Header Updates**: Apply header modifications
- **Include QC**: Attach quality control report

### Downloading Results

1. Open completed job.
2. Navigate to **Results** tab.
3. Select export format.
4. Click **Download**.
5. For large files, a download link is emailed.

---

## Best Practices

### Data Preparation

- Verify file integrity before upload.
- Remove severely corrupted traces beforehand.
- Apply basic preprocessing if needed.
- Document known issues in dataset description.

### Model Selection

- Start with fast models for initial assessment.
- Use physics-informed models when AVO matters.
- Enable uncertainty estimation for critical applications.
- Run ensemble for production workflows.

### Quality Control

- Always review reconstruction visually.
- Check edge effects at patch boundaries.
- Verify amplitude preservation.
- Compare statistics before and after.

### Performance Optimization

- Use appropriate patch sizes (256-512 typical).
- Larger batches improve throughput on GPU.
- Consider preprocessing to reduce data size.
- Schedule large jobs during off-peak hours.

---

## Troubleshooting

### Common Issues

**Upload Fails:**
- Check file size limits.
- Verify file format is supported.
- Check network connectivity.
- Review browser console for errors.

**Job Stuck in Pending:**
- Check worker availability in system status.
- GPU jobs require GPU worker.
- Review queue depth.

**Poor Reconstruction Quality:**
- Try different model.
- Increase ensemble runs.
- Check if data characteristics match model training.
- Review preprocessing parameters.

**Visualization Not Loading:**
- Check browser WebGL support.
- Reduce display data range.
- Try different browser.
- Clear browser cache.

### Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| E001 | Invalid file format | Verify file format |
| E002 | Insufficient storage | Contact administrator |
| E003 | Model not found | Check model availability |
| E004 | GPU memory exceeded | Reduce batch size |
| E005 | Timeout | Retry or contact support |

### Getting Help

If issues persist:

1. Check the [FAQ](faq.md).
2. Search existing GitHub issues.
3. Open a new issue with:
   - Job ID
   - Error messages
   - Steps to reproduce

---

## Related Documents

| Document | Description |
|----------|-------------|
| [API Reference](api-reference.md) | Programmatic API usage |
| [Configuration](configuration.md) | Configuration options |
| [ML Pipelines](ml-pipelines.md) | Model details |
| [FAQ](faq.md) | Frequently asked questions |

---

*For additional assistance, visit [SUPPORT.md](../SUPPORT.md).*
