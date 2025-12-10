# Tests for pipeline functionality

test_that("promethium_pipeline creates valid object", {
  pipeline <- promethium_pipeline(model_type = "wiener")
  
  expect_s3_class(pipeline, "RecoveryPipeline")
  expect_equal(pipeline$model_type, "wiener")
})

test_that("from_preset returns valid pipelines", {
  mc <- from_preset("matrix_completion")
  expect_s3_class(mc, "RecoveryPipeline")
  expect_equal(mc$model_type, "matrix_completion")
  
  fista <- from_preset("fista")
  expect_s3_class(fista, "RecoveryPipeline")
  expect_equal(fista$model_type, "fista")
  
  wiener <- from_preset("wiener")
  expect_s3_class(wiener, "RecoveryPipeline")
  expect_equal(wiener$model_type, "wiener")
})

test_that("from_preset rejects unknown preset", {
  expect_error(from_preset("unknown"))
})

test_that("promethium_run executes wiener pipeline", {
  ds <- promethium_synthetic(ntraces = 5, nsamples = 50, seed = 42)
  pipeline <- from_preset("wiener")
  
  result <- promethium_run(pipeline, ds)
  
  expect_s3_class(result, "SeismicDataset")
  expect_equal(n_traces(result), 5)
  expect_equal(n_samples(result), 50)
})

test_that("promethium_run validates inputs", {
  ds <- promethium_synthetic(ntraces = 5, nsamples = 50)
  
  expect_error(promethium_run("not a pipeline", ds))
  expect_error(promethium_run(from_preset("wiener"), "not a dataset"))
})
