library(testthat)
library(promethiumR)

test_that("wiener_filter denoises signal", {
  set.seed(42)
  
  # Clean signal
  n <- 100
  clean <- sin(seq(0, 4*pi, length.out = n))
  
  # Add noise
  noisy <- clean + rnorm(n, sd = 0.3)
  
  # Apply Wiener filter
  denoised <- wiener_filter(noisy)
  
  # Should reduce error
  error_before <- mean((noisy - clean)^2)
  error_after <- mean((denoised - clean)^2)
  
  expect_true(error_after < error_before)
})

test_that("matrix_completion_ista recovers low-rank matrix", {
  set.seed(42)
  
  # Create low-rank matrix
  n <- 20
  r <- 3  # Rank
  U <- matrix(rnorm(n * r), n, r)
  V <- matrix(rnorm(n * r), n, r)
  true_matrix <- U %*% t(V)
  
  # Create mask (50% observed)
  mask <- matrix(runif(n * n) > 0.5, n, n)
  
  # Observed matrix
  M <- true_matrix
  M[!mask] <- NA
  
  # Complete
  completed <- matrix_completion_ista(M, mask, lambda = 0.1, max_iter = 50)
  
  # Should recover reasonably well
  rel_error <- norm(completed - true_matrix, "F") / norm(true_matrix, "F")
  expect_true(rel_error < 0.5)  # Less than 50% relative error
})

test_that("compressive_sensing_fista recovers sparse signal", {
  set.seed(42)
  
  # Sparse signal
  n <- 50
  x_true <- rep(0, n)
  x_true[c(5, 15, 30)] <- c(2, -1.5, 1)  # 3 non-zero entries
  
  # Measurement
  m <- 30
  A <- matrix(rnorm(m * n), m, n)
  y <- A %*% x_true + rnorm(m, sd = 0.01)
  
  # Recover
  x_recovered <- compressive_sensing_fista(as.vector(y), A, lambda = 0.1, max_iter = 100)
  
  # Check sparsity pattern is roughly preserved
  expect_true(sum(abs(x_recovered) > 0.1) <= 10)  # Few large coefficients
})
