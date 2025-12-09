# Promethium Multi-Language Packages

This directory contains native implementations of Promethium in multiple programming languages.

## Package Overview

| Language | Package | Path | Status |
|----------|---------|------|--------|
| **Python** | `promethium-seismic` | `../src/promethium/` | Production |
| **R** | `promethiumR` | `promethiumR/` | Scaffold |
| **Julia** | `Promethium.jl` | `Promethium.jl/` | Scaffold |
| **Scala** | `promethium-scala` | `promethium-scala/` | Scaffold |

## Design Principles

1. **Independent Native Implementations**: Each language implements algorithms directly from the shared specification. No runtime inter-language calls.

2. **Cross-Language Consistency**: All implementations produce numerically identical results (within tolerance) for the same inputs.

3. **Idiomatic APIs**: Each implementation uses language-native idioms while maintaining conceptual consistency.

## Shared Specification

See [docs/spec/multi-language-architecture.md](../docs/spec/multi-language-architecture.md) for the complete specification.

## Quick Start

### R
```r
# Install (when published to CRAN)
install.packages("promethiumR")

# Or from source
devtools::install("packages/promethiumR")

library(promethiumR)
ds <- SeismicDataset(matrix(rnorm(1000), 10, 100), dt = 0.004)
```

### Julia
```julia
# Add package (when registered)
using Pkg
Pkg.add("Promethium")

using Promethium
ds = SeismicDataset(randn(100, 500), 0.004)
```

### Scala
```scala
// Add to build.sbt
libraryDependencies += "io.promethium" %% "promethium-scala" % "1.0.4"

import io.promethium.core._
val ds = SeismicDataset.fromArray(data, dt = 0.004)
```

## Testing Cross-Language Consistency

All implementations are validated against shared test vectors in `testdata/`:

```bash
# Python
pytest tests/cross_language/

# R
Rscript -e "testthat::test_dir('packages/promethiumR/tests')"

# Julia
julia --project=packages/Promethium.jl -e "using Pkg; Pkg.test()"

# Scala
cd packages/promethium-scala && sbt test
```
