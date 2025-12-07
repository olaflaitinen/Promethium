import numpy as np
from .base import RecoveryAlgorithm
from scipy.fft import dct, idct

class CompressiveSensing(RecoveryAlgorithm):
    """
    Compressive Sensing recovery using Iterative Shrinkage-Thresholding Algorithm (ISTA).
    Minimizes ||y - Phi * x||_2^2 + lambda * ||Psi * x||_1
    where Psi is the sparsifying transform (DCT or Curvelet).
    """
    def __init__(self, lamb: float = 0.1, max_iters: int = 100, tol: float = 1e-5):
        super().__init__()
        self.lamb = lamb
        self.max_iters = max_iters
        self.tol = tol
        self.reconstructed_data = None

    def _soft_threshold(self, x: np.ndarray, thresh: float) -> np.ndarray:
        return np.sign(x) * np.maximum(np.abs(x) - thresh, 0.0)

    def _sparsify(self, data: np.ndarray) -> np.ndarray:
        # Default to 2D DCT
        return dct(dct(data, axis=0, norm='ortho'), axis=1, norm='ortho')

    def _inverse_sparsify(self, coeffs: np.ndarray) -> np.ndarray:
        return idct(idct(coeffs, axis=0, norm='ortho'), axis=1, norm='ortho')

    def fit(self, data: np.ndarray, mask: np.ndarray = None) -> 'CompressiveSensing':
        """
        Fit the model to the incomplete data.
        data: Observed seismic data (missing traces should be filled with zeros or noise)
        mask: boolean mask (True where data is observed)
        """
        if mask is None:
            mask = ~np.isnan(data)
            data = np.nan_to_num(data)

        # Initialize with zero-filled data
        r = data.copy()
        r[~mask] = 0.0
        
        # ISTA Loop
        # x_k+1 = soft(x_k + alpha * AT(y - A x_k), lambda * alpha)
        # Here, A is the Sampling Operator (Phi) combined with Inverse Transform (Psi^-1) if we solve for coefficients.
        # Alternatively, POCS (Projection onto Convex Sets) approach:
        # 1. Transform to sparse domain
        # 2. Threshold
        # 3. Inverse transform
        # 4. Re-insert observed data
        
        for i in range(self.max_iters):
             # 1. Sparsify
            coeffs = self._sparsify(r)
            
            # 2. Threshold
            coeffs_thresh = self._soft_threshold(coeffs, self.lamb)
            
            # 3. Inverse Transform
            r_new = self._inverse_sparsify(coeffs_thresh)
            
            # 4. Enforce Data Consistency
            r_new[mask] = data[mask]
            
            # Check convergence
            if np.linalg.norm(r_new - r) / (np.linalg.norm(r) + 1e-9) < self.tol:
                r = r_new
                break
                
            r = r_new
            
        self.reconstructed_data = r
        return self

    def transform(self, data: np.ndarray, mask: np.ndarray = None) -> np.ndarray:
        if self.reconstructed_data is None:
            raise RuntimeError("Model must be fitted before calling transform")
        return self.reconstructed_data
