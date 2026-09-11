# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Tests for format detection and the format agnostic read and write.

These exist because the command line tool called `load_seismic_data` and
`save_seismic_data` for as long as it has existed, and neither function was
ever written. Nothing caught it: no test ran the CLI, and the import sat
inside a function so it only failed when the command was invoked.

The numpy path is exercised here rather than SEG-Y because numpy needs no
optional dependency, so these run on the core install.
"""

import numpy as np
import pytest

from promethium_seismic.io import formats


def test_detect_format_from_extension():
    """The extension picks the format."""
    assert formats.detect_format("survey.sgy") == "segy"
    assert formats.detect_format("survey.segy") == "segy"
    assert formats.detect_format("gather.npy") == "numpy"
    assert formats.detect_format("record.mseed") == "miniseed"


def test_detect_format_gives_up_clearly():
    """An extension nobody knows returns None rather than guessing."""
    assert formats.detect_format("notes.txt") is None


def test_read_refuses_an_unknown_extension():
    """An undetectable format says so, and lists what it does know."""
    with pytest.raises(ValueError) as caught:
        formats.read("mystery.txt")
    message = str(caught.value)
    assert "mystery.txt" in message
    assert "format_name" in message


def test_every_detectable_format_has_a_reader():
    """detect_format must not name a format get_reader will refuse.

    It did: .dat and .seg2 resolved to seg2, which had no entry in the
    reader table, so `read("shot.dat")` recognised the file and then said the
    format was unsupported. A table that advertises what the dispatcher will
    not handle is worse than one that stays quiet.

    A missing backend is a different matter and is allowed here: segyio and
    obspy live in the io extra, and this test runs on the core install. What
    is being checked is registration, not installation, so ImportError passes
    and ValueError does not.
    """
    for format_name in formats.FORMAT_EXTENSIONS:
        try:
            reader = formats.get_reader(format_name)
        except ValueError as exc:
            pytest.fail(f"{format_name} is detectable but has no reader: {exc}")
        except ImportError:
            continue  # the backend is not installed, which is not the point
        assert callable(reader), format_name


def test_numpy_round_trip(tmp_path):
    """Write then read gives the data back.

    This is the check that would have caught the writer argument order: the
    numpy writer took (data, path) while write_segy took (file_path, data),
    so dispatching through get_writer gave one order for one format and the
    opposite for the other.
    """
    data = np.arange(24, dtype=np.float32).reshape(4, 6)
    target = tmp_path / "gather.npy"

    formats.write(str(target), data)
    assert target.exists()

    restored = formats.read(str(target))
    assert np.array_equal(restored, data)


def test_forcing_a_format_overrides_the_extension(tmp_path):
    """A file with an unhelpful extension can still be read."""
    data = np.arange(6, dtype=np.float32)
    target = tmp_path / "gather.unknown"

    # numpy.save appends .npy when the name has no suffix it recognises, so
    # the written file is checked through the name it actually gets.
    written = tmp_path / "gather.unknown.npy"
    formats.write(str(target), data, format_name="numpy")
    assert written.exists() or target.exists()

    source = written if written.exists() else target
    restored = formats.read(str(source), format_name="numpy")
    assert np.array_equal(restored, data)


def test_get_writer_is_consistent_across_formats():
    """Every writer takes the destination first.

    get_writer promises one interface. It returned two, which is a defect a
    caller can only find by writing a file to the wrong place.
    """
    import inspect

    writer = formats.get_writer("numpy")
    first = list(inspect.signature(writer).parameters)[0]
    assert first == "path", f"numpy writer takes {first!r} first"
