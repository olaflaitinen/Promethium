# Matrix Completion Algorithms

Matrix completion recovers missing entries in a partially observed matrix by exploiting low-rank structure.

## Problem Formulation

Given a partially observed matrix M with observation mask Omega, find a low-rank matrix X such that:

```
min_X  (1/2) ||P_Omega(X - M)||_F^2 + lambda ||X||_*
```

where:
- P_Omega is the projection onto observed entries
- ||X||_* is the nuclear norm (sum of singular values)
- lambda is the regularization parameter

## ISTA (Iterative Shrinkage-Thresholding Algorithm)

### Algorithm

```
Input: M (observed matrix), Omega (mask), lambda, max_iter, tol
Output: X (completed matrix)

1. Initialize X = M with zeros for missing entries
2. L = 1.0 (Lipschitz constant)
3. For k = 1 to max_iter:
   a. Compute gradient: G = Omega * (X - M)
   b. Gradient step: Z = X - (1/L) * G
   c. SVD: U, S, V = svd(Z)
   d. Soft threshold: S_thresh = max(S - lambda/L, 0)
   e. Update: X_new = U * diag(S_thresh) * V'
   f. Check convergence: if ||X_new - X||/||X|| < tol, break
   g. X = X_new
4. Return X
```

### Soft Thresholding

The proximal operator for the nuclear norm is singular value soft thresholding:

```
prox_{lambda ||.||_*}(Z) = U * diag(max(s_i - lambda, 0)) * V'
```

## Convergence

ISTA converges at rate O(1/k) where k is the iteration count. For faster convergence, use FISTA (Fast ISTA) with momentum acceleration.

## Implementation Notes

### Python
```python
from promethium.signal.reconstruction import MatrixCompletionISTA
solver = MatrixCompletionISTA(lambda_=0.1, max_iter=100)
completed = solver.complete(observed, mask)
```

### R
```r
completed <- matrix_completion_ista(observed, mask, lambda = 0.1)
```

### Julia
```julia
completed = matrix_completion_ista(observed, mask; lambda=0.1)
```

### Scala
```scala
val completed = MatrixCompletion.ista(observed, mask, lambda = 0.1)
```

## References

1. Candes, E.J., & Recht, B. (2009). Exact matrix completion via convex optimization.
2. Beck, A., & Teboulle, M. (2009). A fast iterative shrinkage-thresholding algorithm for linear inverse problems.
