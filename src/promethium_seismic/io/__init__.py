# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Reading and writing seismic data.

`read` and `write` choose the format from the file extension and are the
entry points most callers want. The format specific functions are there for
when the extension lies or a backend option is needed.

Only the format machinery is imported eagerly. It is pure standard library
and dispatches to a backend on demand, so `read("gather.npy")` works on the
core install. The SEG-Y functions need segyio, which belongs to the io
extra, so they are resolved on first use and say so when it is absent.
Importing them at module load made the numpy path require segyio too, which
is how a numpy round trip ended up needing a SEG-Y library.
"""

from promethium_seismic.io.formats import (
    detect_format,
    get_reader,
    get_writer,
    read,
    write,
)

_LAZY = {
    "read_segy": "promethium_seismic.io.readers",
    "write_segy": "promethium_seismic.io.writers",
}


def __getattr__(name: str):
    """Resolve a SEG-Y entry point on first use.

    Args:
        name: The attribute being looked up.

    Returns:
        The function from the module that defines it.

    Raises:
        ImportError: when the io extra is not installed.
        AttributeError: when the name is not part of this package.
    """
    module_name = _LAZY.get(name)
    if module_name is None:
        raise AttributeError(
            f"module 'promethium_seismic.io' has no attribute '{name}'"
        )

    import importlib

    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise ImportError(
            f"promethium_seismic.io.{name} needs the 'io' extra, which is "
            f"not installed. Install it with:\n\n"
            f"    pip install 'promethium-seismic[io]'"
        ) from exc

    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list:
    """List the public surface, including names not yet imported."""
    return sorted(set(globals()) | set(_LAZY))


__all__ = [
    "read",
    "write",
    "read_segy",
    "write_segy",
    "detect_format",
    "get_reader",
    "get_writer",
]
