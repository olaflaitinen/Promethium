# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Tests for the core of the library: what importing it costs, and settings.

This file used to assert that numpy, scipy, torch, fastapi, pydantic and
sqlalchemy could be imported. Those tests pass or fail on what happens to be
installed and say nothing about Promethium, and three of them tested the web
application that is no longer here. Two more caught ImportError and called
`pytest.skip`, so a module that stopped importing reported a skip rather than
a failure, which is the one outcome nobody reads.

What is worth asserting is the boundary this package promises: the core
imports on numpy and scipy alone, and anything heavier says which extra it
needs rather than raising a name the caller has never heard of.
"""

import importlib
import importlib.util
import subprocess
import sys

import numpy as np
import pytest

import promethium_seismic


def test_importing_the_package_does_not_pull_torch():
    """The core install is numpy and scipy, and the import must respect it.

    torch is over two gigabytes. If importing the package drags it in then
    `pip install promethium-seismic` costs two gigabytes whatever the
    dependency table says.

    This runs in a fresh interpreter rather than in the current one. The
    first version skipped whenever another test had already imported torch,
    which in a normal run is always, so the check never actually ran.
    """
    probe = (
        "import sys; import promethium_seismic; "
        "sys.exit(1 if 'torch' in sys.modules else 0)"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "importing promethium_seismic loaded torch, so the core install is "
        f"not the core install. {result.stderr.strip()}"
    )


def test_version_and_licence_are_declared():
    """The package states what it is."""
    assert promethium_seismic.__version__
    assert promethium_seismic.__license__ == "MPL-2.0"


def test_light_entry_points_resolve():
    """Everything the core install promises is reachable without an extra."""
    for name in (
        "generate_synthetic_traces",
        "add_noise",
        "bandpass_filter",
        "signal_to_noise_ratio",
        "mean_squared_error",
        "structural_similarity_index",
    ):
        assert callable(getattr(promethium_seismic, name)), name


def test_a_missing_extra_names_itself():
    """A feature behind an extra says which extra, not which module.

    The failure this prevents is a ModuleNotFoundError for segyio reaching a
    user who has never heard of segyio and cannot know it belongs to the io
    extra.
    """
    if importlib.util.find_spec("segyio") is not None:
        pytest.skip("the io extra is installed, so there is no error to read")

    with pytest.raises(ImportError) as caught:
        promethium_seismic.read_segy

    message = str(caught.value)
    assert "io" in message
    assert "pip install" in message


def test_unknown_attribute_is_an_attribute_error():
    """A name outside the public surface fails as a missing attribute."""
    with pytest.raises(AttributeError):
        promethium_seismic.no_such_function


def test_settings_load_and_are_cached():
    """Configuration resolves with no file and no environment set."""
    from promethium_seismic.core.config import get_settings

    settings = get_settings()
    assert settings is not None
    assert get_settings() is settings


def test_logger_carries_the_usual_levels():
    """A named logger comes back and can be written to."""
    from promethium_seismic.core.logging import get_logger

    logger = get_logger("promethium_seismic.test")
    assert logger is not None
    for level in ("info", "warning", "error"):
        assert hasattr(logger, level), level


def test_synthetic_data_is_usable_as_a_fixture():
    """The synthetic generator produces finite data of the size asked for.

    It returns the traces and the metadata that describes them, so a caller
    keeps the sample rate that goes with the array rather than having to
    remember it separately.
    """
    traces, metadata = promethium_seismic.generate_synthetic_traces(
        n_traces=8, n_samples=64, seed=20260911
    )
    assert isinstance(traces, np.ndarray)
    assert sorted(traces.shape) == [8, 64]
    assert np.isfinite(traces).all()

    assert metadata["n_traces"] == 8
    assert metadata["n_samples"] == 64
    assert metadata["sample_rate"] > 0


def test_synthetic_data_is_reproducible_from_a_seed():
    """The same seed gives the same traces, so a test built on it is stable."""
    first, _ = promethium_seismic.generate_synthetic_traces(
        n_traces=4, n_samples=32, seed=7
    )
    second, _ = promethium_seismic.generate_synthetic_traces(
        n_traces=4, n_samples=32, seed=7
    )
    other, _ = promethium_seismic.generate_synthetic_traces(
        n_traces=4, n_samples=32, seed=8
    )

    assert np.array_equal(first, second)
    assert not np.array_equal(first, other)
