# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import segyio
import numpy as np
import xarray as xr
from pathlib import Path
from typing import Union, Optional, Dict, Any

from promethium.core.exceptions import DataIngestionError
from promethium.core.logging import get_logger

logger = get_logger(__name__)

def read_segy(
    file_path: Union[str, Path], 
    strict: bool = False,
    ignore_geometry: bool = True
) -> xr.DataArray:
    """
    Reads a SEG-Y file into an xarray DataArray.
    
    Args:
        file_path: Path to the .sgy file.
        strict: If True, enforces strict SEG-Y standards.
        ignore_geometry: If True, ignores 3D geometry map (faster for raw trace access).

    Returns:
        xr.DataArray: The seismic volume with coordinates.
    """
    path = Path(file_path)
    if not path.exists():
        raise DataIngestionError(f"File not found: {path}")

    try:
        with segyio.open(str(path), ignore_geometry=ignore_geometry, strict=strict) as f:
            # Efficiently read all traces
            # For very large files, this might need to be chunked or memory-mapped handled differently
            # But segyio + numpy is usually fine for <10GB if strictly reading.
            # Ideally we stream to Zarr immediately.
            
            # Metadata
            n_traces = f.tracecount
            n_samples = f.samples.size
            sample_rate = segyio.tools.dt(f) / 1000.0
            t_start = f.samples[0]
            
            # Load Data (Memory Mapped if possible via segyio internal)
            # data = f.trace.raw[:] produces a copy.
            # optimization: use mmap kwarg in open if supported or rely on OS paging
            data = f.trace.raw[:] 

            # Construct Coordinates
            # If 2D: (trace, time)
            # If 3D: we would need inline/crossline headers. 
            # For generic "raw" reading, (trace, time) is safest foundation.
            
            coords = {
                "trace": np.arange(n_traces),
                "time": f.samples
            }
            
            da = xr.DataArray(
                data,
                dims=("trace", "time"),
                coords=coords,
                name="amplitude",
                attrs={
                    "sample_rate": sample_rate,
                    "filepath": str(path),
                    "ns": n_samples,
                    "nt": n_traces
                }
            )
            
            logger.info(f"Loaded SEG-Y: {path.name} | Shape: {da.shape}")
            return da

    except Exception as e:
        logger.error(f"Failed to read SEG-Y {path}: {e}")
        raise DataIngestionError(f"Corrupt or unreadable SEG-Y: {e}") from e
