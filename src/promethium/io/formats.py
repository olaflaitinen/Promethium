# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Format detection and dynamic reader/writer selection for seismic data files.
"""

import os
from pathlib import Path
from typing import Callable, Optional, Dict, Any

# Format extension mappings
FORMAT_EXTENSIONS = {
    'segy': ['.sgy', '.segy', '.seg-y'],
    'miniseed': ['.mseed', '.miniseed'],
    'sac': ['.sac'],
    'seg2': ['.seg2', '.dat'],
    'numpy': ['.npy', '.npz'],
}


def detect_format(path: str) -> Optional[str]:
    """
    Detect the seismic data format based on file extension.
    
    Args:
        path: Path to the seismic data file.
        
    Returns:
        Format name string ('segy', 'miniseed', 'sac', etc.) or None if unknown.
        
    Example:
        >>> detect_format('survey.sgy')
        'segy'
        >>> detect_format('record.mseed')
        'miniseed'
    """
    ext = Path(path).suffix.lower()
    
    for format_name, extensions in FORMAT_EXTENSIONS.items():
        if ext in extensions:
            return format_name
            
    return None


def get_reader(format_name: str) -> Callable:
    """
    Get the appropriate reader function for a given format.
    
    Args:
        format_name: Format name ('segy', 'miniseed', 'sac', etc.)
        
    Returns:
        Reader function that accepts a file path and returns data.
        
    Raises:
        ValueError: If format is not supported.
        
    Example:
        >>> reader = get_reader('segy')
        >>> data = reader('survey.sgy')
    """
    readers = {
        'segy': _get_segy_reader,
        'miniseed': _get_miniseed_reader,
        'sac': _get_sac_reader,
        'numpy': _get_numpy_reader,
    }
    
    if format_name not in readers:
        raise ValueError(f"Unsupported format: {format_name}. Supported: {list(readers.keys())}")
        
    return readers[format_name]()


def get_writer(format_name: str) -> Callable:
    """
    Get the appropriate writer function for a given format.
    
    Args:
        format_name: Format name ('segy', 'numpy', etc.)
        
    Returns:
        Writer function that accepts data and a file path.
        
    Raises:
        ValueError: If format is not supported for writing.
        
    Example:
        >>> writer = get_writer('segy')
        >>> writer(data, 'output.sgy')
    """
    writers = {
        'segy': _get_segy_writer,
        'numpy': _get_numpy_writer,
    }
    
    if format_name not in writers:
        raise ValueError(f"Unsupported format for writing: {format_name}. Supported: {list(writers.keys())}")
        
    return writers[format_name]()


def _get_segy_reader():
    """Return SEG-Y reader function."""
    from promethium.io.readers import read_segy
    return read_segy


def _get_miniseed_reader():
    """Return miniSEED reader function."""
    def read_miniseed(path: str, **kwargs):
        from obspy import read as obspy_read
        import numpy as np
        import xarray as xr
        
        stream = obspy_read(path, **kwargs)
        traces = [tr.data for tr in stream]
        data = np.array(traces, dtype=np.float32)
        
        sample_rate = stream[0].stats.sampling_rate
        n_samples = data.shape[1] if data.ndim > 1 else len(data)
        times = np.arange(n_samples) / sample_rate
        
        return xr.DataArray(
            data,
            dims=("trace", "time"),
            coords={"trace": np.arange(len(traces)), "time": times},
            attrs={"sample_rate": sample_rate, "format": "miniseed"},
        )
    
    return read_miniseed


def _get_sac_reader():
    """Return SAC reader function."""
    def read_sac(path: str, **kwargs):
        from obspy import read as obspy_read
        import numpy as np
        import xarray as xr
        
        stream = obspy_read(path, format="SAC", **kwargs)
        traces = [tr.data for tr in stream]
        data = np.array(traces, dtype=np.float32)
        
        sample_rate = stream[0].stats.sampling_rate
        n_samples = data.shape[1] if data.ndim > 1 else len(data)
        times = np.arange(n_samples) / sample_rate
        
        return xr.DataArray(
            data,
            dims=("trace", "time"),
            coords={"trace": np.arange(len(traces)), "time": times},
            attrs={"sample_rate": sample_rate, "format": "sac"},
        )
    
    return read_sac


def _get_numpy_reader():
    """Return NumPy reader function."""
    def read_numpy(path: str, **kwargs):
        import numpy as np
        return np.load(path, **kwargs)
    
    return read_numpy


def _get_segy_writer():
    """Return SEG-Y writer function."""
    from promethium.io.writers import write_segy
    return write_segy


def _get_numpy_writer():
    """Return NumPy writer function."""
    def write_numpy(data, path: str, **kwargs):
        import numpy as np
        np.save(path, data, **kwargs)
    
    return write_numpy
