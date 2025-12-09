# Cross-Language Validation Tests

This directory contains test infrastructure for validating numerical consistency
across all Promethium language implementations (Python, R, Julia, Scala).

## Purpose

Ensure that all implementations produce identical results (within tolerance) when:
- Given the same input data
- Configured with the same parameters
- Running the same algorithms

## Test Protocol

### 1. Generate Reference Data (Python)

```bash
cd tests/cross_language
python generate_reference.py
```

This creates:
- `reference/input_matrix.npy` - Test input matrix
- `reference/mask.npy` - Observation mask
- `reference/completed_python.npy` - Python output
- `reference/metrics_python.json` - Python metrics

### 2. Run Language Tests

**Python:**
```bash
pytest test_cross_language_python.py
```

**R:**
```r
source("test_cross_language_r.R")
```

**Julia:**
```julia
include("test_cross_language_julia.jl")
```

**Scala:**
```bash
sbt "testOnly *CrossLanguageSpec"
```

### 3. Compare Results

```bash
python compare_results.py
```

## Tolerance Specification

| Metric Type | Absolute Tolerance | Relative Tolerance |
|-------------|-------------------|-------------------|
| Metric values (SNR, etc.) | 1e-6 | 1e-4 |
| Signal arrays | 1e-8 | 1e-6 |
| Iteration counts | 0 | 0 |

## Directory Structure

```
cross_language/
  generate_reference.py      # Generate reference data
  compare_results.py         # Compare outputs across languages
  reference/                 # Reference data files
  test_cross_language_python.py
  test_cross_language_r.R
  test_cross_language_julia.jl
  CrossLanguageSpec.scala
```
