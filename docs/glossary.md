# Glossary

This document defines technical terms used throughout Promethium documentation.

## Seismic Terms

| Term | Definition |
|------|------------|
| **Trace** | A single recording of seismic amplitude versus time from one receiver |
| **Gather** | A collection of traces sharing a common property (CMP, shot, offset) |
| **CMP** | Common Mid-Point; location midway between source and receiver |
| **NMO** | Normal Moveout; time shift due to source-receiver offset |
| **Deconvolution** | Process to compress the seismic wavelet and improve resolution |
| **Migration** | Process to position reflections at true subsurface locations |
| **Amplitude** | Strength of the seismic signal at a given time sample |
| **Phase** | Timing relationship of the seismic wavelet |
| **Bandwidth** | Range of frequencies present in the seismic signal |
| **Sample Rate** | Number of samples recorded per second (Hz) |
| **SNR** | Signal-to-Noise Ratio; measure of signal quality |
| **AVO** | Amplitude Variation with Offset; analysis of amplitude changes |
| **Ground Roll** | Surface wave noise in land seismic data |
| **Multiple** | Unwanted reflection that bounces more than once |

## Data Formats

| Term | Definition |
|------|------------|
| **SEG-Y** | Industry standard format for seismic exchange |
| **miniSEED** | Seismological data format from IRIS/FDSN |
| **SAC** | Seismic Analysis Code format for single traces |
| **Header** | Metadata stored with each trace or file |

## ML/AI Terms

| Term | Definition |
|------|------------|
| **U-Net** | Encoder-decoder CNN with skip connections |
| **Autoencoder** | Neural network that learns compressed representations |
| **VAE** | Variational Autoencoder; probabilistic generative model |
| **GAN** | Generative Adversarial Network; adversarial training |
| **PINN** | Physics-Informed Neural Network; incorporates physics |
| **Inference** | Using a trained model to make predictions |
| **Training** | Process of optimizing model parameters |
| **Epoch** | One complete pass through training data |
| **Batch** | Subset of data processed together |
| **Loss Function** | Metric measuring prediction error |
| **SSIM** | Structural Similarity Index; perceptual quality metric |
| **MSE** | Mean Squared Error; average squared difference |

## System Terms

| Term | Definition |
|------|------------|
| **API** | Application Programming Interface |
| **REST** | Representational State Transfer; API architecture |
| **JWT** | JSON Web Token; authentication token |
| **Worker** | Background process executing tasks |
| **Queue** | List of pending tasks awaiting execution |
| **Pipeline** | Sequence of processing steps |

## Promethium-Specific Terms

| Term | Definition |
|------|------------|
| **Dataset** | Uploaded seismic data file with metadata |
| **Job** | Processing task submitted by user |
| **Model** | Trained ML model in the registry |
| **Result** | Output from a completed job |
| **Reconstruction** | Process of estimating missing data |
| **Denoising** | Process of reducing noise in data |

---

## Related Documents

| Document | Description |
|----------|-------------|
| [Overview](overview.md) | Project overview |
| [ML Pipelines](ml-pipelines.md) | ML documentation |
