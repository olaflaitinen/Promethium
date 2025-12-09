"""
Recovery algorithms for seismic data reconstruction.

Implements matrix completion (ISTA) and compressive sensing (FISTA).
"""

# ============== Soft Thresholding ==============

"""
    soft_threshold(x, tau)

Soft thresholding operator for L1 proximal.
"""
soft_threshold(x::Real, tau::Real) = sign(x) * max(abs(x) - tau, 0.0)
soft_threshold(x::AbstractArray, tau::Real) = soft_threshold.(x, tau)


# ============== Matrix Completion via ISTA ==============

"""
    matrix_completion_ista(observed, mask; kwargs...) -> Matrix

Matrix completion via Iterative Shrinkage-Thresholding Algorithm.

Solves: min_X (1/2)||P_Omega(X - M)||_F^2 + lambda ||X||_*

# Arguments
- `observed::AbstractMatrix`: Observed matrix (missing entries can be any value)
- `mask::AbstractMatrix{Bool}`: Observation mask (true = observed)

# Keyword Arguments
- `lambda::Float64=0.1`: Nuclear norm regularization
- `max_iter::Int=100`: Maximum iterations
- `tolerance::Float64=1e-5`: Convergence tolerance
- `verbose::Bool=false`: Print progress

# Returns
- `Matrix{Float64}`: Completed matrix
"""
function matrix_completion_ista(
    observed::AbstractMatrix{T},
    mask::AbstractMatrix{Bool};
    lambda::Float64 = 0.1,
    max_iter::Int = 100,
    tolerance::Float64 = 1e-5,
    verbose::Bool = false
) where {T<:Real}
    
    m, n = size(observed)
    @assert size(mask) == (m, n) "Mask dimensions must match observed"
    
    # Initialize with observed values
    X = zeros(Float64, m, n)
    for i in 1:m, j in 1:n
        if mask[i, j]
            X[i, j] = observed[i, j]
        end
    end
    
    L = 1.0  # Lipschitz constant
    
    for iter in 1:max_iter
        # Gradient step
        grad = zeros(Float64, m, n)
        for i in 1:m, j in 1:n
            if mask[i, j]
                grad[i, j] = X[i, j] - observed[i, j]
            end
        end
        
        Z = X - (1.0 / L) * grad
        
        # Proximal step: singular value soft thresholding
        U, S, V = svd(Z)
        S_thresh = soft_threshold(S, lambda / L)
        
        X_new = U * Diagonal(S_thresh) * V'
        
        # Check convergence
        rel_change = norm(X_new - X) / (norm(X) + EPSILON)
        
        if verbose && iter % 10 == 0
            println("Iter $iter: relative change = $rel_change")
        end
        
        if rel_change < tolerance
            verbose && println("Converged at iteration $iter")
            break
        end
        
        X = X_new
    end
    
    X
end


# ============== Compressive Sensing via FISTA ==============

"""
    compressive_sensing_fista(y, A; kwargs...) -> Vector

Sparse recovery via FISTA (Fast ISTA) with L1 regularization.

Solves: min_x (1/2)||Ax - y||_2^2 + lambda ||x||_1

FISTA achieves O(1/k^2) convergence rate.

# Arguments
- `y::AbstractVector`: Observation vector
- `A::AbstractMatrix`: Measurement matrix

# Keyword Arguments
- `lambda::Float64=0.1`: L1 regularization
- `max_iter::Int=100`: Maximum iterations
- `tolerance::Float64=1e-5`: Convergence tolerance
- `verbose::Bool=false`: Print progress

# Returns
- `Vector{Float64}`: Recovered sparse vector
"""
function compressive_sensing_fista(
    y::AbstractVector{T},
    A::AbstractMatrix{S};
    lambda::Float64 = 0.1,
    max_iter::Int = 100,
    tolerance::Float64 = 1e-5,
    verbose::Bool = false
) where {T<:Real, S<:Real}
    
    m, n = size(A)
    @assert length(y) == m "Observation length must match rows of A"
    
    x = zeros(Float64, n)
    z = copy(x)
    t = 1.0
    
    # Lipschitz constant estimate
    AtA = A' * A
    L = maximum(abs.(diag(AtA))) * n
    
    for iter in 1:max_iter
        # Gradient step
        grad = A' * (A * z - y)
        u = z - (1.0 / L) * grad
        
        # Proximal step (soft thresholding for L1)
        x_new = soft_threshold(u, lambda / L)
        
        # FISTA momentum
        t_new = (1.0 + sqrt(1.0 + 4.0 * t^2)) / 2.0
        z = x_new + ((t - 1.0) / t_new) * (x_new - x)
        
        # Check convergence
        rel_change = norm(x_new - x) / (norm(x) + EPSILON)
        
        if verbose && iter % 10 == 0
            println("Iter $iter: relative change = $rel_change")
        end
        
        if rel_change < tolerance
            verbose && println("Converged at iteration $iter")
            break
        end
        
        x = x_new
        t = t_new
    end
    
    x
end

"""
    compressive_sensing_ista(y, A; kwargs...) -> Vector

Standard ISTA (simpler but slower O(1/k) convergence).
"""
function compressive_sensing_ista(
    y::AbstractVector,
    A::AbstractMatrix;
    lambda::Float64 = 0.1,
    max_iter::Int = 100
)
    m, n = size(A)
    x = zeros(Float64, n)
    
    AtA = A' * A
    L = maximum(abs.(diag(AtA))) * n
    
    for iter in 1:max_iter
        grad = A' * (A * x - y)
        u = x - (1.0 / L) * grad
        x = soft_threshold(u, lambda / L)
    end
    
    x
end
