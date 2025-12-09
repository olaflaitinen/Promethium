# Tests for recovery algorithms

test_that("soft_threshold works correctly", {
  expect_equal(soft_threshold(5, 2), 3)
  expect_equal(soft_threshold(-5, 2), -3)
  expect_equal(soft_threshold(1, 2), 0)
  expect_equal(soft_threshold(-1, 2), 0)
})

test_that("matrix_completion_ista recovers low-rank matrix", {
  set.seed(42)
  
  # Create low-rank matrix
  U <- matrix(rnorm(20 * 2), 20, 2)
  V <- matrix(rnorm(20 * 2), 20, 2)
  M <- U %*% t(V)
  
  # Create mask (70% observed)
  mask <- matrix(runif(400) < 0.7, 20, 20)
  observed <- M * mask
  
  # Complete matrix
  completed <- matrix_completion_ista(observed, mask, lambda = 0.5, max_iter = 50)
  
  # Check dimensions preserved

  expect_equal(dim(completed), dim(M))
  
  # Check recovery quality (relative error should be reasonable)
  rel_error <- norm(completed - M, "F") / norm(M, "F")
  expect_true(rel_error < 0.5)  # Allow for some error
})

test_that("compressive_sensing_fista recovers sparse signal", {
  set.seed(42)
  
  n <- 30
  x_true <- rep(0, n)
  x_true[c(5, 15, 25)] <- c(2, -1.5, 1)
  
  m <- 20
  A <- matrix(rnorm(m * n), m, n) / sqrt(m)
  y <- A %*% x_true
  
  x_rec <- compressive_sensing_fista(y, A, lambda = 0.05, max_iter = 100)
  
  expect_length(x_rec, n)
  
  # Check sparsity pattern roughly preserved
  expect_true(abs(x_rec[5]) > 0.5)
  expect_true(abs(x_rec[15]) > 0.5)
})

test_that("compressive_sensing_ista returns correct length", {
  n <- 20
  m <- 15
  A <- matrix(rnorm(m * n), m, n)
  y <- rnorm(m)
  
  x_rec <- compressive_sensing_ista(y, A, lambda = 0.1)
  expect_length(x_rec, n)
})
