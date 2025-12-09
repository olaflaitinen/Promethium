# Tests for evaluation metrics

test_that("compute_snr handles identical signals", {
  x <- rnorm(100)
  snr <- compute_snr(x, x)
  expect_true(snr > 100)  # Very high SNR for identical
})

test_that("compute_snr handles noisy signals", {
  original <- sin(seq(0, 4*pi, length.out = 100))
  noisy <- original + rnorm(100) * 0.1
  
  snr <- compute_snr(original, noisy)
  expect_true(snr > 0)
  expect_true(snr < 50)
})

test_that("compute_mse is zero for identical signals", {
  x <- rnorm(100)
  expect_equal(compute_mse(x, x), 0)
})

test_that("compute_mse is positive for different signals", {
  x <- rnorm(100)
  y <- rnorm(100)
  expect_true(compute_mse(x, y) > 0)
})

test_that("compute_psnr handles identical signals", {
  x <- rnorm(100)
  psnr <- compute_psnr(x, x)
  expect_true(psnr > 100)
})

test_that("compute_ssim returns 1 for identical signals", {
  x <- matrix(rnorm(100), 10, 10)
  ssim <- compute_ssim(x, x)
  expect_equal(ssim, 1, tolerance = 1e-6)
})

test_that("compute_ssim is less than 1 for different signals", {
  x <- matrix(rnorm(100), 10, 10)
  y <- matrix(rnorm(100), 10, 10)
  ssim <- compute_ssim(x, y)
  expect_true(ssim < 1)
})

test_that("compute_relative_error is zero for identical", {
  x <- rnorm(100)
  expect_equal(compute_relative_error(x, x), 0)
})

test_that("promethium_evaluate returns all metrics", {
  original <- promethium_synthetic(10, 50, seed = 42)
  recovered <- original
  recovered$traces <- original$traces + rnorm(500) * 0.1
  
  metrics <- promethium_evaluate(original, recovered)
  
  expect_type(metrics, "list")
  expect_true("snr" %in% names(metrics))
  expect_true("mse" %in% names(metrics))
  expect_true("psnr" %in% names(metrics))
  expect_true("ssim" %in% names(metrics))
})
