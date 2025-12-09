"""
Recovery algorithms for Promethium.jl

Implements matrix completion (ISTA), compressive sensing (FISTA),
following the Promethium specification pseudocode.
"""

"""
    soft_threshold(x, τ)

Soft thresholding operator: sign(x) * max(|x| - τ, 0)
"""
soft_threshold(x::Real, τ::Real) = sign(x) * max(abs(x) - τ, 0)
soft_threshold(x::AbstractArray, τ::Real) = soft_threshold.(x, τ)

"""
    matrix_completion_ista(M, mask; λ=0.1, max_iter=100, tol=1e-5) -> Matrix

Matrix completion via ISTA with nuclear norm regularization.

Solves: min_X (1/2)||P_Ω(X - M)||_F^2 + λ||X||_*

# Arguments
- `M`: Observed matrix (can have NaN for missing)
- `mask`: Boolean matrix (true = observed)
- `λ`: Regularization parameter
- `max_iter`: Maximum iterations
- `tol`: Convergence tolerance

# Returns
Completed matrix X
"""
function matrix_completion_ista(
    M::AbstractMatrix,
    mask::AbstractMatrix{Bool};
    λ::Float64 = 0.1,
    max_iter::Int = 100,
    tol::Float64 = 1e-5
)
    X = copy(M)
    X[.!mask] .= 0.0
    L = 1.0
    
    for k in 1:max_iter
        # Gradient of data fidelity term
        grad = mask .* (X .- M)
        grad[isnan.(grad)] .= 0.0
        
        Z = X .- (1/L) .* grad
        
        # SVD soft-thresholding (proximal of nuclear norm)
        F = svd(Z)
        S_thresh = max.(F.S .- λ/L, 0.0)
        X_new = F.U * Diagonal(S_thresh) * F.Vt
        
        # Check convergence
        rel_change = norm(X_new - X) / (norm(X) + 1e-10)
        if rel_change < tol
            @info "ISTA converged at iteration $k"
            return X_new
        end
        X = X_new
    end
    
    @warn "ISTA did not converge within $max_iter iterations"
    return X
end

"""
    compressive_sensing_fista(y, A; λ=0.1, max_iter=100, tol=1e-5) -> Vector

Sparse recovery via FISTA (Fast ISTA) with L1 regularization.

Solves: min_x (1/2)||Ax - y||_2^2 + λ||x||_1

# Arguments
- `y`: Observation vector
- `A`: Measurement matrix
- `λ`: Regularization parameter
- `max_iter`: Maximum iterations  
- `tol`: Convergence tolerance

# Returns
Recovered sparse vector x
"""
function compressive_sensing_fista(
    y::AbstractVector,
    A::AbstractMatrix;
    λ::Float64 = 0.1,
    max_iter::Int = 100,
    tol::Float64 = 1e-5
)
    n = size(A, 2)
    x = zeros(n)
    z = copy(x)
    t = 1.0
    
    # Lipschitz constant (spectral norm squared)
    L = maximum(svd(A).S)^2
    
    for k in 1:max_iter
        # Gradient step
        grad = A' * (A * z - y)
        u = z - (1/L) * grad
        
        # Proximal step (soft thresholding)
        x_new = soft_threshold(u, λ/L)
        
        # FISTA momentum update
        t_new = (1 + sqrt(1 + 4*t^2)) / 2
        z = x_new + ((t - 1) / t_new) * (x_new - x)
        
        # Check convergence
        if norm(x_new - x) / (norm(x) + 1e-10) < tol
            @info "FISTA converged at iteration $k"
            return x_new
        end
        
        x = x_new
        t = t_new
    end
    
    @warn "FISTA did not converge within $max_iter iterations"
    return x
end
