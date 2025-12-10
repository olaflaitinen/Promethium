# Tests for evaluation metrics

test_that("compute_snr handles identical signals", {
  traces <- matrix(rnorm(100), 10, 10)
  ref <- SeismicDataset(traces, dt = 0.004)
  est <- SeismicDataset(traces, dt = 0.004)
  
  snr <- compute_snr(ref, est)
  expect_true(snr > 90)  # Very high SNR for identical (limited by EPSILON)
})

test_that("compute_snr handles noisy signals", {
  traces <- matrix(sin(seq(0, 4*pi, length.out = 100)), 10, 10)
  ref <- SeismicDataset(traces, dt = 0.004)
  
  noisy_traces <- traces + matrix(rnorm(100) * 0.1, 10, 10)
  est <- SeismicDataset(noisy_traces, dt = 0.004)
  
  snr <- compute_snr(ref, est)
  expect_true(snr > 0)
  expect_true(snr < 50)
})

test_that("compute_mse is zero for identical signals", {
  traces <- matrix(rnorm(100), 10, 10)
  ref <- SeismicDataset(traces, dt = 0.004)
  est <- SeismicDataset(traces, dt = 0.004)
  
  expect_equal(compute_mse(ref, est), 0)
})

test_that("compute_mse is positive for different signals", {
  ref <- SeismicDataset(matrix(rnorm(100), 10, 10), dt = 0.004)
  est <- SeismicDataset(matrix(rnorm(100), 10, 10), dt = 0.004)
  
  expect_true(compute_mse(ref, est) > 0)
})

test_that("compute_psnr handles identical signals", {
  traces <- matrix(rnorm(100), 10, 10)
  ref <- SeismicDataset(traces, dt = 0.004)
  est <- SeismicDataset(traces, dt = 0.004)
  
  psnr <- compute_psnr(ref, est)
  expect_true(psnr > 100)
})

test_that("compute_ssim returns 1 for identical signals", {
  traces <- matrix(rnorm(100), 10, 10)
  ref <- SeismicDataset(traces, dt = 0.004)
  est <- SeismicDataset(traces, dt = 0.004)
  
  ssim <- compute_ssim(ref, est)
  expect_equal(ssim, 1, tolerance = 0.02)
})

test_that("compute_ssim is less than 1 for different signals", {
  ref <- SeismicDataset(matrix(rnorm(100), 10, 10), dt = 0.004)
  est <- SeismicDataset(matrix(rnorm(100), 10, 10), dt = 0.004)
  
  ssim <- compute_ssim(ref, est)
  expect_true(ssim < 1)
})

test_that("compute_relative_error is zero for identical", {
  traces <- matrix(rnorm(100), 10, 10)
  ref <- SeismicDataset(traces, dt = 0.004)
  est <- SeismicDataset(traces, dt = 0.004)
  
  expect_equal(compute_relative_error(ref, est), 0)
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
