# User Guide

This guide explains how to use the Promethium Web Interface.

## Accessing the Dashboard
Navigate to `http://localhost:3000` (or your deployment URL).

## Managing Datasets

### Uploading Data
1.  Go to the **Datasets** tab.
2.  Click **Upload New**.
3.  Select a SEG-Y or SEG-2 file.
4.  Provide a unique name and optional description.
5.  Click **Submit**. The file will be ingested and indexed asynchronously.

### Inspecting Data
Click on any dataset in the list to view its metadata, including trace count, sample rate, and acquisition geometry.

## Running Jobs

### Submitting a Job
1.  Navigate to **Submit**.
2.  Select a specific dataset.
3.  Choose a processing workflow:
    *   **Bandpass Filter**: Simple frequency filtering.
    *   **Deconvolution**: Predictive deconvolution for multiple suppression.
    *   **U-Net Reconstruction**: Deep learning-based interpolation.
4.  Configure parameters (e.g., corners, gap size).
5.  Click **Run**.

### Monitoring Progress
Go to the **Jobs** tab to see the status of all submissions.
*   **Queued**: Waiting for a worker.
*   **Processing**: Currently running.
*   **Completed**: Finished successfully.
*   **Failed**: Encountered an error (logs available).

## Visualization
The **Visualize** tab allows interactive inspection of seismic gathers.
*   **Left Panel**: Original/Input data.
*   **Right Panel**: Processed/Reconstructed output.
*   **Controls**: Gain, clip, and zoom controls are available to enhance visibility.
