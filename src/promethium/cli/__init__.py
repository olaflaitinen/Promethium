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
