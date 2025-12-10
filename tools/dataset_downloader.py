"""
Promethium Dataset Downloader

Utility for downloading and managing datasets from the Promethium registry.
Provides functions for listing, downloading, and verifying dataset integrity.

Usage:
    from promethium.tools.dataset_downloader import DatasetManager
    
    manager = DatasetManager()
    manager.list_datasets()
    manager.download("synthetic_marmousi", output_dir="data/")
"""
import hashlib
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Any

import yaml
import requests
from tqdm import tqdm


class DatasetManager:
    """Manager for downloading and organizing Promethium datasets."""
    
    REGISTRY_PATH = Path(__file__).parent.parent.parent.parent / "datasets" / "registry.yaml"
    
    def __init__(self, registry_path: Optional[Path] = None, cache_dir: Optional[Path] = None):
        """
        Initialize the dataset manager.
        
        Args:
            registry_path: Path to the registry YAML file. Defaults to built-in registry.
            cache_dir: Directory for caching downloads. Defaults to .promethium/cache.
        """
        self.registry_path = registry_path or self.REGISTRY_PATH
        self.cache_dir = cache_dir or Path.home() / ".promethium" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._registry: Optional[Dict] = None
    
    @property
    def registry(self) -> Dict:
        """Load and cache the dataset registry."""
        if self._registry is None:
            if self.registry_path.exists():
                with open(self.registry_path, "r") as f:
                    self._registry = yaml.safe_load(f)
            else:
                self._registry = {"datasets": {}, "config": {}}
        return self._registry
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """
        List all available datasets.
        
        Returns:
            List of dataset info dictionaries.
        """
        datasets = []
        for key, info in self.registry.get("datasets", {}).items():
            datasets.append({
                "id": key,
                "name": info.get("name", key),
                "description": info.get("description", ""),
                "format": info.get("format", "unknown"),
                "size": info.get("size", "unknown"),
                "license": info.get("license", "unknown"),
            })
        return datasets
    
    def get_info(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific dataset.
        
        Args:
            dataset_id: The dataset identifier.
            
        Returns:
            Dataset info dictionary or None if not found.
        """
        return self.registry.get("datasets", {}).get(dataset_id)
    
    def download(
        self,
        dataset_id: str,
        output_dir: Path,
        verify_checksum: bool = True,
        extract: bool = True,
        force: bool = False,
    ) -> Path:
        """
        Download a dataset from the registry.
        
        Args:
            dataset_id: The dataset identifier.
            output_dir: Directory to save the dataset.
            verify_checksum: Whether to verify SHA256 checksum if available.
            extract: Whether to extract compressed archives.
            force: Whether to re-download if already exists.
            
        Returns:
            Path to the downloaded/extracted dataset.
            
        Raises:
            ValueError: If dataset is not found in registry.
            RuntimeError: If download or verification fails.
        """
        info = self.get_info(dataset_id)
        if info is None:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        url = info.get("url", "")
        if not url or url == "placeholder":
            raise RuntimeError(f"Dataset URL not available for: {dataset_id}")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        dataset_dir = output_dir / dataset_id
        if dataset_dir.exists() and not force:
            print(f"Dataset already exists: {dataset_dir}")
            return dataset_dir
        
        # Download to cache first
        filename = url.split("/")[-1]
        cache_file = self.cache_dir / filename
        
        if not cache_file.exists() or force:
            print(f"Downloading {info.get('name', dataset_id)}...")
            self._download_file(url, cache_file)
        
        # Verify checksum
        checksum = info.get("checksum_sha256", "")
        if verify_checksum and checksum and checksum != "placeholder":
            if not self._verify_checksum(cache_file, checksum):
                raise RuntimeError(f"Checksum verification failed for {dataset_id}")
        
        # Extract or copy
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        if extract and cache_file.suffix in [".zip", ".tar", ".gz", ".tgz"]:
            print(f"Extracting to {dataset_dir}...")
            self._extract_archive(cache_file, dataset_dir)
        else:
            shutil.copy2(cache_file, dataset_dir / filename)
        
        print(f"Dataset ready: {dataset_dir}")
        return dataset_dir
    
    def _download_file(self, url: str, output_path: Path) -> None:
        """Download a file with progress bar."""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get("content-length", 0))
            
            with open(output_path, "wb") as f:
                with tqdm(total=total_size, unit="B", unit_scale=True, desc="Downloading") as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
                            
        except requests.RequestException as e:
            raise RuntimeError(f"Download failed: {e}")
    
    def _verify_checksum(self, file_path: Path, expected_sha256: str) -> bool:
        """Verify file checksum."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        
        actual = sha256_hash.hexdigest()
        return actual == expected_sha256
    
    def _extract_archive(self, archive_path: Path, output_dir: Path) -> None:
        """Extract a compressed archive."""
        if archive_path.suffix == ".zip":
            with zipfile.ZipFile(archive_path, "r") as zf:
                zf.extractall(output_dir)
        elif archive_path.suffix in [".tar", ".gz", ".tgz"]:
            import tarfile
            with tarfile.open(archive_path, "r:*") as tf:
                tf.extractall(output_dir)
        else:
            raise RuntimeError(f"Unsupported archive format: {archive_path.suffix}")


def list_datasets() -> List[Dict[str, Any]]:
    """List all available datasets."""
    return DatasetManager().list_datasets()


def download_dataset(
    dataset_id: str,
    output_dir: str = "data",
    verify: bool = True,
    extract: bool = True,
) -> Path:
    """
    Download a dataset from the registry.
    
    Args:
        dataset_id: The dataset identifier.
        output_dir: Directory to save the dataset.
        verify: Whether to verify checksum.
        extract: Whether to extract archives.
        
    Returns:
        Path to the dataset directory.
    """
    manager = DatasetManager()
    return manager.download(
        dataset_id,
        output_dir=Path(output_dir),
        verify_checksum=verify,
        extract=extract,
    )


if __name__ == "__main__":
    # Simple CLI for testing
    import sys
    
    manager = DatasetManager()
    
    if len(sys.argv) < 2:
        print("Usage: python dataset_downloader.py [list|info|download] [args...]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        for ds in manager.list_datasets():
            print(f"{ds['id']}: {ds['name']} ({ds['size']}) - {ds['license']}")
    
    elif command == "info" and len(sys.argv) > 2:
        info = manager.get_info(sys.argv[2])
        if info:
            for key, value in info.items():
                print(f"  {key}: {value}")
        else:
            print(f"Dataset not found: {sys.argv[2]}")
    
    elif command == "download" and len(sys.argv) > 2:
        output = sys.argv[3] if len(sys.argv) > 3 else "data"
        manager.download(sys.argv[2], Path(output))
    
    else:
        print("Unknown command or missing arguments")
