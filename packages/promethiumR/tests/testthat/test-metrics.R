library(testthat)
library(promethiumR)

test_that("compute_snr works correctly", {
  reference <- c(1, 2, 3, 4, 5)
  estimate <- reference  # Perfect reconstruction
  
  snr <- compute_snr(reference, estimate)
  expect_true(snr > 100)  # Very high SNR for identical signals
})

test_that("compute_snr handles noisy estimate", {
  set.seed(42)
  reference <- rnorm(100)
  estimate <- reference + rnorm(100, sd = 0.1)
  
  snr <- compute_snr(reference, estimate)
  expect_true(snr > 10)  # Should be decent SNR
  expect_true(snr < 30)  # But not perfect
})

test_that("compute_mse is non-negative", {
  reference <- c(1, 2, 3)
  estimate <- c(1.1, 2.1, 2.9)
  
  mse <- compute_mse(reference, estimate)
  expect_true(mse >= 0)
  expect_equal(mse, mean((reference - estimate)^2))
})

test_that("compute_psnr works", {
  reference <- matrix(runif(100), 10, 10)
  estimate <- reference + rnorm(100, sd = 0.01)
  
  psnr <- compute_psnr(reference, estimate)
  expect_true(is.numeric(psnr))
  expect_true(psnr > 0)
})

test_that("compute_ssim returns value in valid range", {
  reference <- matrix(rnorm(100), 10, 10)
  estimate <- reference + rnorm(100, sd = 0.1)
  
  ssim <- compute_ssim(reference, estimate)
  expect_true(ssim >= -1 && ssim <= 1)
})

test_that("promethium_evaluate returns all metrics", {
  reference <- matrix(rnorm(100), 10, 10)
  estimate <- reference + rnorm(100, sd = 0.1)
  
  results <- promethium_evaluate(reference, estimate)
  
  expect_true("snr" %in% names(results))
  expect_true("mse" %in% names(results))
  expect_true("psnr" %in% names(results))
  expect_true("ssim" %in% names(results))
})
