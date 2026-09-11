# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# Promethium Utils Module

"""
Utility functions for reproducibility, data generation, and visualization.
"""

# Only the numpy based helpers are imported eagerly. Seeding and device
# selection need torch, and plotting needs matplotlib; both are resolved on
# first use so that importing promethium_seismic.utils costs nothing.
from promethium_seismic.utils.synthetic import add_noise, generate_synthetic_traces

_LAZY = {
    "set_seed": ("promethium_seismic.utils.reproducibility", "ml"),
    "get_device": ("promethium_seismic.utils.reproducibility", "ml"),
    "plot_traces": ("promethium_seismic.utils.visualization", "viz"),
    "plot_comparison": ("promethium_seismic.utils.visualization", "viz"),
}


def __getattr__(name: str):
    """Resolve a helper that needs an optional dependency.

    Args:
        name: The attribute being looked up.

    Returns:
        The object from the module that defines it.

    Raises:
        ImportError: when the extra that provides it is not installed.
        AttributeError: when the name is not part of this package.
    """
    entry = _LAZY.get(name)
    if entry is None:
        raise AttributeError(
            f"module 'promethium_seismic.utils' has no attribute '{name}'"
        )

    module_name, extra = entry
    import importlib

    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise ImportError(
            f"promethium_seismic.utils.{name} needs the '{extra}' extra, which is "
            f"not installed. Install it with:\n\n"
            f"    pip install 'promethium-seismic[{extra}]'"
        ) from exc

    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list:
    """List the public surface, including names not yet imported."""
    return sorted(set(globals()) | set(_LAZY))


__all__ = [
    "set_seed",
    "get_device",
    "generate_synthetic_traces",
    "add_noise",
    "plot_traces",
    "plot_comparison",
]
