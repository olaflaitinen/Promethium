# Cross-Language Test Data

This directory contains reference test vectors for validating cross-language consistency.

## Purpose

All Promethium implementations (Python, R, Julia, Scala) must produce numerically consistent results. This directory provides:

1. **Synthetic datasets** with known ground truth
2. **Degraded versions** (noise, missing traces)
3. **Reference outputs** from the Python implementation
4. **Expected metric values** for validation

## Data Format

All data is stored in language-neutral formats:

| Format | Extension | Usage |
|--------|-----------|-------|
| HDF5 | `.h5` | Primary format for arrays |
| JSON | `.json` | Metadata and expected values |
| Binary | `.bin` | Raw float64 arrays |

## Test Cases

### 1. Basic Metrics (`test_metrics/`)
- `reference.h5`: Reference signal (100 x 500)
- `noisy.h5`: Noisy version (SNR ~10 dB)
- `expected.json`: Expected metric values

### 2. Matrix Completion (`test_matrix_completion/`)
- `full_matrix.h5`: Complete low-rank matrix
- `observed.h5`: Partially observed (50% mask)
- `mask.h5`: Boolean observation mask
- `recovered.h5`: Reference reconstruction
- `expected.json`: Expected recovery error

### 3. Wiener Denoising (`test_wiener/`)
- `clean.h5`: Clean synthetic signal
- `noisy.h5`: Noisy version
- `denoised.h5`: Reference denoised output
- `expected.json`: Expected SNR improvement

## Tolerance Specification

| Metric Type | Tolerance |
|-------------|-----------|
| SNR, PSNR | 0.01 dB |
| MSE | 1e-8 relative |
| SSIM | 1e-4 |
| Signal arrays | 1e-6 relative L2 |

## Generating Test Data

Run the Python script to regenerate all test data:

```bash
python scripts/generate_test_data.py
```

## Using Test Data

### Python
```python
import h5py
with h5py.File('testdata/test_metrics/reference.h5', 'r') as f:
    data = f['traces'][:]
```

### R
```r
library(hdf5r)
f <- H5File$new('testdata/test_metrics/reference.h5', 'r')
data <- f[['traces']]$read()
```

### Julia
```julia
using HDF5
data = h5read("testdata/test_metrics/reference.h5", "traces")
```

### Scala
```scala
// Using jhdf5 or similar
val file = HDF5Factory.openForReading("testdata/test_metrics/reference.h5")
val data = file.readDoubleMatrix("/traces")
```
