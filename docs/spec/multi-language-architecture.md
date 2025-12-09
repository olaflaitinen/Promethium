# Multi-Language Architecture Specification

This document defines the architecture for Promethium as a family of independent native implementations in Python, R, Julia, and Scala.

For the complete specification, see: [promethium_multilang_spec.md](../../packages/README.md)

## Overview

Promethium is implemented as **four independent native libraries** that share:
- Common mathematical foundation
- Identical algorithm pseudocode  
- Consistent data structures adapted to language idioms
- Unified evaluation metrics with cross-language numerical consistency

**Critical Principle**: No implementation calls another at runtime. Each is a first-class citizen in its ecosystem.

## Package Locations

| Language | Package | Path |
|----------|---------|------|
| Python | `promethium-seismic` | `src/promethium/` |
| R | `promethiumR` | `packages/promethiumR/` |
| Julia | `Promethium.jl` | `packages/Promethium.jl/` |
| Scala | `promethium-scala` | `packages/promethium-scala/` |

## Cross-Language Consistency

All implementations must pass identical test vectors with:
- Metric tolerance: 10^-8 relative error
- Signal tolerance: 10^-6 relative error

## Algorithm Reference

See [`docs/methodology.md`](../methodology.md) for mathematical formulations.
