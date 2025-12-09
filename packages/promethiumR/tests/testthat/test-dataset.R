library(testthat)
library(promethiumR)

test_that("SeismicDataset constructor works", {
  traces <- matrix(rnorm(100), nrow = 10, ncol = 10)
  ds <- SeismicDataset(traces, dt = 0.004)
  
  expect_s3_class(ds, "SeismicDataset")
  expect_equal(ds$n_traces, 10)
  expect_equal(ds$n_samples, 10)
  expect_equal(ds$dt, 0.004)
})

test_that("SeismicDataset validation fails on bad input", {
  expect_error(SeismicDataset("not a matrix", dt = 0.004))
  expect_error(SeismicDataset(matrix(1:4, 2, 2), dt = -1))
})

test_that("normalize.SeismicDataset works", {
  traces <- matrix(c(1, 2, 3, 4, 5, 6), nrow = 2, ncol = 3)
  ds <- SeismicDataset(traces, dt = 0.004)
  
  ds_norm <- normalize.SeismicDataset(ds, method = "rms")
  expect_s3_class(ds_norm, "SeismicDataset")
  
  # RMS of each row should be close to 1
  rms <- sqrt(rowMeans(ds_norm$traces^2))
  expect_true(all(abs(rms - 1) < 0.01))
})

test_that("VelocityModel constructor works", {
  grid <- matrix(2000 + runif(100) * 1000, nrow = 10, ncol = 10)
  vm <- VelocityModel(grid, dx = 10, dz = 5)
  
  expect_s3_class(vm, "VelocityModel")
  expect_equal(vm$nx, 10)
  expect_equal(vm$nz, 10)
})
