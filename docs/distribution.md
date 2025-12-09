# Package Distribution Guide

This document describes how Promethium, a state-of-the-art (SoTA) seismic data recovery framework, is distributed across multiple language ecosystems.

## Overview

Promethium provides native implementations in four programming languages, each distributed through its respective package registry.

| Language | Package | Distribution | Status |
|----------|---------|--------------|--------|
| Python | `promethium-seismic` | PyPI | Production |
| R | `promethiumR` | CRAN | Pending |
| Julia | `Promethium.jl` | General Registry | Pending |
| Scala | `promethium-scala` | Maven Central | Pending |

---

## Python: PyPI Installation

The Python implementation is published on PyPI as `promethium-seismic`.

### Installation

```bash
pip install promethium-seismic==1.0.4
```

**PyPI Package:** [https://pypi.org/project/promethium-seismic/](https://pypi.org/project/promethium-seismic/)

### Optional Dependency Groups

| Group | Command | Purpose |
|-------|---------|---------|
| `dev` | `pip install promethium-seismic[dev]` | Development tools, testing |
| `viz` | `pip install promethium-seismic[viz]` | Visualization support |
| `server` | `pip install promethium-seismic[server]` | FastAPI, Celery, Redis |
| `all` | `pip install promethium-seismic[all]` | All optional dependencies |

### Development Installation (From Source)

```bash
git clone https://github.com/olaflaitinen/Promethium.git
cd Promethium
pip install -e ".[dev]"
```

---

## R: CRAN Publication

The R implementation targets CRAN as `promethiumR`.

### Target Installation

```r
install.packages("promethiumR")
library(promethiumR)
```

### Development Installation

```r
devtools::install("packages/promethiumR")
```

### CRAN Submission Process

1. **Package Preparation**
   - Ensure `DESCRIPTION` has correct metadata
   - Run `roxygen2::roxygenize()` to generate documentation
   - Verify `NAMESPACE` exports

2. **Quality Checks**
   ```r
   devtools::check()
   R CMD check --as-cran promethiumR_1.0.4.tar.gz
   ```

3. **Submission**
   - Use `devtools::release()` or submit manually via CRAN web form
   - Address any feedback from CRAN maintainers
   - Allow 2-10 business days for review

### Package Structure

```
packages/promethiumR/
├── DESCRIPTION
├── NAMESPACE
├── R/
│   ├── dataset.R
│   ├── metrics.R
│   ├── recovery.R
│   ├── signal.R
│   ├── io.R
│   └── pipeline.R
├── man/
└── tests/testthat/
```

---

## Julia: General Registry Registration

The Julia implementation targets the General registry as `Promethium`.

### Target Installation

```julia
using Pkg
Pkg.add("Promethium")
using Promethium
```

### Development Installation

```julia
using Pkg
Pkg.develop(path="packages/Promethium.jl")
```

### Registration Process

1. **Prepare Package**
   - Ensure `Project.toml` has correct UUID and version
   - All tests pass: `julia --project=. -e "using Pkg; Pkg.test()"`

2. **Create Release Tag**
   ```bash
   git tag v1.0.4
   git push origin v1.0.4
   ```

3. **Register with JuliaRegistrator**
   - Comment `@JuliaRegistrator register` on the release commit
   - Wait for automated checks to pass
   - Merge PR to General registry

### Package Structure

```
packages/Promethium.jl/
├── Project.toml
├── src/
│   ├── Promethium.jl
│   ├── types.jl
│   ├── metrics.jl
│   ├── recovery.jl
│   ├── signal.jl
│   ├── io.jl
│   └── pipeline.jl
└── test/runtests.jl
```

---

## Scala: Maven Central Publication

The Scala implementation is available on Maven Central with coordinates `io.github.olaflaitinen:promethium-scala`.

**Status: Published**

**Maven Central:** [https://central.sonatype.com/artifact/io.github.olaflaitinen/promethium-scala_2.13](https://central.sonatype.com/artifact/io.github.olaflaitinen/promethium-scala_2.13)

### Installation

**SBT:**
```scala
libraryDependencies += "io.github.olaflaitinen" %% "promethium-scala" % "1.0.4"
```

**Maven:**
```xml
<dependency>
    <groupId>io.github.olaflaitinen</groupId>
    <artifactId>promethium-scala_2.13</artifactId>
    <version>1.0.4</version>
</dependency>
```


### Development Installation

```bash
cd packages/promethium-scala
sbt publishLocal
```

### Publication Process

1. **Configure Sonatype Credentials**
   - Set up `~/.sbt/1.0/sonatype.sbt` with credentials
   - Ensure GPG key is configured for signing

2. **Publish**
   ```bash
   sbt +publishSigned
   sbt sonatypeRelease
   ```

3. **Verification**
   - Artifacts appear on Maven Central within 2-4 hours
   - Verify at `https://search.maven.org/`

### Package Structure

```
packages/promethium-scala/
├── build.sbt
├── project/
│   ├── build.properties
│   └── plugins.sbt
└── src/main/scala/io/promethium/
    ├── core/
    ├── evaluation/
    ├── recovery/
    ├── signal/
    └── io/
```

---

## Cross-Language Consistency

All implementations are validated against shared test vectors to ensure numerical consistency:

| Metric Type | Absolute Tolerance | Relative Tolerance |
|-------------|-------------------|-------------------|
| Metric values | 1e-6 | 1e-4 |
| Signal arrays | 1e-8 | 1e-6 |

Test data is stored in `testdata/` and `tests/cross_language/`.

---

## Version Synchronization

All language implementations share synchronized version numbers:

| Language | Package | Version |
|----------|---------|---------|
| Python | `promethium` | 1.0.4 |
| R | `promethiumR` | 1.0.4 |
| Julia | `Promethium.jl` | 1.0.4 |
| Scala | `promethium-scala` | 1.0.4 |

When updating versions, ensure all implementations are updated together.
