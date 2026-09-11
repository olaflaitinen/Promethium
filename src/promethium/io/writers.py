# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import segyio
import numpy as np
import xarray as xr
from pathlib import Path
from typing import Union

from promethium.core.exceptions import DataIngestionError
from promethium.core.logging import get_logger

logger = get_logger(__name__)

def write_segy(
    file_path: Union[str, Path], 
    data: xr.DataArray,
    sample_rate: float = 2.0,
    format: int = 1
) -> None:
    """
    Writes an xarray DataArray to a SEG-Y file.
    
    Args:
        file_path: Output file path.
        data: DataArray with dims ('trace', 'time').
        sample_rate: Sample rate in ms.
        format: SEG-Y format code (1=IBM float, 5=IEEE float).
    """
    path = Path(file_path)
    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    n_traces, n_samples = data.shape
    
    spec = segyio.spec()
    spec.tracecount = n_traces
    spec.samples = range(n_samples)
    spec.format = format
    
    try:
        with segyio.create(str(path), spec) as f:
            # Write traces
            f.trace = data.values
            f.bin = segyio.create.bin(spec)
            
            # Simple header writing if needed
            # for i in range(n_traces):
            #     f.header[i] = {segyio.TraceField.TRACE_SEQUENCE_LINE: i + 1}
                
        logger.info(f"Written SEG-Y: {path}")
        
    except Exception as e:
        logger.error(f"Failed to write SEG-Y {path}: {e}")
        raise DataIngestionError(f"Failed to write SEG-Y: {e}") from e
