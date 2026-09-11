# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# Promethium I/O Module

"""
Format-specific readers and writers for seismic data formats
including SEG-Y, miniSEED, SAC, and SEG-2.
"""

from promethium.io.readers import read_segy
from promethium.io.writers import write_segy
from promethium.io.formats import detect_format, get_reader, get_writer

__all__ = [
    "read_segy",
    "write_segy",
    "detect_format",
    "get_reader",
    "get_writer",
]
