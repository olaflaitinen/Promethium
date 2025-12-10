#!/usr/bin/env python
"""
Seismic Denoising Pipeline Recipe

This script demonstrates a typical seismic denoising workflow using Promethium.
It loads noisy data, applies denoising, and evaluates the results.

Usage:
    python denoise_shot_gather.py input.npy output.npy --method wiener
    python denoise_shot_gather.py input.sgy output.sgy --method unet --config config.yaml
"""
import argparse
from pathlib import Path

import numpy as np


def main():
    parser = argparse.ArgumentParser(
        description="Denoise seismic shot gather data using Promethium."
    )
    parser.add_argument("input", type=Path, help="Input seismic data file")
    parser.add_argument("output", type=Path, help="Output file path")
    parser.add_argument(
        "--method", 
        type=str, 
        default="wiener",
        choices=["wiener", "bandpass", "unet", "autoencoder"],
        help="Denoising method to use"
    )
    parser.add_argument("--config", type=Path, help="Optional YAML configuration file")
    parser.add_argument("--reference", type=Path, help="Reference data for evaluation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Import Promethium components
    from promethium import SeismicDataset
    from promethium.io.readers import load_seismic_data
    from promethium.io.writers import save_seismic_data
    from promethium.pipelines.recovery import SeismicRecoveryPipeline
    from promethium.evaluation.metrics import signal_to_noise_ratio, mean_squared_error
    
    print(f"Promethium Seismic Denoising")
    print(f"Input: {args.input}")
    print(f"Method: {args.method}")
    print("-" * 40)
    
    # Load data
    if args.verbose:
        print("Loading input data...")
    
    dataset = load_seismic_data(str(args.input))
    print(f"Loaded: {dataset.traces.shape[0]} traces, {dataset.traces.shape[1]} samples")
    
    # Configure pipeline
    pipeline_config = {
        "model": {
            "type": args.method,
        }
    }
    
    # Load additional config if provided
    if args.config:
        import yaml
        with open(args.config, "r") as f:
            user_config = yaml.safe_load(f)
            pipeline_config.update(user_config)
    
    # Create and run pipeline
    if args.verbose:
        print(f"Running {args.method} denoising...")
    
    pipeline = SeismicRecoveryPipeline(args.method, pipeline_config)
    result = pipeline.run(dataset)
    
    # Evaluate if reference available
    if args.reference and args.reference.exists():
        if args.verbose:
            print("Computing quality metrics...")
        
        reference_data = np.load(str(args.reference))
        result_data = result.traces if hasattr(result, "traces") else np.array(result)
        
        snr = signal_to_noise_ratio(reference_data, result_data)
        mse = mean_squared_error(reference_data, result_data)
        
        print(f"SNR: {snr:.2f} dB")
        print(f"MSE: {mse:.6e}")
    
    # Save output
    if args.verbose:
        print(f"Saving to {args.output}...")
    
    args.output.parent.mkdir(parents=True, exist_ok=True)
    save_seismic_data(result, str(args.output))
    
    print(f"Done. Output saved to: {args.output}")


if __name__ == "__main__":
    main()
