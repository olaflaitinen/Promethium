# Benchmarking and Metrics

Promethium includes tools to evaluate the quality of reconstruction and the performance of the system.

## Quality Metrics

### Signal-to-Noise Ratio (SNR)
Measured in decibels (dB). used to compare the energy of the reconstructed signal versus the difference from the ground truth.

### Structural Similarity Index (SSIM)
Perceptual metric that quantifies the preservation of structural features (reflectors, faults) rather than just pixel-wise difference.

### Peak Signal-to-Noise Ratio (PSNR)
Standard image processing metric used for quick regression testing.

## Performance Benchmarks

### Ingestion Speed
*   **SEG-Y Reader (Custom)**: ~500 MB/s on NVMe SSD.
*   **ObsPy Fallback**: ~50 MB/s.

### Reconstruction Speed (NVIDIA T4)
*   **U-Net Inference**: 12ms per gather (128x128).
*   **SoftImpute (CPU)**: 450ms per gather.
*   **PINN (Training)**: ~2 hours for 1000 iter convergence on single shot gather.

## Running Benchmarks
Use the provided script to run a standard benchmark suite:

```bash
python -m promethium.scripts.benchmark --data /path/to/test.sgy
```
