# Mathematical Methodology and Models

This document details the mathematical foundations and model architectures used in the Promethium library.

## 1. Evaluation Metrics

### Signal-to-Noise Ratio (SNR)

The Signal-to-Noise Ratio measures the ratio of signal power to noise power, expressed in decibels (dB).

$$
\mathrm{SNR}_{\mathrm{dB}} = 10 \log_{10} \left( \frac{P_{\text{signal}}}{P_{\text{noise}}} \right)
$$

Where power \(P\) is calculated as the mean squared amplitude:
$$
P_{\text{signal}} = \frac{1}{N} \sum_{i=1}^{N} y_i^2,
\qquad
P_{\text{noise}} = \frac{1}{N} \sum_{i=1}^{N} (y_i - \hat{y}_i)^2
$$

### Structural Similarity Index (SSIM)

SSIM measures the perceived quality of the reconstructed signal by comparing luminance, contrast, and structure.

$$
\mathrm{SSIM}(x, y) =
\frac{(2\mu_x\mu_y + C_1)(2\sigma_{xy} + C_2)}
{(\mu_x^2 + \mu_y^2 + C_1)(\sigma_x^2 + \sigma_y^2 + C_2)}
$$

Where:

- \(\mu_x, \mu_y\): Local means of \(x\) and \(y\).
- \(\sigma_x^2, \sigma_y^2\): Local variances.
- \(\sigma_{xy}\): Local covariance.
- \(C_1, C_2\): Constants to stabilize division.

---

## 2. Signal Processing Transforms

### Fast Fourier Transform (FFT)

We use the Discrete Fourier Transform (DFT) to analyze the frequency content of seismic traces.

$$
X_k = \sum_{n=0}^{N-1} x_n \, e^{-i 2\pi k n / N}
$$

### Continuous Wavelet Transform (CWT)

Decomposes a signal into wavelets, which are localized in both time and frequency.

$$
W(a, b) = \frac{1}{\sqrt{a}}
\int_{-\infty}^{\infty}
x(t)\,
\psi^*\!\left(\frac{t-b}{a}\right)\, dt
$$

Where:

- \(\psi\): Mother wavelet (e.g., Morlet).
- \(a\): Scale parameter (related to frequency).
- \(b\): Translation parameter (time shift).

---

## 3. Reconstruction Algorithms

### Compressive Sensing (ISTA)

We employ the Iterative Shrinkage–Thresholding Algorithm (ISTA) to recover missing seismic data by exploiting sparsity in a transform domain (e.g., DCT or Curvelet).

**Optimization Objective:**

$$
\min_x \;
\frac{1}{2} \,\|y - \Phi x\|_2^2
\;+\;
\lambda \,\|\Psi x\|_1
$$

Where:

- \(y\): Observed data (with missing traces).
- \(\Phi\): Sampling operator (masking).
- \(\Psi\): Sparsifying transform.
- \(\lambda\): Regularization parameter.

**Update Rule:**

$$
x_{k+1}
=
\mathcal{S}_{\lambda \alpha}
\Bigl(
x_k + \alpha \,\Phi^\top (y - \Phi x_k)
\Bigr)
$$

Where \(\mathcal{S}\) is the soft-thresholding operator:

$$
\mathcal{S}_{\tau}(u)
=
\operatorname{sign}(u)\,
\max\bigl(|u| - \tau,\, 0\bigr)
$$

---

## 4. Deep Learning Architectures

### U-Net (Seismic Denoising & Recovery)

The U-Net is a fully convolutional network with an encoder–decoder structure and skip connections. It is highly effective for image-to-image tasks like seismic data restoration.

**Architecture:**

1. **Encoder (Contracting Path)**  
   - Sequence of `Conv2D` \(\rightarrow\) `BatchNorm` \(\rightarrow\) `LeakyReLU`  
   - Max pooling for downsampling  
   - Captures context and high-level features  

2. **Decoder (Expansive Path)**  
   - `UpSample` (bilinear or transpose convolution)  
   - Concatenation with corresponding encoder feature maps (skip connections)  
   - Recovers spatial resolution  

3. **Output**  
   - \(1\times 1\) convolution to map features to the output space (e.g., denoised amplitude)

**Loss Function:**

We typically use Mean Squared Error (MSE) or L1 loss for signal reconstruction:

$$
\mathcal{L}_{\text{MSE}}
=
\frac{1}{N}
\sum_{i=1}^{N}
\left\|
y_i^{\text{true}} - y_i^{\text{pred}}
\right\|^2
$$

For perceptual quality, we may combine this with an adversarial loss (GAN) or a perceptual loss (e.g., VGG-based).

### Spectral Loss

To ensure frequency content is preserved during reconstruction, we employ a spectral loss term:

$$
\mathcal{L}_{\text{total}}
=
\mathcal{L}_{\text{MSE}}
+
\alpha \,\mathcal{L}_{\text{spectral}}
$$

Where:

$$
\mathcal{L}_{\text{spectral}}
=
\left\|
\,\bigl|\mathcal{F}(y)\bigr|
-
\bigl|\mathcal{F}(\hat{y})\bigr|
\right\|^2
$$

and \(\mathcal{F}\) denotes the Fourier transform (magnitude). This penalizes blurriness and helps recover high-frequency geologic features.
