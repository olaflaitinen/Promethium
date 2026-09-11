# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import torch

from promethium_seismic.core.config import get_settings
from promethium_seismic.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


if TYPE_CHECKING:
    from promethium_seismic.ml.train import PromethiumModule


class InferenceEngine:
    """
    Batched, Patch-based Inference Engine.
    Handles:
    - Loading large volumes
    - Sliding window extraction
    - Batched GPU inference
    - Window blending (Cosine weighted)
    - Reassembly
    """

    def __init__(
        self, model=None, model_path: str | None = None, device: str | None = None
    ):
        """Build an engine around a model.

        Args:
            model: An already loaded model. Use this when the caller has one
                in hand, which is the common case from Python.
            model_path: A checkpoint to load instead. Use this from a script
                or the command line.
            device: Where to run. Defaults to the configured device, and
                resolves "auto" to cuda when one is present.

        Raises:
            ValueError: if neither a model nor a path is given.

        This used to take a model_path, ignore it, and build a fresh
        untrained U-Net from a config marked "Mock", so a caller passing a
        trained checkpoint got random weights and no warning.
        """
        if model is None and model_path is None:
            raise ValueError("pass either a model or a model_path")

        resolved = device or settings.DEFAULT_DEVICE
        if resolved == "auto":
            resolved = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = resolved

        if model is None:
            from promethium_seismic.ml.train import PromethiumModule

            # model_path is not None here: the constructor refuses to be
            # built with neither a model nor a path.
            assert model_path is not None
            model = PromethiumModule.load_from_checkpoint(
                model_path, map_location=self.device
            )

        self.model = model
        self.model.to(self.device)
        self.model.eval()
        self.config = getattr(model, "config", {})

    @torch.no_grad()
    def reconstruct_array(
        self,
        data: np.ndarray,
        patch_size: int = 128,
        overlap: float = 0.25,
        batch_size: int = 8,
    ) -> np.ndarray:
        """Reconstruct an array in memory, tile by tile.

        Args:
            data: A two dimensional gather.
            patch_size: Side of the square window the model sees.
            overlap: Fraction of a window that overlaps the next one. The
                blend weights are a cosine taper, so overlapping windows
                cross fade instead of leaving seams.
            batch_size: Windows per forward pass.

        Returns:
            The reconstruction, the same shape as the input.

        Raises:
            ValueError: if the input is not two dimensional, or is smaller
                than one window.
        """
        values = np.asarray(getattr(data, "values", data), dtype=np.float32)
        if values.ndim != 2:
            raise ValueError(f"expected a 2D gather, got shape {values.shape}")

        n_traces, n_time = values.shape
        if n_traces < patch_size or n_time < patch_size:
            raise ValueError(
                f"the gather is {values.shape} and the window is "
                f"{patch_size}: reduce patch_size to fit"
            )

        stride = max(1, int(patch_size * (1 - overlap)))

        output = np.zeros_like(values)
        weights = np.zeros_like(values)

        # A cosine taper in each direction, so that overlapping windows sum
        # to roughly one and the seams do not show.
        taper = np.sin(np.pi * np.arange(0.5, patch_size + 0.5) / patch_size)
        window = np.outer(taper, taper)

        patches: list[np.ndarray] = []
        coords: list[tuple[int, int]] = []

        for t in range(0, n_traces - patch_size + 1, stride):
            for s in range(0, n_time - patch_size + 1, stride):
                patches.append(values[t : t + patch_size, s : s + patch_size])
                coords.append((t, s))

                if len(patches) == batch_size:
                    self._process_batch(patches, coords, output, weights, window)
                    patches = []
                    coords = []

        if patches:
            self._process_batch(patches, coords, output, weights, window)

        # Where no window landed, keep the input rather than dividing by a
        # weight of zero and returning noise.
        covered = weights > 1e-8
        result = values.copy()
        result[covered] = output[covered] / weights[covered]
        return result

    def run(
        self,
        input_path: str,
        output_path: str,
        patch_size: int = 128,
        overlap: float = 0.25,
        batch_size: int = 8,
    ) -> np.ndarray:
        """Reconstruct a file and write the result.

        Args:
            input_path: A Zarr store to read.
            output_path: Where to write the reconstruction, as .npy.
            patch_size: Side of the square window the model sees.
            overlap: Fraction of a window that overlaps the next one.
            batch_size: Windows per forward pass.

        Returns:
            The reconstruction, so a caller does not have to read back what
            it just wrote.

        Raises:
            ValueError: if the input is not a Zarr store.

        This used to compute the reconstruction and then return None without
        writing anything, under a log line saying "Saving results...".
        """
        source = Path(input_path)
        target = Path(output_path)

        logger.info(f"Starting inference on {source}")

        if source.suffix != ".zarr":
            raise ValueError(
                f"Unsupported format {source.suffix}. Convert to Zarr first."
            )

        # Imported here so that the ml extra does not drag in the io extra:
        # this is the only line in the module that reads a store.
        from promethium_seismic.io.zarr_wrapper import load_zarr

        # load_zarr returns an xarray DataArray; reconstruct_array takes
        # the values off it either way, and the annotation should say what
        # is passed rather than what is accepted.
        data = np.asarray(load_zarr(source))
        result = self.reconstruct_array(
            data, patch_size=patch_size, overlap=overlap, batch_size=batch_size
        )

        target.parent.mkdir(parents=True, exist_ok=True)
        np.save(target, result)
        logger.info(f"Inference complete, wrote {target}")
        return result

    def _process_batch(self, patches, coords, output, weights, window):
        """Run one batch of windows and accumulate them into the output."""
        batch = np.array(patches)  # B, H, W
        batch = torch.from_numpy(batch).unsqueeze(1).float().to(self.device)

        pred = self.model(batch)
        pred = pred.cpu().numpy()[:, 0, :, :]

        for i, (t, s) in enumerate(coords):
            h, w = pred[i].shape
            output[t : t + h, s : s + w] += pred[i] * window
            weights[t : t + h, s : s + w] += window


def load_model(path: str, device: str | None = None) -> "PromethiumModule":
    """
    Load a pre-trained model from a checkpoint.

    Args:
        path: Path to the .ckpt file or model directory.
        device: Device to load model on (e.g., 'cuda', 'cpu').

    Returns:
        Loaded PromethiumModule in eval mode.
    """
    from promethium_seismic.ml.train import PromethiumModule

    if device is None:
        device = settings.DEFAULT_DEVICE

    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        # Assuming path is a checkpoint file
        model = PromethiumModule.load_from_checkpoint(path, map_location=device)
        model.to(device)
        model.eval()
        model.freeze()
        return model
    except Exception as e:
        logger.error(f"Failed to load model from {path}: {e}")
        raise


def reconstruct(
    data: np.ndarray,
    model: "PromethiumModule",
    device: str | None = None,
    patch_size: tuple[int, int] = (128, 128),
    overlap: float = 0.25,
) -> np.ndarray:
    """
    High-level convenience function for reconstruction.

    Args:
        data: Input seismic data (2D array).
        model: Loaded PromethiumModule.
        device: Computation advice.
        patch_size: Size of sliding window.
        overlap: Overlap fraction.

    Returns:
        Reconstructed numpy array.
    """
    window = patch_size[0] if isinstance(patch_size, tuple) else patch_size
    engine = InferenceEngine(model=model, device=device)
    return engine.reconstruct_array(data, patch_size=window, overlap=overlap)
