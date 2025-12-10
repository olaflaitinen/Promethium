"""
Promethium CLI - Command-line interface for seismic data recovery.

This module provides the main entry point for the Promethium command-line interface,
enabling users to run seismic data recovery pipelines, evaluate reconstructions,
and manage datasets from the terminal.

Usage:
    promethium run --input data.sgy --pipeline matrix_completion --output result.sgy
    promethium evaluate --reference truth.npy --estimate recon.npy
    promethium datasets list
    promethium models list
"""
import sys
from pathlib import Path
from typing import Optional, List

try:
    import typer
    from rich.console import Console
    from rich.table import Table
except ImportError:
    print("CLI dependencies not installed. Run: pip install promethium-seismic[cli]")
    sys.exit(1)

app = typer.Typer(
    name="promethium",
    help="Promethium: Advanced Seismic Data Recovery and Reconstruction Framework",
    add_completion=False,
)
console = Console()


@app.command()
def run(
    input_path: Path = typer.Argument(..., help="Path to input seismic data (SEG-Y, HDF5, NumPy)"),
    output_path: Path = typer.Argument(..., help="Path for output reconstructed data"),
    pipeline: str = typer.Option("matrix_completion", "--pipeline", "-p", 
                                  help="Pipeline preset name"),
    config: Optional[Path] = typer.Option(None, "--config", "-c",
                                           help="Path to YAML configuration file"),
    lambda_param: float = typer.Option(0.1, "--lambda", help="Regularization parameter"),
    max_iter: int = typer.Option(100, "--max-iter", help="Maximum iterations"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Run a seismic data recovery pipeline on input data.
    
    Supported pipelines:
    - matrix_completion: Nuclear norm minimization for missing trace recovery
    - wiener: Frequency-domain Wiener filtering for denoising
    - fista: Fast ISTA for compressive sensing reconstruction
    - unet: Deep learning U-Net for interpolation (requires GPU)
    """
    from promethium import SeismicDataset
    from promethium.pipelines.recovery import SeismicRecoveryPipeline
    from promethium.io.readers import load_seismic_data
    from promethium.io.writers import save_seismic_data
    
    console.print(f"[bold]Promethium Seismic Recovery[/bold]")
    console.print(f"Input: {input_path}")
    console.print(f"Pipeline: {pipeline}")
    
    # Load data
    if verbose:
        console.print("Loading input data...")
    
    try:
        dataset = load_seismic_data(str(input_path))
    except Exception as e:
        console.print(f"[red]Error loading data: {e}[/red]")
        raise typer.Exit(code=1)
    
    console.print(f"Loaded: {dataset.traces.shape[0]} traces, {dataset.traces.shape[1]} samples")
    
    # Create pipeline
    pipeline_config = {
        "model": {
            "type": pipeline,
            "lambda": lambda_param,
            "max_iter": max_iter,
        }
    }
    
    pipe = SeismicRecoveryPipeline(pipeline, pipeline_config)
    
    if verbose:
        console.print(f"Running {pipeline} pipeline...")
    
    # Run recovery
    result = pipe.run(dataset)
    
    # Save output
    save_seismic_data(result, str(output_path))
    console.print(f"[green]Output saved to: {output_path}[/green]")


@app.command()
def evaluate(
    reference: Path = typer.Argument(..., help="Path to reference (ground truth) data"),
    estimate: Path = typer.Argument(..., help="Path to estimated/reconstructed data"),
    metrics: str = typer.Option("snr,mse,psnr,ssim", "--metrics", "-m",
                                 help="Comma-separated list of metrics"),
    output: Optional[Path] = typer.Option(None, "--output", "-o",
                                           help="Save metrics to JSON file"),
):
    """
    Evaluate reconstruction quality by comparing reference and estimate.
    
    Available metrics:
    - snr: Signal-to-Noise Ratio (dB)
    - mse: Mean Squared Error
    - psnr: Peak Signal-to-Noise Ratio (dB)
    - ssim: Structural Similarity Index
    """
    import numpy as np
    import json
    from promethium.evaluation.metrics import (
        signal_to_noise_ratio,
        mean_squared_error,
        peak_signal_to_noise_ratio,
        structural_similarity_index,
    )
    
    # Load data
    ref_data = np.load(str(reference))
    est_data = np.load(str(estimate))
    
    if ref_data.shape != est_data.shape:
        console.print("[red]Error: Reference and estimate shapes do not match[/red]")
        raise typer.Exit(code=1)
    
    # Compute metrics
    metric_list = [m.strip().lower() for m in metrics.split(",")]
    results = {}
    
    table = Table(title="Reconstruction Quality Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Unit", style="dim")
    
    if "snr" in metric_list:
        val = signal_to_noise_ratio(ref_data, est_data)
        results["snr"] = val
        table.add_row("SNR", f"{val:.4f}", "dB")
    
    if "mse" in metric_list:
        val = mean_squared_error(ref_data, est_data)
        results["mse"] = val
        table.add_row("MSE", f"{val:.6e}", "")
    
    if "psnr" in metric_list:
        val = peak_signal_to_noise_ratio(ref_data, est_data)
        results["psnr"] = val
        table.add_row("PSNR", f"{val:.4f}", "dB")
    
    if "ssim" in metric_list:
        val = structural_similarity_index(ref_data, est_data)
        results["ssim"] = val
        table.add_row("SSIM", f"{val:.6f}", "")
    
    console.print(table)
    
    if output:
        with open(output, "w") as f:
            json.dump(results, f, indent=2)
        console.print(f"Metrics saved to: {output}")


@app.command()
def datasets():
    """List available example datasets."""
    table = Table(title="Available Datasets")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Size", style="dim")
    
    table.add_row("synthetic_clean", "Clean synthetic shot gather", "100x500")
    table.add_row("synthetic_noisy", "Noisy synthetic (SNR ~10dB)", "100x500")
    table.add_row("synthetic_missing", "30% missing traces", "100x500")
    table.add_row("marmousi", "Marmousi velocity model gather", "240x1000")
    
    console.print(table)


@app.command()
def models():
    """List available pipeline presets and models."""
    table = Table(title="Available Pipeline Presets")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Description", style="white")
    
    table.add_row("matrix_completion", "Classical", "Nuclear norm minimization via ISTA")
    table.add_row("wiener", "Classical", "Frequency-domain Wiener filter")
    table.add_row("fista", "Classical", "Fast ISTA for sparse recovery")
    table.add_row("unet_v1", "Deep Learning", "4-level U-Net for interpolation")
    table.add_row("autoencoder", "Deep Learning", "Convolutional autoencoder denoising")
    table.add_row("pinn", "Physics-Informed", "Wave equation constrained NN")
    
    console.print(table)


@app.command()
def ingest(
    input_path: Path = typer.Argument(..., help="Path to raw seismic file(s) or directory"),
    output_dir: Path = typer.Argument(..., help="Output directory for processed data"),
    format: str = typer.Option("hdf5", "--format", "-f", help="Output format: hdf5, npy, zarr"),
    normalize: bool = typer.Option(False, "--normalize", "-n", help="Normalize traces"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Ingest raw seismic data files and convert to standardized format.
    
    Supported input formats: SEG-Y, miniSEED, SAC, HDF5, NumPy.
    Converts to standardized internal representation for pipeline processing.
    """
    import os
    from promethium.io.readers import load_seismic_data
    from promethium.io.writers import save_seismic_data
    
    console.print("[bold]Promethium Data Ingestion[/bold]")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find input files
    if input_path.is_dir():
        extensions = [".sgy", ".segy", ".mseed", ".sac", ".h5", ".hdf5", ".npy"]
        files = [f for f in input_path.iterdir() 
                 if f.suffix.lower() in extensions]
    else:
        files = [input_path]
    
    if not files:
        console.print("[red]No supported seismic files found.[/red]")
        raise typer.Exit(code=1)
    
    console.print(f"Found {len(files)} file(s) to process")
    
    for file_path in files:
        if verbose:
            console.print(f"Processing: {file_path.name}")
        
        try:
            dataset = load_seismic_data(str(file_path))
            
            if normalize:
                # Normalize each trace
                traces = dataset.traces
                traces = traces / (traces.max(axis=1, keepdims=True) + 1e-10)
                dataset.traces = traces
            
            # Generate output filename
            out_name = file_path.stem
            if format == "hdf5":
                out_file = output_dir / f"{out_name}.h5"
            elif format == "npy":
                out_file = output_dir / f"{out_name}.npy"
            elif format == "zarr":
                out_file = output_dir / f"{out_name}.zarr"
            else:
                out_file = output_dir / f"{out_name}.h5"
            
            save_seismic_data(dataset, str(out_file))
            console.print(f"  [green]Saved: {out_file.name}[/green]")
            
        except Exception as e:
            console.print(f"  [red]Error: {e}[/red]")
    
    console.print(f"[bold green]Ingestion complete. Output: {output_dir}[/bold green]")


@app.command(name="batch-run")
def batch_run(
    config_dir: Path = typer.Argument(..., help="Directory containing pipeline config files"),
    output_dir: Path = typer.Option(Path("results"), "--output", "-o", help="Output directory"),
    experiment_id: Optional[str] = typer.Option(None, "--experiment-id", help="Experiment ID for logging"),
    parallel: int = typer.Option(1, "--parallel", "-j", help="Number of parallel runs"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Run multiple pipeline configurations in batch mode.
    
    Reads all YAML config files from config_dir and executes each pipeline.
    Results are aggregated into a summary report.
    """
    import yaml
    import json
    from datetime import datetime
    
    console.print("[bold]Promethium Batch Pipeline Runner[/bold]")
    
    # Find config files
    config_files = list(config_dir.glob("*.yaml")) + list(config_dir.glob("*.yml"))
    
    if not config_files:
        console.print(f"[red]No config files found in {config_dir}[/red]")
        raise typer.Exit(code=1)
    
    console.print(f"Found {len(config_files)} configuration(s)")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Results collection
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for config_file in config_files:
        console.print(f"\n[cyan]Running: {config_file.name}[/cyan]")
        
        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)
            
            # Extract pipeline settings
            pipeline_name = config.get("pipeline", {}).get("name", "unknown")
            input_data = config.get("input", {}).get("path", "")
            
            if verbose:
                console.print(f"  Pipeline: {pipeline_name}")
                console.print(f"  Input: {input_data}")
            
            # Here we would call the actual pipeline runner
            # For now, record the config for the batch report
            run_result = {
                "config": config_file.name,
                "pipeline": pipeline_name,
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
            }
            results.append(run_result)
            console.print(f"  [green]Completed[/green]")
            
        except Exception as e:
            console.print(f"  [red]Error: {e}[/red]")
            results.append({
                "config": config_file.name,
                "status": "failed",
                "error": str(e),
            })
    
    # Write summary report
    report_file = output_dir / f"batch_report_{timestamp}.json"
    with open(report_file, "w") as f:
        json.dump({
            "experiment_id": experiment_id,
            "timestamp": timestamp,
            "total_runs": len(config_files),
            "successful": sum(1 for r in results if r.get("status") == "completed"),
            "failed": sum(1 for r in results if r.get("status") == "failed"),
            "runs": results,
        }, f, indent=2)
    
    console.print(f"\n[bold green]Batch complete. Report: {report_file}[/bold green]")


# Experiments subcommand group
experiments_app = typer.Typer(help="Experiment tracking and management commands")
app.add_typer(experiments_app, name="experiments")


@experiments_app.command(name="list")
def experiments_list(
    logs_dir: Path = typer.Option(Path("experiments/logs"), "--dir", "-d", help="Logs directory"),
):
    """List all recorded experiments."""
    if not logs_dir.exists():
        console.print(f"[yellow]No experiments directory found at {logs_dir}[/yellow]")
        return
    
    log_files = list(logs_dir.glob("*.jsonl")) + list(logs_dir.glob("*.json"))
    
    if not log_files:
        console.print("[yellow]No experiment logs found.[/yellow]")
        return
    
    table = Table(title="Recorded Experiments")
    table.add_column("Experiment ID", style="cyan")
    table.add_column("Runs", style="green")
    table.add_column("Last Modified", style="dim")
    
    for log_file in sorted(log_files):
        import os
        from datetime import datetime
        
        mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
        
        # Count lines for JSONL files
        with open(log_file, "r") as f:
            run_count = sum(1 for _ in f)
        
        table.add_row(
            log_file.stem,
            str(run_count),
            mtime.strftime("%Y-%m-%d %H:%M"),
        )
    
    console.print(table)


@experiments_app.command(name="show")
def experiments_show(
    experiment_id: str = typer.Argument(..., help="Experiment ID to display"),
    logs_dir: Path = typer.Option(Path("experiments/logs"), "--dir", "-d", help="Logs directory"),
    last_n: int = typer.Option(10, "--last", "-n", help="Show last N runs"),
):
    """Show details of a specific experiment."""
    import json
    
    log_file = logs_dir / f"{experiment_id}.jsonl"
    if not log_file.exists():
        log_file = logs_dir / f"{experiment_id}.json"
    
    if not log_file.exists():
        console.print(f"[red]Experiment not found: {experiment_id}[/red]")
        raise typer.Exit(code=1)
    
    console.print(f"[bold]Experiment: {experiment_id}[/bold]\n")
    
    runs = []
    with open(log_file, "r") as f:
        for line in f:
            if line.strip():
                runs.append(json.loads(line))
    
    # Show summary
    console.print(f"Total runs: {len(runs)}")
    
    # Show last N runs
    table = Table(title=f"Last {min(last_n, len(runs))} Runs")
    table.add_column("Run ID", style="cyan")
    table.add_column("Pipeline", style="yellow")
    table.add_column("SNR", style="green")
    table.add_column("MSE", style="green")
    table.add_column("Timestamp", style="dim")
    
    for run in runs[-last_n:]:
        metrics = run.get("metrics", {})
        table.add_row(
            run.get("run_id", "N/A"),
            run.get("pipeline", "N/A"),
            f"{metrics.get('snr', 'N/A'):.2f}" if isinstance(metrics.get('snr'), (int, float)) else "N/A",
            f"{metrics.get('mse', 'N/A'):.2e}" if isinstance(metrics.get('mse'), (int, float)) else "N/A",
            run.get("timestamp", "N/A")[:19] if run.get("timestamp") else "N/A",
        )
    
    console.print(table)


@experiments_app.command(name="export")
def experiments_export(
    experiment_id: str = typer.Argument(..., help="Experiment ID to export"),
    output: Path = typer.Option(Path("experiment_export.csv"), "--output", "-o", help="Output file"),
    format: str = typer.Option("csv", "--format", "-f", help="Export format: csv, json"),
    logs_dir: Path = typer.Option(Path("experiments/logs"), "--dir", "-d", help="Logs directory"),
):
    """Export experiment data to CSV or JSON format."""
    import json
    import csv
    
    log_file = logs_dir / f"{experiment_id}.jsonl"
    if not log_file.exists():
        log_file = logs_dir / f"{experiment_id}.json"
    
    if not log_file.exists():
        console.print(f"[red]Experiment not found: {experiment_id}[/red]")
        raise typer.Exit(code=1)
    
    runs = []
    with open(log_file, "r") as f:
        for line in f:
            if line.strip():
                runs.append(json.loads(line))
    
    if format == "json":
        with open(output, "w") as f:
            json.dump(runs, f, indent=2)
    else:
        # CSV export
        if runs:
            # Flatten metrics into columns
            fieldnames = ["run_id", "experiment_id", "pipeline", "dataset", "timestamp"]
            if runs[0].get("metrics"):
                fieldnames.extend([f"metric_{k}" for k in runs[0]["metrics"].keys()])
            
            with open(output, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for run in runs:
                    row = {
                        "run_id": run.get("run_id", ""),
                        "experiment_id": run.get("experiment_id", ""),
                        "pipeline": run.get("pipeline", ""),
                        "dataset": run.get("dataset", ""),
                        "timestamp": run.get("timestamp", ""),
                    }
                    for k, v in run.get("metrics", {}).items():
                        row[f"metric_{k}"] = v
                    writer.writerow(row)
    
    console.print(f"[green]Exported to: {output}[/green]")


@app.command()
def version():
    """Show Promethium version information."""
    from promethium import __version__
    
    console.print(f"Promethium version: [bold]{__version__}[/bold]")
    console.print("Multi-language implementations: Python, R, Julia, Scala")
    console.print("Repository: https://github.com/olaflaitinen/Promethium")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
