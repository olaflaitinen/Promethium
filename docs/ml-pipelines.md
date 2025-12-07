# Machine Learning Pipelines

Promethium integrates PyTorch for deep learning-based seismic processing.

## Models

### U-Net for Interpolation
Located in `src/promethium/ml/models.py`.
*   **Input**: 2D Seismic patches (regularly sampled, with zeros for missing traces).
*   **Architecture**: Encoder-Decoder with skip connections.
*   **Loss Function**: MSE + L1 (Composite loss).

### Physics-Informed Neural Networks (PINNs)
Located in `src/promethium/ml/pinns.py`.
*   **Concept**: Incorporates the Wave Equation directly into the loss function.
*   **Advantage**: Requires less training data; ensures physical consistency.
*   **Usage**: Best for velocity model building and wavefield reconstruction in complex media.

## Training Pipeline

1.  **Data Loading**: `SeismicTorchDataset` handles SEG-Y files, extracting 2D patches on-the-fly.
2.  **Augmentation**: Random noise injection, gain scaling, and trace killing (masking) simulating missing data.
3.  **Distributed Training**: `PromethiumLightningModule` wraps the models for multi-GPU training using PyTorch Lightning.

## Inference

Inference is handled by the `InferencePipeline` class:
1.  Loads model checkpoint.
2.  Segments input gather into overlapping patches.
3.  Predicts missing traces.
4.  Merges patches with tapering to avoid edge artifacts.
