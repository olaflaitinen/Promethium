# Language-Specific Guides

This directory contains language-specific documentation for Promethium implementations.

## Available Languages

| Language | Package | Guide |
|----------|---------|-------|
| [Python](python/) | `promethium-seismic` | Primary implementation |
| [R](r/) | `promethiumR` | Native R port |
| [Julia](julia/) | `Promethium.jl` | Native Julia port |
| [Scala](scala/) | `promethium-scala` | JVM implementation |

## Quick Comparison

### Installation

**Python:**
```bash
pip install promethium-seismic
```

**R:**
```r
# From source
devtools::install_github("olaflaitinen/Promethium/packages/promethiumR")
```

**Julia:**
```julia
using Pkg
Pkg.add(url="https://github.com/olaflaitinen/Promethium", subdir="packages/Promethium.jl")
```

**Scala:**
```scala
libraryDependencies += "io.promethium" %% "promethium-scala" % "1.0.4"
```

### Basic Usage

All languages follow the same conceptual workflow:

1. Load data into `SeismicDataset`
2. Create `RecoveryPipeline` with configuration
3. Run pipeline to get reconstructed data
4. Evaluate results with metrics

See language-specific guides for idiomatic examples.

## Choosing a Language

| Use Case | Recommended |
|----------|-------------|
| Rapid prototyping, ML research | Python |
| Statistical analysis, visualization | R |
| High-performance computing | Julia |
| Enterprise, Spark integration | Scala |

## Cross-Language Consistency

All implementations are validated against shared test vectors in `testdata/`.
Numerical results should match within documented tolerances.
