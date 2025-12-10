"""
Promethium Pipeline Runner

Configuration-driven pipeline execution for seismic data recovery.
Parses YAML configs, builds pipelines, and executes with logging.

Usage:
    from promethium.tools.pipeline_runner import run_pipeline_from_config
    
    result = run_pipeline_from_config("configs/pipelines/unet_denoising.yaml")
"""
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from datetime import datetime


def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load and validate a pipeline configuration file.
    
    Args:
        config_path: Path to YAML configuration file.
        
    Returns:
        Configuration dictionary.
        
    Raises:
        ValueError: If configuration is invalid.
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Validate required sections
    required = ["pipeline", "input", "model", "output"]
    missing = [r for r in required if r not in config]
    if missing:
        raise ValueError(f"Missing required config sections: {missing}")
    
    return config


def build_pipeline(config: Dict[str, Any]):
    """
    Build a SeismicRecoveryPipeline from configuration.
    
    Args:
        config: Pipeline configuration dictionary.
        
    Returns:
        Configured pipeline object.
    """
    from promethium.pipelines.recovery import SeismicRecoveryPipeline
    
    pipeline_name = config["pipeline"]["name"]
    pipeline_type = config["pipeline"].get("type", "classical")
    
    # Build model configuration
    model_config = config.get("model", {})
    
    # Create pipeline
    pipe = SeismicRecoveryPipeline(pipeline_name, {
        "model": model_config,
        "preprocessing": config.get("preprocessing", {}),
        "postprocessing": config.get("postprocessing", {}),
    })
    
    return pipe


def load_data(config: Dict[str, Any]):
    """
    Load input data based on configuration.
    
    Args:
        config: Configuration dictionary with input section.
        
    Returns:
        SeismicDataset object.
    """
    from promethium.io.readers import load_seismic_data
    
    input_config = config["input"]
    input_path = input_config["path"]
    
    dataset = load_seismic_data(input_path)
    
    return dataset


def run_evaluation(
    reconstructed,
    config: Dict[str, Any],
) -> Dict[str, float]:
    """
    Run evaluation metrics on reconstructed data.
    
    Args:
        reconstructed: Reconstructed data array.
        config: Configuration dictionary with evaluation section.
        
    Returns:
        Dictionary of metric names to values.
    """
    import numpy as np
    from promethium.evaluation.metrics import (
        signal_to_noise_ratio,
        mean_squared_error,
        peak_signal_to_noise_ratio,
        structural_similarity_index,
    )
    
    eval_config = config.get("evaluation", {})
    ref_path = eval_config.get("reference_path")
    
    if not ref_path:
        return {}
    
    # Load reference data
    reference = np.load(ref_path)
    
    # Get data as numpy array
    if hasattr(reconstructed, "traces"):
        recon_data = reconstructed.traces
    elif hasattr(reconstructed, "values"):
        recon_data = reconstructed.values
    else:
        recon_data = np.array(reconstructed)
    
    # Compute metrics
    metrics = {}
    metric_list = eval_config.get("metrics", ["snr", "mse"])
    
    if "snr" in metric_list:
        metrics["snr"] = float(signal_to_noise_ratio(reference, recon_data))
    
    if "mse" in metric_list:
        metrics["mse"] = float(mean_squared_error(reference, recon_data))
    
    if "psnr" in metric_list:
        metrics["psnr"] = float(peak_signal_to_noise_ratio(reference, recon_data))
    
    if "ssim" in metric_list:
        metrics["ssim"] = float(structural_similarity_index(reference, recon_data))
    
    return metrics


def save_results(
    reconstructed,
    metrics: Dict[str, float],
    config: Dict[str, Any],
) -> Path:
    """
    Save reconstruction results and metrics.
    
    Args:
        reconstructed: Reconstructed data.
        metrics: Evaluation metrics dictionary.
        config: Configuration dictionary.
        
    Returns:
        Path to output directory.
    """
    import json
    import numpy as np
    from promethium.io.writers import save_seismic_data
    
    output_config = config["output"]
    output_dir = Path(output_config["path"])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save reconstructed data
    if output_config.get("save_reconstructed", True):
        output_format = output_config.get("format", "npy")
        if output_format == "npy":
            if hasattr(reconstructed, "traces"):
                np.save(output_dir / f"reconstructed_{timestamp}.npy", reconstructed.traces)
            else:
                np.save(output_dir / f"reconstructed_{timestamp}.npy", reconstructed)
        else:
            save_seismic_data(reconstructed, str(output_dir / f"reconstructed_{timestamp}.{output_format}"))
    
    # Save metrics
    if output_config.get("save_metrics", True) and metrics:
        with open(output_dir / f"metrics_{timestamp}.json", "w") as f:
            json.dump({
                "timestamp": timestamp,
                "pipeline": config["pipeline"]["name"],
                "metrics": metrics,
            }, f, indent=2)
    
    return output_dir


def run_pipeline_from_config(
    config_path: str,
    experiment_id: Optional[str] = None,
    verbose: bool = True,
) -> Tuple[Any, Dict[str, float]]:
    """
    Run a complete pipeline from configuration file.
    
    Args:
        config_path: Path to YAML configuration file.
        experiment_id: Optional experiment ID for logging.
        verbose: Whether to print progress messages.
        
    Returns:
        Tuple of (reconstructed data, metrics dictionary).
    """
    config_path = Path(config_path)
    
    if verbose:
        print(f"Loading configuration: {config_path}")
    
    # Load config
    config = load_config(config_path)
    
    pipeline_name = config["pipeline"]["name"]
    if verbose:
        print(f"Pipeline: {pipeline_name}")
    
    # Setup experiment logging
    logger = None
    if experiment_id or config.get("logging", {}).get("experiment_id"):
        from promethium.tools.experiment_logger import ExperimentLogger
        exp_id = experiment_id or config["logging"]["experiment_id"]
        logger = ExperimentLogger(exp_id)
        logger.start_run(
            pipeline=pipeline_name,
            dataset=config["input"].get("path"),
            config_path=str(config_path),
        )
        logger.log_params(config.get("model", {}))
    
    try:
        # Load data
        if verbose:
            print("Loading input data...")
        dataset = load_data(config)
        
        # Build and run pipeline
        if verbose:
            print("Building pipeline...")
        pipeline = build_pipeline(config)
        
        if verbose:
            print("Running reconstruction...")
        reconstructed = pipeline.run(dataset)
        
        # Evaluate
        if verbose:
            print("Computing metrics...")
        metrics = run_evaluation(reconstructed, config)
        
        if verbose and metrics:
            for key, value in metrics.items():
                print(f"  {key}: {value:.4f}")
        
        # Save results
        if verbose:
            print("Saving results...")
        output_dir = save_results(reconstructed, metrics, config)
        
        if verbose:
            print(f"Results saved to: {output_dir}")
        
        # Log completion
        if logger:
            logger.log_metrics(metrics)
            logger.log_artifact(str(output_dir), "results_directory")
            logger.end_run(status="completed")
        
        return reconstructed, metrics
        
    except Exception as e:
        if logger:
            logger.end_run(status="failed", error=str(e))
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pipeline_runner.py <config_path> [experiment_id]")
        sys.exit(1)
    
    config_path = sys.argv[1]
    experiment_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    run_pipeline_from_config(config_path, experiment_id)
