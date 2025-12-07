import numpy as np
from .base import RecoveryAlgorithm
from scipy.sparse.linalg import svds

class SoftImpute(RecoveryAlgorithm):
    """
    Optimized implementation of Soft Impute algorithm for Matrix Completion.
    Minimizes ||X - M||_F^2 + lambda * ||X||_*
    """
    def __init__(self, lamb: float = 0.1, max_iters: int = 100, tol: float = 1e-5, rank: int = 10):
        super().__init__()
        self.lamb = lamb
        self.max_iters = max_iters
        self.tol = tol
        self.rank = rank # Optimization: Use truncated SVD
        self.X_reconstructed = None

    def fit(self, data: np.ndarray, mask: np.ndarray = None) -> 'SoftImpute':
        if mask is None:
            mask = ~np.isnan(data)
            
        # Initialize X with zeros where missing
        X = data.copy()
        X[~mask] = 0.0
        
        for i in range(self.max_iters):
            X_old = X.copy()
            
            # Optimization: Use randomized/truncated SVD for speed on large matrices
            if self.rank < min(X.shape):
                U, s, Vt = svds(X, k=self.rank)
                # svds returns singular values in increasing order
                s = s[::-1]
                U = U[:, ::-1]
                Vt = Vt[::-1, :]
            else:
                U, s, Vt = np.linalg.svd(X, full_matrices=False)
            
            # Soft thresholding
            s_thresh = np.maximum(s - self.lamb, 0)
            
            # Reconstruct low-rank approximation
            X_new = np.dot(U * s_thresh, Vt)
            
            # Enforce data consistency (Client constraint)
            X_new[mask] = data[mask]
            X = X_new
            
            # Check convergence
            diff = np.linalg.norm(X - X_old) / (np.linalg.norm(X_old) + 1e-9)
            if diff < self.tol:
                break
            
        self.X_reconstructed = X
        return self

    def transform(self, data: np.ndarray, mask: np.ndarray = None) -> np.ndarray:
        if self.X_reconstructed is None:
            raise RuntimeError("Model must be fitted before calling transform")
        return self.X_reconstructed
