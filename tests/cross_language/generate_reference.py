"""
Generate reference data for cross-language validation testing.

This script creates standardized test inputs and Python reference outputs
that other language implementations use for consistency validation.
"""
import numpy as np
import json
from pathlib import Path

# Reproducibility
np.random.seed(42)

def generate_low_rank_matrix(m: int, n: int, rank: int) -> np.ndarray:
    """Generate a low-rank matrix for completion tests."""
    U = np.random.randn(m, rank)
    V = np.random.randn(n, rank)
    return U @ V.T

def generate_sparse_signal(n: int, sparsity: int) -> np.ndarray:
    """Generate sparse signal for compressive sensing tests."""
    x = np.zeros(n)
    indices = np.random.choice(n, sparsity, replace=False)
    x[indices] = np.random.randn(sparsity) * 2
    return x

def compute_snr(reference: np.ndarray, estimate: np.ndarray) -> float:
    """Compute SNR in dB."""
    signal_power = np.mean(reference**2)
    noise_power = np.mean((reference - estimate)**2)
    return 10 * np.log10(signal_power / (noise_power + 1e-10))

def compute_mse(reference: np.ndarray, estimate: np.ndarray) -> float:
    """Compute MSE."""
    return float(np.mean((reference - estimate)**2))

def soft_threshold(x: np.ndarray, tau: float) -> np.ndarray:
    """Soft thresholding operator."""
    return np.sign(x) * np.maximum(np.abs(x) - tau, 0)

def matrix_completion_ista(M: np.ndarray, mask: np.ndarray, 
                            lambda_: float = 0.1, max_iter: int = 50) -> np.ndarray:
    """Reference ISTA implementation for matrix completion."""
    X = M.copy()
    X[~mask] = 0
    L = 1.0
    
    for _ in range(max_iter):
        grad = mask * (X - M)
        Z = X - (1/L) * grad
        U, S, Vt = np.linalg.svd(Z, full_matrices=False)
        S_thresh = soft_threshold(S, lambda_/L)
        X = U @ np.diag(S_thresh) @ Vt
    
    return X

def main():
    output_dir = Path(__file__).parent / "reference"
    output_dir.mkdir(exist_ok=True)
    
    print("Generating cross-language reference data...")
    
    # Test Case 1: Matrix Completion
    print("  1. Matrix completion test case...")
    m, n, r = 50, 50, 5
    true_matrix = generate_low_rank_matrix(m, n, r)
    mask = np.random.rand(m, n) < 0.6
    
    observed = true_matrix.copy()
    observed[~mask] = 0
    
    completed = matrix_completion_ista(observed, mask, lambda_=0.1, max_iter=50)
    
    np.save(output_dir / "matrix_true.npy", true_matrix)
    np.save(output_dir / "matrix_observed.npy", observed)
    np.save(output_dir / "matrix_mask.npy", mask)
    np.save(output_dir / "matrix_completed_python.npy", completed)
    
    mc_metrics = {
        "relative_error": float(np.linalg.norm(completed - true_matrix) / np.linalg.norm(true_matrix)),
        "snr": compute_snr(true_matrix, completed),
        "mse": compute_mse(true_matrix, completed),
    }
    
    # Test Case 2: Metrics computation
    print("  2. Metrics computation test case...")
    reference = np.random.randn(100, 100)
    noisy = reference + 0.1 * np.random.randn(100, 100)
    
    np.save(output_dir / "metrics_reference.npy", reference)
    np.save(output_dir / "metrics_noisy.npy", noisy)
    
    metrics_test = {
        "snr": compute_snr(reference, noisy),
        "mse": compute_mse(reference, noisy),
    }
    
    # Save all reference values
    all_references = {
        "version": "1.0.4",
        "tolerance": {
            "metric_absolute": 1e-6,
            "metric_relative": 1e-4,
            "array_absolute": 1e-8,
            "array_relative": 1e-6,
        },
        "matrix_completion": mc_metrics,
        "metrics_test": metrics_test,
    }
    
    with open(output_dir / "reference_values.json", "w") as f:
        json.dump(all_references, f, indent=2)
    
    print(f"Reference data saved to: {output_dir}")
    print("Done.")

if __name__ == "__main__":
    main()
