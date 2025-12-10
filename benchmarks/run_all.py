"""
Promethium Benchmark Runner

Executes benchmark configurations and aggregates results across
multiple pipelines and datasets for algorithm comparison.

Usage:
    python -m benchmarks.run_all configs/batch/classical_vs_ml.yaml
    
    or programmatically:
    
    from benchmarks.run_all import run_benchmark
    results = run_benchmark("configs/batch/classical_vs_ml.yaml")
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def load_benchmark_config(config_path: Path) -> Dict[str, Any]:
    """Load benchmark configuration from YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def run_single_pipeline(
    pipeline_config: Dict[str, Any],
    dataset_path: str,
    reference_path: Optional[str] = None,
    output_dir: Path = Path("results"),
) -> Dict[str, Any]:
    """
    Run a single pipeline and collect metrics.
    
    Args:
        pipeline_config: Pipeline configuration dictionary.
        dataset_path: Path to input dataset.
        reference_path: Optional path to reference data.
        output_dir: Directory for outputs.
        
    Returns:
        Dictionary with run results and metrics.
    """
    from promethium.io.readers import load_seismic_data
    from promethium.pipelines.recovery import SeismicRecoveryPipeline
    from promethium.evaluation.metrics import (
        signal_to_noise_ratio,
        mean_squared_error,
        structural_similarity_index,
    )
    import numpy as np
    
    pipeline_name = pipeline_config["name"]
    start_time = datetime.now()
    
    try:
        # Load data
        dataset = load_seismic_data(dataset_path)
        
        # Create and run pipeline
        pipe = SeismicRecoveryPipeline(pipeline_name, {
            "model": pipeline_config.get("config", {}),
        })
        
        reconstructed = pipe.run(dataset)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Compute metrics if reference available
        metrics = {}
        if reference_path and Path(reference_path).exists():
            reference = np.load(reference_path)
            recon_data = reconstructed.traces if hasattr(reconstructed, "traces") else np.array(reconstructed)
            
            metrics = {
                "snr": float(signal_to_noise_ratio(reference, recon_data)),
                "mse": float(mean_squared_error(reference, recon_data)),
                "ssim": float(structural_similarity_index(reference, recon_data)),
            }
        
        return {
            "pipeline": pipeline_name,
            "status": "success",
            "duration_seconds": duration,
            "metrics": metrics,
        }
        
    except Exception as e:
        return {
            "pipeline": pipeline_name,
            "status": "failed",
            "error": str(e),
            "metrics": {},
        }


def run_benchmark(
    config_path: str,
    output_dir: Optional[str] = None,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Run a complete benchmark suite.
    
    Args:
        config_path: Path to benchmark configuration file.
        output_dir: Optional output directory override.
        verbose: Whether to print progress.
        
    Returns:
        Benchmark results dictionary.
    """
    config_path = Path(config_path)
    config = load_benchmark_config(config_path)
    
    benchmark_name = config["benchmark"]["name"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if verbose:
        print(f"Running benchmark: {benchmark_name}")
        print("=" * 60)
    
    # Setup output directory
    output_base = Path(output_dir) if output_dir else Path(config["output"]["results_dir"])
    output_base.mkdir(parents=True, exist_ok=True)
    
    # Collect results
    all_results = []
    
    datasets = config.get("datasets", [])
    pipelines = config.get("pipelines", [])
    
    for dataset_info in datasets:
        dataset_id = dataset_info["id"]
        dataset_path = dataset_info["path"]
        reference_path = dataset_info.get("reference")
        
        if verbose:
            print(f"\nDataset: {dataset_id}")
            print("-" * 40)
        
        for pipeline_config in pipelines:
            pipeline_name = pipeline_config["name"]
            
            if verbose:
                print(f"  Running: {pipeline_name}...", end=" ")
            
            result = run_single_pipeline(
                pipeline_config,
                dataset_path,
                reference_path,
                output_base,
            )
            
            result["dataset"] = dataset_id
            result["timestamp"] = datetime.now().isoformat()
            
            all_results.append(result)
            
            if verbose:
                if result["status"] == "success":
                    metrics = result.get("metrics", {})
                    snr = metrics.get("snr", "N/A")
                    print(f"OK (SNR: {snr:.2f} dB)" if isinstance(snr, float) else "OK")
                else:
                    print(f"FAILED: {result.get('error', 'Unknown error')}")
    
    # Aggregate results
    summary = generate_summary(all_results, config)
    
    # Save results
    results_file = output_base / f"benchmark_{benchmark_name}_{timestamp}.json"
    with open(results_file, "w") as f:
        json.dump({
            "benchmark": benchmark_name,
            "timestamp": timestamp,
            "config_path": str(config_path),
            "summary": summary,
            "results": all_results,
        }, f, indent=2)
    
    if verbose:
        print(f"\nResults saved to: {results_file}")
    
    # Generate CSV
    if config["output"].get("save_csv", True):
        csv_file = output_base / f"benchmark_{benchmark_name}_{timestamp}.csv"
        save_results_csv(all_results, csv_file)
        if verbose:
            print(f"CSV saved to: {csv_file}")
    
    return {
        "benchmark": benchmark_name,
        "summary": summary,
        "results": all_results,
        "output_path": str(results_file),
    }


def generate_summary(results: List[Dict], config: Dict) -> Dict[str, Any]:
    """Generate summary statistics from results."""
    import statistics
    
    # Group by pipeline
    by_pipeline = {}
    for result in results:
        if result["status"] != "success":
            continue
        
        name = result["pipeline"]
        if name not in by_pipeline:
            by_pipeline[name] = {"metrics": {}}
        
        for metric, value in result.get("metrics", {}).items():
            if metric not in by_pipeline[name]["metrics"]:
                by_pipeline[name]["metrics"][metric] = []
            by_pipeline[name]["metrics"][metric].append(value)
    
    # Compute statistics
    summary = {}
    for pipeline, data in by_pipeline.items():
        summary[pipeline] = {}
        for metric, values in data["metrics"].items():
            if values:
                summary[pipeline][metric] = {
                    "mean": statistics.mean(values),
                    "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                    "min": min(values),
                    "max": max(values),
                }
    
    return summary


def save_results_csv(results: List[Dict], output_path: Path) -> None:
    """Save results to CSV format."""
    import csv
    
    if not results:
        return
    
    # Collect all metric keys
    all_metrics = set()
    for r in results:
        all_metrics.update(r.get("metrics", {}).keys())
    
    fieldnames = ["dataset", "pipeline", "status", "duration_seconds"] + sorted(all_metrics)
    
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            row = {
                "dataset": result.get("dataset", ""),
                "pipeline": result.get("pipeline", ""),
                "status": result.get("status", ""),
                "duration_seconds": result.get("duration_seconds", ""),
            }
            for metric in all_metrics:
                row[metric] = result.get("metrics", {}).get(metric, "")
            writer.writerow(row)


def print_comparison_table(summary: Dict[str, Any]) -> None:
    """Print a formatted comparison table."""
    try:
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        table = Table(title="Benchmark Results Summary")
        
        # Add columns
        table.add_column("Pipeline", style="cyan")
        
        # Get all metrics
        all_metrics = set()
        for data in summary.values():
            all_metrics.update(data.keys())
        
        for metric in sorted(all_metrics):
            table.add_column(metric.upper(), style="green")
        
        # Add rows
        for pipeline, metrics in summary.items():
            row = [pipeline]
            for metric in sorted(all_metrics):
                if metric in metrics:
                    val = metrics[metric]["mean"]
                    std = metrics[metric]["std"]
                    row.append(f"{val:.4f} +/- {std:.4f}")
                else:
                    row.append("N/A")
            table.add_row(*row)
        
        console.print(table)
        
    except ImportError:
        # Fallback without rich
        print("\nBenchmark Summary:")
        print("-" * 60)
        for pipeline, metrics in summary.items():
            print(f"\n{pipeline}:")
            for metric, stats in metrics.items():
                print(f"  {metric}: {stats['mean']:.4f} +/- {stats['std']:.4f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_all.py <benchmark_config.yaml>")
        print("\nExample:")
        print("  python run_all.py configs/batch/classical_vs_ml.yaml")
        sys.exit(1)
    
    config_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    results = run_benchmark(config_path, output_dir)
    
    print("\n" + "=" * 60)
    print_comparison_table(results["summary"])
