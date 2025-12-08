# Promethium I/O Module

"""
Format-specific readers and writers for seismic data formats
including SEG-Y, miniSEED, SAC, and SEG-2.
"""

from promethium.io.segy import read_segy, write_segy
from promethium.io.formats import detect_format, get_reader, get_writer

__all__ = [
    "read_segy",
    "write_segy",
    "detect_format",
    "get_reader",
    "get_writer",
]
