# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Tests for the patch based inference path.

`reconstruct` is one of the package's public names and it could not work
under any arguments. It built `InferenceEngine(model, device=..., patch_size=
..., overlap=...)`, a constructor that takes neither of those keywords, then
called `run(data)` where run takes a path to read and a path to write. Nothing
caught it because no test ever called it.

These tests need the ml extra and skip cleanly without it.
"""

import numpy as np
import pytest

torch = pytest.importorskip(
    "torch",
    reason="these tests need the ml extra: pip install 'promethium-seismic[ml]'",
)

from promethium_seismic.ml.inference import InferenceEngine  # noqa: E402
from promethium_seismic.ml.models import UNet  # noqa: E402


@pytest.fixture
def model():
    """A small untrained U-Net. The arithmetic is what is under test."""
    return UNet(n_channels=1, n_classes=1)


@pytest.fixture
def gather():
    """A synthetic gather large enough for several windows."""
    rng = np.random.default_rng(20260911)
    return rng.standard_normal((96, 96)).astype(np.float32)


def test_engine_needs_a_model_or_a_path():
    """Neither given is an error, not a silently untrained model.

    The constructor used to accept a checkpoint path, ignore it, and build a
    fresh untrained network from a hardcoded config marked "Mock", so a
    caller passing a trained model got random weights and no warning.
    """
    with pytest.raises(ValueError):
        InferenceEngine()


def test_reconstruct_array_returns_the_input_shape(model, gather):
    """The reconstruction covers the gather it was given."""
    engine = InferenceEngine(model=model, device="cpu")
    result = engine.reconstruct_array(gather, patch_size=32, overlap=0.25)

    assert isinstance(result, np.ndarray)
    assert result.shape == gather.shape
    assert np.isfinite(result).all()


def test_reconstruct_array_refuses_a_gather_smaller_than_the_window(model):
    """A window that cannot fit is an error with the sizes in it."""
    engine = InferenceEngine(model=model, device="cpu")
    with pytest.raises(ValueError) as caught:
        engine.reconstruct_array(np.zeros((8, 8), dtype=np.float32), patch_size=32)
    assert "32" in str(caught.value)


def test_reconstruct_array_refuses_the_wrong_rank(model):
    """A three dimensional volume is not a gather."""
    engine = InferenceEngine(model=model, device="cpu")
    with pytest.raises(ValueError):
        engine.reconstruct_array(np.zeros((4, 8, 8), dtype=np.float32))


def test_uncovered_samples_keep_the_input(model):
    """Where no window lands, the input survives.

    With a stride that does not divide the gather, the last rows and columns
    are never inside a window. Dividing by a weight of zero there would
    return noise; the input is kept instead.
    """
    engine = InferenceEngine(model=model, device="cpu")
    data = np.ones((70, 70), dtype=np.float32)
    result = engine.reconstruct_array(data, patch_size=32, overlap=0.0)

    assert np.isfinite(result).all()
    # The far corner is outside every window at this stride.
    assert result[-1, -1] == pytest.approx(1.0)


def test_public_reconstruct_runs(model, gather):
    """The module level convenience works, which it never has."""
    from promethium_seismic.ml.inference import reconstruct

    result = reconstruct(gather, model, device="cpu", patch_size=(32, 32))
    assert result.shape == gather.shape
    assert np.isfinite(result).all()


def test_run_writes_what_it_computes(model, gather, tmp_path, monkeypatch):
    """run must write its output, not log that it did.

    It used to compute the reconstruction, log "Inference complete. Saving
    results..." and return None, leaving output_path untouched.
    """
    pytest.importorskip(
        "zarr",
        reason="reading a store needs the io extra: "
        "pip install 'promethium-seismic[io]'",
    )

    import promethium_seismic.ml.inference as inference

    store = tmp_path / "input.zarr"
    store.mkdir()
    target = tmp_path / "out" / "rebuilt.npy"

    monkeypatch.setattr(
        "promethium_seismic.io.zarr_wrapper.load_zarr",
        lambda path: gather,
        raising=False,
    )

    engine = inference.InferenceEngine(model=model, device="cpu")
    result = engine.run(str(store), str(target), patch_size=32)

    assert target.exists(), "run did not write its output"
    written = np.load(target)
    assert written.shape == gather.shape
    assert np.array_equal(written, result)
