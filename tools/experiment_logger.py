"""
Promethium Experiment Logger

Lightweight experiment tracking for seismic data recovery pipelines.
Logs run metadata, parameters, and metrics to JSON-lines files.

Usage:
    from promethium.tools.experiment_logger import ExperimentLogger
    
    logger = ExperimentLogger("my_experiment")
    run_id = logger.start_run(pipeline="unet", dataset="synthetic")
    logger.log_params({"learning_rate": 0.001, "epochs": 100})
    logger.log_metrics({"snr": 18.5, "mse": 0.002})
    logger.end_run()
"""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class ExperimentLogger:
    """Lightweight experiment logger using JSON-lines format."""
    
    DEFAULT_LOGS_DIR = Path("experiments/logs")
    
    def __init__(
        self,
        experiment_id: str,
        logs_dir: Optional[Path] = None,
        auto_create: bool = True,
    ):
        """
        Initialize experiment logger.
        
        Args:
            experiment_id: Unique identifier for this experiment.
            logs_dir: Directory for log files. Defaults to experiments/logs.
            auto_create: Whether to create logs directory if it doesn't exist.
        """
        self.experiment_id = experiment_id
        self.logs_dir = logs_dir or self.DEFAULT_LOGS_DIR
        
        if auto_create:
            self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.logs_dir / f"{experiment_id}.jsonl"
        
        # Current run state
        self._current_run: Optional[Dict[str, Any]] = None
        self._run_id: Optional[str] = None
    
    def start_run(
        self,
        pipeline: Optional[str] = None,
        dataset: Optional[str] = None,
        config_path: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Start a new run within this experiment.
        
        Args:
            pipeline: Name of the pipeline being run.
            dataset: Name of the dataset being used.
            config_path: Path to configuration file.
            tags: Optional key-value tags for this run.
            
        Returns:
            Unique run ID.
        """
        self._run_id = str(uuid.uuid4())[:8]
        
        self._current_run = {
            "run_id": self._run_id,
            "experiment_id": self.experiment_id,
            "pipeline": pipeline,
            "dataset": dataset,
            "config_path": config_path,
            "tags": tags or {},
            "parameters": {},
            "metrics": {},
            "artifacts": [],
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "status": "running",
            "error": None,
        }
        
        return self._run_id
    
    def log_params(self, params: Dict[str, Any]) -> None:
        """
        Log parameters for the current run.
        
        Args:
            params: Dictionary of parameter names and values.
        """
        if self._current_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        
        self._current_run["parameters"].update(params)
    
    def log_param(self, key: str, value: Any) -> None:
        """
        Log a single parameter.
        
        Args:
            key: Parameter name.
            value: Parameter value.
        """
        self.log_params({key: value})
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        """
        Log metrics for the current run.
        
        Args:
            metrics: Dictionary of metric names and values.
            step: Optional step/epoch number for time-series metrics.
        """
        if self._current_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        
        if step is not None:
            # Store as time series
            for key, value in metrics.items():
                if key not in self._current_run["metrics"]:
                    self._current_run["metrics"][key] = []
                self._current_run["metrics"][key].append({
                    "step": step,
                    "value": value,
                    "timestamp": datetime.now().isoformat(),
                })
        else:
            # Store as final metrics
            self._current_run["metrics"].update(metrics)
    
    def log_metric(self, key: str, value: float, step: Optional[int] = None) -> None:
        """
        Log a single metric.
        
        Args:
            key: Metric name.
            value: Metric value.
            step: Optional step number.
        """
        self.log_metrics({key: value}, step=step)
    
    def log_artifact(self, path: str, artifact_type: str = "file") -> None:
        """
        Log an artifact (file) path for the current run.
        
        Args:
            path: Path to the artifact file.
            artifact_type: Type of artifact (file, model, plot, etc.).
        """
        if self._current_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        
        self._current_run["artifacts"].append({
            "path": path,
            "type": artifact_type,
            "logged_at": datetime.now().isoformat(),
        })
    
    def end_run(self, status: str = "completed", error: Optional[str] = None) -> None:
        """
        End the current run and write to log file.
        
        Args:
            status: Run status (completed, failed, cancelled).
            error: Error message if status is failed.
        """
        if self._current_run is None:
            raise RuntimeError("No active run to end.")
        
        self._current_run["end_time"] = datetime.now().isoformat()
        self._current_run["status"] = status
        self._current_run["error"] = error
        
        # Calculate duration
        start = datetime.fromisoformat(self._current_run["start_time"])
        end = datetime.fromisoformat(self._current_run["end_time"])
        self._current_run["duration_seconds"] = (end - start).total_seconds()
        
        # Write to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(self._current_run) + "\n")
        
        # Reset state
        self._current_run = None
        self._run_id = None
    
    def get_runs(self) -> list:
        """
        Get all runs for this experiment.
        
        Returns:
            List of run dictionaries.
        """
        runs = []
        if self.log_file.exists():
            with open(self.log_file, "r") as f:
                for line in f:
                    if line.strip():
                        runs.append(json.loads(line))
        return runs
    
    def get_best_run(self, metric: str, maximize: bool = True) -> Optional[Dict]:
        """
        Get the run with the best value for a given metric.
        
        Args:
            metric: Metric name to optimize.
            maximize: Whether to maximize (True) or minimize (False).
            
        Returns:
            Best run dictionary or None if no runs found.
        """
        runs = self.get_runs()
        if not runs:
            return None
        
        def get_metric_value(run: Dict) -> float:
            val = run.get("metrics", {}).get(metric)
            if isinstance(val, list):
                # Time series - get last value
                return val[-1]["value"] if val else float('-inf' if maximize else 'inf')
            return val if val is not None else float('-inf' if maximize else 'inf')
        
        return max(runs, key=get_metric_value) if maximize else min(runs, key=get_metric_value)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for this experiment.
        
        Returns:
            Dictionary with experiment summary.
        """
        runs = self.get_runs()
        
        if not runs:
            return {
                "experiment_id": self.experiment_id,
                "total_runs": 0,
                "completed": 0,
                "failed": 0,
            }
        
        completed = [r for r in runs if r.get("status") == "completed"]
        failed = [r for r in runs if r.get("status") == "failed"]
        
        # Aggregate metrics across completed runs
        metric_values = {}
        for run in completed:
            for key, value in run.get("metrics", {}).items():
                if isinstance(value, (int, float)):
                    if key not in metric_values:
                        metric_values[key] = []
                    metric_values[key].append(value)
        
        # Calculate statistics
        metric_stats = {}
        for key, values in metric_values.items():
            if values:
                metric_stats[key] = {
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                }
        
        return {
            "experiment_id": self.experiment_id,
            "total_runs": len(runs),
            "completed": len(completed),
            "failed": len(failed),
            "metric_summary": metric_stats,
            "first_run": runs[0].get("start_time") if runs else None,
            "last_run": runs[-1].get("start_time") if runs else None,
        }


# Context manager support
class ExperimentRun:
    """Context manager for experiment runs."""
    
    def __init__(self, logger: ExperimentLogger, **kwargs):
        self.logger = logger
        self.kwargs = kwargs
        self.run_id = None
    
    def __enter__(self) -> "ExperimentRun":
        self.run_id = self.logger.start_run(**self.kwargs)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.logger.end_run(status="failed", error=str(exc_val))
        else:
            self.logger.end_run(status="completed")
        return False


def create_experiment(experiment_id: str, logs_dir: Optional[str] = None) -> ExperimentLogger:
    """
    Create a new experiment logger.
    
    Args:
        experiment_id: Unique experiment identifier.
        logs_dir: Optional logs directory path.
        
    Returns:
        ExperimentLogger instance.
    """
    return ExperimentLogger(
        experiment_id,
        logs_dir=Path(logs_dir) if logs_dir else None,
    )
