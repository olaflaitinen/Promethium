# Algorithms Reference

This section documents the mathematical foundations and algorithms implemented in Promethium.

## Contents

- [Classical Signal Processing](classical_signal_processing.md)
- [Matrix Completion](matrix_completion.md)
- [Compressive Sensing](compressive_sensing.md)
- [Deep Learning Models](deep_learning.md)
- [Physics-Informed Neural Networks](pinns.md)

## Algorithm Categories

### Classical Signal Processing

Traditional signal processing methods adapted for seismic data:

| Algorithm | Purpose | Reference |
|-----------|---------|-----------|
| Wiener Filter | Frequency-domain denoising | Wiener (1949) |
| LMS Adaptive | Time-varying noise removal | Widrow & Hoff (1960) |
| Deconvolution | Wavelet recovery | Robinson (1967) |
| STFT | Time-frequency analysis | Allen (1977) |

### Inverse Problems

Optimization-based methods for missing data recovery:

| Algorithm | Problem | Regularization |
|-----------|---------|----------------|
| ISTA | Matrix completion | Nuclear norm |
| FISTA | Sparse recovery | L1 norm |
| ADMM | General inverse | Mixed |

### Deep Learning

Neural network architectures for seismic reconstruction:

| Model | Architecture | Application |
|-------|--------------|-------------|
| U-Net | Encoder-decoder with skip | Interpolation, denoising |
| Autoencoder | Bottleneck compression | Denoising |
| GAN | Generator + discriminator | High-fidelity reconstruction |
| PINN | NN + PDE constraints | Physics-constrained recovery |

## Cross-Language Implementation

All algorithms are implemented natively in each language following the shared specification. See the [Multi-Language Architecture](../spec/multi-language-architecture.md) for implementation details.
