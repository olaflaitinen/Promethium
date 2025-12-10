#!/usr/bin/env python
"""
U-Net Denoising Pipeline Recipe

This script demonstrates training and inference with the U-Net model
for seismic data denoising and interpolation.

Usage:
    # Inference with pre-trained model
    python unet_denoising_pipeline.py infer input.npy output.npy --weights models/unet_v1.pt
    
    # Training from scratch
    python unet_denoising_pipeline.py train --data-dir data/training --epochs 100
"""
import argparse
from pathlib import Path

import numpy as np


def run_inference(args):
    """Run U-Net inference on input data."""
    from promethium.io.readers import load_seismic_data
    from promethium.io.writers import save_seismic_data
    from promethium.ml import load_model, reconstruct
    
    print("U-Net Inference Mode")
    print("-" * 40)
    
    # Load data
    print(f"Loading: {args.input}")
    dataset = load_seismic_data(str(args.input))
    
    # Load model
    print(f"Loading model: {args.weights}")
    model = load_model(str(args.weights), device=args.device)
    
    # Run reconstruction
    print("Running inference...")
    result = reconstruct(dataset, model)
    
    # Save output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    save_seismic_data(result, str(args.output))
    print(f"Saved: {args.output}")


def run_training(args):
    """Train U-Net model from scratch."""
    from promethium.ml.data import SeismicDataLoader
    from promethium.ml.models import UNetDenoiser
    
    print("U-Net Training Mode")
    print("-" * 40)
    
    # Setup data loaders
    print(f"Loading training data from: {args.data_dir}")
    
    train_loader = SeismicDataLoader(
        args.data_dir / "train",
        batch_size=args.batch_size,
        shuffle=True,
    )
    
    val_loader = None
    if (args.data_dir / "val").exists():
        val_loader = SeismicDataLoader(
            args.data_dir / "val",
            batch_size=args.batch_size,
            shuffle=False,
        )
    
    # Create model
    print("Creating U-Net model...")
    model = UNetDenoiser(
        in_channels=1,
        out_channels=1,
        features=[32, 64, 128, 256],
    )
    
    # Training configuration
    import torch
    import torch.nn as nn
    import torch.optim as optim
    
    device = torch.device(args.device if args.device != "auto" else 
                          "cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    
    # Training loop
    print(f"Training for {args.epochs} epochs on {device}")
    
    best_loss = float("inf")
    for epoch in range(args.epochs):
        model.train()
        train_loss = 0.0
        
        for batch_idx, (noisy, clean) in enumerate(train_loader):
            noisy, clean = noisy.to(device), clean.to(device)
            
            optimizer.zero_grad()
            output = model(noisy)
            loss = criterion(output, clean)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        scheduler.step()
        
        # Validation
        val_loss = 0.0
        if val_loader:
            model.eval()
            with torch.no_grad():
                for noisy, clean in val_loader:
                    noisy, clean = noisy.to(device), clean.to(device)
                    output = model(noisy)
                    val_loss += criterion(output, clean).item()
            val_loss /= len(val_loader)
        
        # Print progress
        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(f"Epoch {epoch+1}/{args.epochs} - Train Loss: {train_loss:.6f}", end="")
            if val_loader:
                print(f" - Val Loss: {val_loss:.6f}", end="")
            print()
        
        # Save best model
        current_loss = val_loss if val_loader else train_loss
        if current_loss < best_loss:
            best_loss = current_loss
            args.output_dir.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), args.output_dir / "unet_best.pt")
    
    # Save final model
    torch.save(model.state_dict(), args.output_dir / "unet_final.pt")
    print(f"\nTraining complete. Models saved to: {args.output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="U-Net seismic denoising training and inference."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Inference subcommand
    infer_parser = subparsers.add_parser("infer", help="Run inference")
    infer_parser.add_argument("input", type=Path, help="Input data file")
    infer_parser.add_argument("output", type=Path, help="Output file path")
    infer_parser.add_argument("--weights", type=Path, required=True, help="Model weights")
    infer_parser.add_argument("--device", type=str, default="auto", help="Device (auto/cuda/cpu)")
    
    # Training subcommand
    train_parser = subparsers.add_parser("train", help="Train model")
    train_parser.add_argument("--data-dir", type=Path, required=True, help="Training data directory")
    train_parser.add_argument("--output-dir", type=Path, default=Path("models"), help="Output directory")
    train_parser.add_argument("--epochs", type=int, default=100, help="Number of epochs")
    train_parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    train_parser.add_argument("--learning-rate", type=float, default=0.001, help="Learning rate")
    train_parser.add_argument("--device", type=str, default="auto", help="Device")
    
    args = parser.parse_args()
    
    if args.command == "infer":
        run_inference(args)
    elif args.command == "train":
        run_training(args)


if __name__ == "__main__":
    main()
