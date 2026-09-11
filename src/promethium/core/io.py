# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import segyio
import numpy as np
from pathlib import Path
from typing import Union, Optional
from .models import SeismicDataset, SeismicGather, SeismicTrace
from .exceptions import DataIngestionError
from .logging import logger

def read_segy(file_path: Union[str, Path], strict: bool = False) -> SeismicDataset:
    """
    Reads a SEG-Y file and returns a SeismicDataset.
    
    Args:
        file_path: Path to the SEG-Y file.
        strict: If True, enforce strict mode in segyio.
    
    Returns:
        SeismicDataset instance.
        
    Raises:
        DataIngestionError: If the file cannot be read.
    """
    file_path = str(file_path)
    try:
        # Open with segyio
        # Using ignore_geometry=True is safer for general loading unless 3D structure is guaranteed
        with segyio.open(file_path, ignore_geometry=True, strict=strict) as f:
            # Load traces into memory (for now - optimize for large files later)
            data = f.trace.raw[:]
            
            # Extract headers (basic example)
            n_traces = f.tracecount
            sample_rate = segyio.tools.dt(f) / 1000.0 # Convert to ms if needed, check units
            
            # Simple metadata extraction
            metadata = {
                "n_traces": n_traces,
                "n_samples": f.samples.size,
                "sample_rate": sample_rate,
                "text_header": segyio.tools.wrap(f.text[0]) if f.text else ""
            }
            
            # We can construct an xarray for the dataset
            import xarray as xr
            da = xr.DataArray(
                data,
                dims=("trace", "time"),
                coords={
                    "trace": np.arange(n_traces),
                    "time": f.samples
                },
                name="amplitude",
                attrs=metadata
            )
            
            return SeismicDataset(data=da, metadata=metadata)
            
    except Exception as e:
        logger.error(f"Failed to read SEG-Y file {file_path}: {e}")
        raise DataIngestionError(f"Failed to read SEG-Y file: {e}") from e

def read_miniseed(file_path: Union[str, Path]) -> SeismicDataset:
    """
    Reads a miniSEED file using Obspy.
    """
    import obspy
    try:
        st = obspy.read(str(file_path))
        # Convert stream to SeismicDataset logic...
        # For now, simplistic conversion merging all traces if they share time axis
        # Implementation to be refined.
        
        # Placeholder return
        return SeismicDataset(data=st, metadata={"source": "miniseed"})
    except Exception as e:
        logger.error(f"Failed to read miniSEED file {file_path}: {e}")
        raise DataIngestionError(f"Failed to read miniSEED file: {e}") from e
