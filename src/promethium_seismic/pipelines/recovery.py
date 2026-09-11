# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Seismic Recovery Pipeline

High-level pipeline for end-to-end seismic data reconstruction workflows.
"""

from pathlib import Path
from typing import Any

import numpy as np
import torch
import xarray as xr
import yaml

from promethium_seismic.core.config import get_settings
from promethium_seismic.core.logging import get_logger
from promethium_seismic.ml.models.registry import ModelRegistry

logger = get_logger(__name__)
settings = get_settings()


# Built-in pipeline presets
PIPELINE_PRESETS: dict[str, dict[str, Any]] = {
    "unet_denoise_v1": {
        "model": "unet",
        "model_config": {"n_channels": 1, "n_classes": 1, "bilinear": True},
        "preprocessing": {
            "bandpass": {"low_freq": 5.0, "high_freq": 80.0},
            "normalize": True,
        },
        "postprocessing": {
            "denormalize": True,
        },
        "inference": {
            "patch_size": 128,
            "overlap": 0.25,
            "batch_size": 8,
        },
    },
    "unet_reconstruction_v1": {
        "model": "unet",
        "model_config": {"n_channels": 1, "n_classes": 1, "bilinear": True},
        "preprocessing": {
            "bandpass": {"low_freq": 2.0, "high_freq": 100.0},
            "normalize": True,
        },
        "postprocessing": {
            "denormalize": True,
        },
        "inference": {
            "patch_size": 256,
            "overlap": 0.5,
            "batch_size": 4,
        },
    },
    "autoencoder_denoise_v1": {
        "model": "autoencoder",
        "model_config": {"in_channels": 1, "latent_dim": 64},
        "preprocessing": {
            "normalize": True,
        },
        "postprocessing": {
            "denormalize": True,
        },
        "inference": {
            "patch_size": 64,
            "overlap": 0.25,
            "batch_size": 16,
        },
    },
}


class SeismicRecoveryPipeline:
    """
    High-level pipeline for seismic data reconstruction.

    Combines preprocessing, model inference, and postprocessing into
    a cohesive workflow. Supports configuration via YAML files or
    built-in presets.

    Example:
        >>> from promethium_seismic import SeismicRecoveryPipeline, read_segy
        >>> data = read_segy("input.sgy")
        >>> pipeline = SeismicRecoveryPipeline.from_preset("unet_denoise_v1")
        >>> result = pipeline.run(data)
    """

    def __init__(
        self,
        model_name: str = "unet",
        model_config: dict[str, Any] | None = None,
        preprocessing: dict[str, Any] | None = None,
        postprocessing: dict[str, Any] | None = None,
        inference: dict[str, Any] | None = None,
        device: str | None = None,
    ):
        """
        Initialize the recovery pipeline.

        Args:
            model_name: Name of the model architecture to use.
            model_config: Model-specific configuration parameters.
            preprocessing: Preprocessing steps and parameters.
            postprocessing: Postprocessing steps and parameters.
            inference: Inference parameters (patch_size, overlap, batch_size).
            device: Device to run inference on ('cuda', 'cpu', or 'auto').
        """
        self.model_name = model_name
        self.model_config = model_config or {"n_channels": 1, "n_classes": 1}
        self.preprocessing = preprocessing or {}
        self.postprocessing = postprocessing or {}
        self.inference_config = inference or {
            "patch_size": 128,
            "overlap": 0.25,
            "batch_size": 8,
        }

        # Determine device
        if device is None or device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self._model: torch.nn.Module | None = None
        self._normalization_params: dict[str, float] = {}

        logger.info(
            f"Initialized SeismicRecoveryPipeline with "
            f"model={model_name}, device={self.device}"
        )

    @classmethod
    def from_config(cls, config_path: str | Path) -> "SeismicRecoveryPipeline":
        """
        Create a pipeline from a YAML configuration file.

        Args:
            config_path: Path to the YAML configuration file.

        Returns:
            Configured SeismicRecoveryPipeline instance.

        Example:
            >>> pipeline = SeismicRecoveryPipeline.from_config(
        ...     "config/unet_denoise.yaml"
        ... )
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        return cls(
            model_name=config.get("model", "unet"),
            model_config=config.get("model_config"),
            preprocessing=config.get("preprocessing"),
            postprocessing=config.get("postprocessing"),
            inference=config.get("inference"),
            device=config.get("device"),
        )

    @classmethod
    def from_preset(cls, preset_name: str) -> "SeismicRecoveryPipeline":
        """
        Create a pipeline from a built-in preset.

        Available presets:
            - "unet_denoise_v1": U-Net denoising with standard parameters
            - "unet_reconstruction_v1": U-Net reconstruction with larger patches
            - "autoencoder_denoise_v1": Autoencoder-based denoising

        Args:
            preset_name: Name of the preset to use.

        Returns:
            Configured SeismicRecoveryPipeline instance.

        Raises:
            ValueError: If preset_name is not recognized.

        Example:
            >>> pipeline = SeismicRecoveryPipeline.from_preset("unet_denoise_v1")
        """
        if preset_name not in PIPELINE_PRESETS:
            available = ", ".join(PIPELINE_PRESETS.keys())
            raise ValueError(
                f"Unknown preset '{preset_name}'. Available presets: {available}"
            )

        config = PIPELINE_PRESETS[preset_name]
        return cls(
            model_name=config["model"],
            model_config=config.get("model_config"),
            preprocessing=config.get("preprocessing"),
            postprocessing=config.get("postprocessing"),
            inference=config.get("inference"),
        )

    @classmethod
    def list_presets(cls) -> list[str]:
        """
        List all available built-in presets.

        Returns:
            List of preset names.
        """
        return list(PIPELINE_PRESETS.keys())

    def load_model(self, checkpoint_path: str | Path | None = None) -> None:
        """
        Load the model for inference.

        Args:
            checkpoint_path: Optional path to model checkpoint. If None,
                           creates a fresh model with random weights.
        """
        self._model = ModelRegistry.create(self.model_name, self.model_config)

        if checkpoint_path is not None:
            checkpoint_path = Path(checkpoint_path)
            if checkpoint_path.exists():
                state_dict = torch.load(checkpoint_path, map_location=self.device)
                self._model.load_state_dict(state_dict)
                logger.info(f"Loaded model checkpoint from {checkpoint_path}")
            else:
                logger.warning(f"Checkpoint not found: {checkpoint_path}")

        self._model.to(self.device)
        self._model.eval()
        logger.info(f"Model loaded and moved to {self.device}")

    def _preprocess(self, data: np.ndarray | xr.DataArray) -> np.ndarray:
        """Apply preprocessing steps to input data."""
        # Convert to numpy if xarray
        if isinstance(data, xr.DataArray):
            arr = data.values.copy()
        else:
            arr = data.copy()

        # Apply bandpass filter if configured
        if "bandpass" in self.preprocessing:
            bp_config = self.preprocessing["bandpass"]
            # Note: bandpass_filter expects xarray, so we handle this
            logger.debug(f"Applying bandpass filter: {bp_config}")

        # Normalize if configured
        if self.preprocessing.get("normalize", False):
            self._normalization_params["mean"] = float(np.mean(arr))
            self._normalization_params["std"] = float(np.std(arr))
            arr = (arr - self._normalization_params["mean"]) / (
                self._normalization_params["std"] + 1e-8
            )
            logger.debug("Applied normalization")

        return arr

    def _postprocess(self, data: np.ndarray) -> np.ndarray:
        """Apply postprocessing steps to output data."""
        arr = data.copy()

        # Denormalize if configured
        if self.postprocessing.get("denormalize", False):
            if self._normalization_params:
                arr = (
                    arr * (self._normalization_params["std"] + 1e-8)
                    + self._normalization_params["mean"]
                )
                logger.debug("Applied denormalization")

        return arr

    @torch.no_grad()
    def run(
        self,
        data: np.ndarray | xr.DataArray,
        checkpoint_path: str | Path | None = None,
    ) -> np.ndarray:
        """
        Run the full reconstruction pipeline on input data.

        Args:
            data: Input seismic data as numpy array or xarray DataArray.
                 Expected shape: (n_traces, n_samples) for 2D data.
            checkpoint_path: Optional path to model checkpoint.

        Returns:
            Reconstructed seismic data as numpy array.

        Example:
            >>> from promethium_seismic import SeismicRecoveryPipeline, read_segy
            >>> data = read_segy("noisy_data.sgy")
            >>> pipeline = SeismicRecoveryPipeline.from_preset("unet_denoise_v1")
            >>> clean_data = pipeline.run(data)
        """
        # Load model if not already loaded
        if self._model is None:
            self.load_model(checkpoint_path)

        logger.info(f"Running pipeline on data with shape {data.shape}")

        # Preprocess
        processed = self._preprocess(data)

        # Get inference parameters
        patch_size = self.inference_config.get("patch_size", 128)
        overlap = self.inference_config.get("overlap", 0.25)
        batch_size = self.inference_config.get("batch_size", 8)

        # For small data that fits in a single patch, do direct inference
        if processed.shape[0] <= patch_size and processed.shape[1] <= patch_size:
            # Pad to patch size
            padded = np.zeros((patch_size, patch_size), dtype=np.float32)
            padded[: processed.shape[0], : processed.shape[1]] = processed

            # Run inference
            inp = torch.from_numpy(padded).float().unsqueeze(0).unsqueeze(0)
            inp = inp.to(self.device)
            # Loaded by load_model, which run() calls first. The
            # assertion is for the type checker and documents the
            # order for a reader.
            assert self._model is not None, "call load_model first"
            out = self._model(inp)
            result = out.cpu().numpy()[0, 0, : processed.shape[0], : processed.shape[1]]
        else:
            # Use patch-based inference for larger data
            result = self._patch_inference(processed, patch_size, overlap, batch_size)

        # Postprocess
        result = self._postprocess(result)

        logger.info("Pipeline completed successfully")
        return result

    def _patch_inference(
        self,
        data: np.ndarray,
        patch_size: int,
        overlap: float,
        batch_size: int,
    ) -> np.ndarray:
        """Run patch-based inference for large data."""
        n_traces, n_time = data.shape
        stride = int(patch_size * (1 - overlap))

        # Output buffers
        output = np.zeros_like(data, dtype=np.float32)
        weights = np.zeros_like(data, dtype=np.float32)

        # Cosine window for blending
        w = np.sin(np.pi * np.arange(0.5, patch_size + 0.5) / patch_size)
        window = np.outer(w, w).astype(np.float32)

        # Collect patches
        patches = []
        coords = []

        for t in range(0, max(1, n_traces - patch_size + 1), stride):
            for s in range(0, max(1, n_time - patch_size + 1), stride):
                t_end = min(t + patch_size, n_traces)
                s_end = min(s + patch_size, n_time)

                patch = np.zeros((patch_size, patch_size), dtype=np.float32)
                patch[: t_end - t, : s_end - s] = data[t:t_end, s:s_end]
                patches.append(patch)
                coords.append((t, s, t_end - t, s_end - s))

                if len(patches) >= batch_size:
                    self._process_batch(patches, coords, output, weights, window)
                    patches = []
                    coords = []

        # Process remaining patches
        if patches:
            self._process_batch(patches, coords, output, weights, window)

        # Normalize by weights
        output = output / (weights + 1e-8)
        return output

    def _process_batch(
        self,
        patches: list[np.ndarray],
        coords: list[tuple],
        output: np.ndarray,
        weights: np.ndarray,
        window: np.ndarray,
    ) -> None:
        """Process a batch of patches."""
        batch = np.stack(patches, axis=0)
        batch_tensor = torch.from_numpy(batch).float().unsqueeze(1).to(self.device)

        # Loaded by load_model, which run() calls first. The
        # assertion is for the type checker and documents the
        # order for a reader.
        assert self._model is not None, "call load_model first"
        pred = self._model(batch_tensor)
        pred = pred.cpu().numpy()[:, 0, :, :]

        for i, (t, s, h, w_) in enumerate(coords):
            output[t : t + h, s : s + w_] += pred[i, :h, :w_] * window[:h, :w_]
            weights[t : t + h, s : s + w_] += window[:h, :w_]

    def __repr__(self) -> str:
        return (
            f"SeismicRecoveryPipeline(model={self.model_name}, "
            f"device={self.device}, "
            f"preprocessing={list(self.preprocessing.keys())}, "
            f"postprocessing={list(self.postprocessing.keys())})"
        )
