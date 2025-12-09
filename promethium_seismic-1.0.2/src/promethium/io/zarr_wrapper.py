import zarr
import numpy as np
import xarray as xr
from pathlib import Path
from typing import Union, Tuple

from promethium.core.logging import get_logger
from promethium.core.config import get_settings
from promethium.io.readers import read_segy

logger = get_logger(__name__)
settings = get_settings()

def convert_to_zarr(
    source_path: Union[str, Path],
    output_name: str,
    chunk_size: Tuple[int, int] = (1024, 1024)
) -> Path:
    """
    Converts a SEG-Y file to Zarr format for high-performance random access.
    
    Args:
        source_path: Input SEG-Y file.
        output_name: Name of the output Zarr store (without extension).
        chunk_size: Zarr chunk encoding (trace, time).

    Returns:
        Path: Absolute path to the created .zarr directory.
    """
    source = Path(source_path)
    output_dir = settings.DATA_STORAGE_PATH / f"{output_name}.zarr"
    
    logger.info(f"Converting {source.name} to Zarr at {output_dir}")
    
    # 1. Read Data (Lazy if possible, but currently eager via readers.py)
    # TODO: Make readers.py yield chunks for generic large file support
    da = read_segy(source)
    
    # 2. Re-chunking strategy
    # Seismic data is accessed:
    # - By trace (vertical)
    # - By time slice (horizontal)
    # - By rectangular patch (ML training)
    # Square-ish chunks (e.g. 1024x1024) offer balanced performance.
    
    ds = da.to_dataset()
    ds = ds.chunk({"trace": chunk_size[0], "time": chunk_size[1]})
    
    # 3. Write via xarray zarr backend
    compressor = zarr.Blosc(cname="zstd", clevel=3, shuffle=2)
    encoding = {
        "amplitude": {"compressor": compressor}
    }
    
    ds.to_zarr(output_dir, mode="w", encoding=encoding, consolidated=True)
    
    logger.info(f"Conversion complete: {output_dir}")
    return output_dir

def load_zarr(path: Union[str, Path]) -> xr.DataArray:
    """Load a Seismic Zarr dataset."""
    ds = xr.open_zarr(path, consolidated=True)
    return ds["amplitude"]
