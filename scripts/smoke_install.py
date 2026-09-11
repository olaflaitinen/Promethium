# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Acceptance test for a built wheel, run against the installed package.

This is deliberately not part of the pytest suite. The suite runs against the
source tree with every extra present, which is exactly the situation that
hides packaging defects: a missing __init__.py, a module left out of the
distribution, or a core import that quietly needs an extra.

This runs against a wheel installed into an environment that has the core
dependencies and nothing else, so it fails on the things the suite cannot
see.

    pip install dist/*.whl
    python scripts/smoke_install.py
"""

import sys

import promethium_seismic as p


def main() -> int:
    """Check that the installed package is usable.

    Returns:
        0 when every check passes.

    Raises:
        AssertionError: on the first check that does not hold.
    """
    print("version:", p.__version__)

    assert p.__license__ == "MPL-2.0", p.__license__
    print("licence:", p.__license__)

    traces, meta = p.generate_synthetic_traces(n_traces=4, n_samples=32)
    assert traces.shape == (4, 32), traces.shape
    print("synthetic:", traces.shape, "at", meta["sample_rate"], "Hz")

    snr = p.signal_to_noise_ratio([1.0, 2.0], [1.0, 2.1])
    assert snr > 0.0
    print("snr:", round(snr, 3))

    ssim = p.structural_similarity_index(traces, traces)
    assert abs(ssim - 1.0) < 1e-12, ssim
    print("ssim of a gather against itself:", round(ssim, 6))

    # The core install is numpy and scipy. If importing the package reaches
    # torch then the install is two gigabytes whatever the table says.
    assert "torch" not in sys.modules, "the core install pulled torch"
    print("torch not pulled by the core install")

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
