# Tests for promethiumR core functionality

test_that("SeismicDataset creation works", {
  traces <- matrix(rnorm(100), nrow = 10, ncol = 10)
  ds <- SeismicDataset(traces, dt = 0.004)
  
  expect_s3_class(ds, "SeismicDataset")
  expect_equal(n_traces(ds), 10)
  expect_equal(n_samples(ds), 10)
  expect_equal(ds$dt, 0.004)
})

test_that("SeismicDataset validation rejects invalid input", {
  expect_error(SeismicDataset("not a matrix", dt = 0.004))
  expect_error(SeismicDataset(matrix(1:4, 2, 2), dt = -1))
})

test_that("time_axis computes correctly", {
  ds <- SeismicDataset(matrix(1:20, 4, 5), dt = 0.001)
  t <- time_axis(ds)
  
  expect_length(t, 5)
  expect_equal(t[1], 0)
  expect_equal(t[5], 0.004)
})

test_that("normalize works for different methods", {
  ds <- SeismicDataset(matrix(1:20, 4, 5), dt = 0.001)
  
  ds_max <- normalize(ds, method = "max")
  expect_true(max(abs(ds_max$traces)) <= 1)
  
  ds_std <- normalize(ds, method = "standard")
  expect_true(abs(mean(ds_std$traces)) < 1e-10)
})

test_that("VelocityModel creation works", {
  vm <- constant_velocity(10, 10, 100, 100, 1500)
  
  expect_s3_class(vm, "VelocityModel")
  expect_equal(nrow(vm$velocities), 10)
  expect_equal(ncol(vm$velocities), 10)
  expect_true(all(vm$velocities == 1500))
})

test_that("linear_velocity creates gradient", {
  vm <- linear_velocity(5, 5, 100, 100, 1500, 3000)
  
  expect_s3_class(vm, "VelocityModel")
  expect_equal(vm$velocities[1, 1], 1500)
  expect_equal(vm$velocities[5, 5], 3000)
})
