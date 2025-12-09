# Compressive Sensing Algorithms

Compressive sensing recovers sparse signals from undersampled measurements.

## Problem Formulation

Given measurements y = Ax + noise where x is sparse, solve:

```
min_x  (1/2) ||Ax - y||_2^2 + lambda ||Psi * x||_1
```

where:
- A is the measurement matrix
- Psi is a sparsifying transform (identity, DCT, wavelet)
- lambda is the regularization parameter

## FISTA (Fast ISTA)

FISTA adds Nesterov momentum to ISTA for faster convergence.

### Algorithm

```
Input: y (observations), A (matrix), lambda, max_iter, tol
Output: x (sparse solution)

1. Initialize x = 0, z = x, t = 1
2. L = ||A||_2^2 (spectral norm squared)
3. For k = 1 to max_iter:
   a. Gradient: g = A' * (A * z - y)
   b. Gradient step: u = z - (1/L) * g
   c. Soft threshold: x_new = sign(u) * max(|u| - lambda/L, 0)
   d. Momentum: t_new = (1 + sqrt(1 + 4*t^2)) / 2
   e. Extrapolation: z = x_new + ((t-1)/t_new) * (x_new - x)
   f. Update: x = x_new, t = t_new
4. Return x
```

### Convergence Rate

FISTA converges at rate O(1/k^2), compared to O(1/k) for ISTA.

## Seismic Applications

### Missing Trace Interpolation

Create measurement matrix A as a subsampling operator:

```python
# Observation indices
observed_indices = [0, 2, 5, 7, ...]  # Known traces
A = np.zeros((len(observed_indices), n_total))
for i, idx in enumerate(observed_indices):
    A[i, idx] = 1
```

### Curvelet-Domain Sparsity

Seismic data is sparse in the curvelet domain:

```python
# Transform to curvelet domain, apply L1, transform back
Psi = CurveletTransform()
x_curvelet = fista(y, A @ Psi.inverse, lambda_)
x_recovered = Psi.inverse(x_curvelet)
```

## Implementation

### Python
```python
from promethium.signal.reconstruction import CompressiveSensingFISTA
solver = CompressiveSensingFISTA(lambda_=0.1)
recovered = solver.solve(y, A)
```

### R
```r
recovered <- compressive_sensing_fista(y, A, lambda = 0.1)
```

### Julia
```julia
recovered = compressive_sensing_fista(y, A; lambda=0.1)
```

### Scala
```scala
val recovered = CompressiveSensing.fista(y, A, lambda = 0.1)
```

## References

1. Candes, E.J., Romberg, J., & Tao, T. (2006). Robust uncertainty principles.
2. Herrmann, F.J., et al. (2008). Curvelet-based seismic data processing.
