#' Recovery Pipeline for Seismic Data
#'
#' Orchestrates preprocessing, model execution, and postprocessing.

#' Create Recovery Pipeline Configuration
#'
#' @param preprocessing List of preprocessing step names
#' @param model_type Model type: "matrix_completion", "fista", "wiener"
#' @param model_config Named list of model parameters
#' @param postprocessing List of postprocessing step names
#' @return RecoveryPipeline S3 object
#'
#' @examples
#' pipeline <- promethium_pipeline(
#'   model_type = "matrix_completion",
#'   model_config = list(lambda = 0.1, max_iter = 50)
#' )
#'
#' @export
promethium_pipeline <- function(preprocessing = c("remove_dc"),
                                model_type = "matrix_completion",
                                model_config = list(),
                                postprocessing = character(0)) {
  valid_models <- c("matrix_completion", "fista", "ista", "wiener")
  if (!model_type %in% valid_models) {
    stop("Invalid model_type: ", model_type, 
         ". Must be one of: ", paste(valid_models, collapse = ", "))
  }
  
  structure(
    list(
      preprocessing = preprocessing,
      model_type = model_type,
      model_config = model_config,
      postprocessing = postprocessing
    ),
    class = "RecoveryPipeline"
  )
}

#' @export
print.RecoveryPipeline <- function(x, ...) {
  cat("RecoveryPipeline\n")
  cat("  Preprocessing:", paste(x$preprocessing, collapse = ", "), "\n")
  cat("  Model:", x$model_type, "\n")
  if (length(x$model_config) > 0) {
    cat("  Config:", paste(names(x$model_config), "=", 
                           x$model_config, collapse = ", "), "\n")
  }
  cat("  Postprocessing:", paste(x$postprocessing, collapse = ", "), "\n")
  invisible(x)
}

#' Create Pipeline from Preset
#'
#' @param preset Preset name: "matrix_completion", "fista", "wiener"
#' @return RecoveryPipeline object
#'
#' @examples
#' pipeline <- from_preset("wiener")
#'
#' @export
from_preset <- function(preset) {
  switch(preset,
    "matrix_completion" = promethium_pipeline(
      preprocessing = c("remove_dc"),
      model_type = "matrix_completion",
      model_config = list(lambda = 0.1, max_iter = 100, tolerance = 1e-5)
    ),
    "fista" = promethium_pipeline(
      preprocessing = c("remove_dc"),
      model_type = "fista",
      model_config = list(lambda = 0.1, max_iter = 100, tolerance = 1e-5)
    ),
    "wiener" = promethium_pipeline(
      preprocessing = c("remove_dc"),
      model_type = "wiener",
      model_config = list(noise_var = NULL)
    ),
    stop("Unknown preset: ", preset)
  )
}

#' Run Recovery Pipeline
#'
#' Execute pipeline on seismic data with optional mask for missing data.
#'
#' @param pipeline RecoveryPipeline object
#' @param data SeismicDataset object
#' @param mask Logical matrix (TRUE = observed, FALSE = missing)
#' @param verbose Print progress
#' @return Recovered SeismicDataset
#'
#' @examples
#' ds <- promethium_synthetic(ntraces = 20, nsamples = 100)
#' pipeline <- from_preset("wiener")
#' result <- promethium_run(pipeline, ds)
#'
#' @export
promethium_run <- function(pipeline, data, mask = NULL, verbose = FALSE) {
  if (!inherits(pipeline, "RecoveryPipeline")) {
    stop("`pipeline` must be a RecoveryPipeline object")
  }
  if (!inherits(data, "SeismicDataset")) {
    stop("`data` must be a SeismicDataset object")
  }
  
  result <- data
  
  # Preprocessing
  for (step in pipeline$preprocessing) {
    if (verbose) message("Preprocessing: ", step)
    result <- switch(step,
      "remove_dc" = remove_dc(result),
      "normalize" = normalize(result),
      { warning("Unknown preprocessing step: ", step); result }
    )
  }
  
  # Model execution
  if (verbose) message("Running model: ", pipeline$model_type)
  
  cfg <- pipeline$model_config
  
  result$traces <- switch(pipeline$model_type,
    "matrix_completion" = {
      if (is.null(mask)) {
        mask <- matrix(TRUE, nrow = n_traces(result), ncol = n_samples(result))
      }
      matrix_completion_ista(
        observed = result$traces,
        mask = mask,
        lambda = cfg$lambda %||% 0.1,
        max_iter = cfg$max_iter %||% 100L,
        tolerance = cfg$tolerance %||% 1e-5,
        verbose = verbose
      )
    },
    "fista" = {
      # For FISTA, flatten and use identity measurement matrix
      n <- n_traces(result) * n_samples(result)
      y <- as.vector(result$traces)
      A <- diag(n)
      x_rec <- compressive_sensing_fista(
        y = y, A = A,
        lambda = cfg$lambda %||% 0.1,
        max_iter = cfg$max_iter %||% 100L,
        tolerance = cfg$tolerance %||% 1e-5,
        verbose = verbose
      )
      matrix(x_rec, nrow = n_traces(result), ncol = n_samples(result))
    },
    "ista" = {
      n <- n_traces(result) * n_samples(result)
      y <- as.vector(result$traces)
      A <- diag(n)
      x_rec <- compressive_sensing_ista(
        y = y, A = A,
        lambda = cfg$lambda %||% 0.1,
        max_iter = cfg$max_iter %||% 100L
      )
      matrix(x_rec, nrow = n_traces(result), ncol = n_samples(result))
    },
    "wiener" = {
      wiener_filter(result, noise_var = cfg$noise_var)$traces
    },
    stop("Unknown model type: ", pipeline$model_type)
  )
  
  # Postprocessing
  for (step in pipeline$postprocessing) {
    if (verbose) message("Postprocessing: ", step)
    result <- switch(step,
      "normalize" = normalize(result),
      { warning("Unknown postprocessing step: ", step); result }
    )
  }
  
  result
}

# Internal: Null-coalescing operator
# @param x Primary value
# @param y Default value if x is NULL
# @return x if not NULL, otherwise y
`%||%` <- function(x, y) {
  if (is.null(x)) y else x
}
