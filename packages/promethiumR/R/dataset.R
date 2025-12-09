#' SeismicDataset Constructor
#'
#' Create a new SeismicDataset object containing seismic trace data.
#'
#' @param traces Numeric matrix (n_traces x n_samples)
#' @param dt Sampling interval in seconds
#' @param coords Optional data frame with spatial coordinates
#' @param metadata Named list of metadata key-value pairs
#' @return SeismicDataset S3 object
#' @export
#' @examples
#' traces <- matrix(rnorm(1000), nrow = 10, ncol = 100)
#' ds <- SeismicDataset(traces, dt = 0.004)
#' print(ds)
SeismicDataset <- function(traces, dt, coords = NULL, metadata = list()) {
  stopifnot(is.matrix(traces), is.numeric(dt), dt > 0)
  
  structure(
    list(
      traces = traces,
      dt = dt,
      coords = coords,
      metadata = metadata,
      n_traces = nrow(traces),
      n_samples = ncol(traces)
    ),
    class = "SeismicDataset"
  )
}

#' @export
print.SeismicDataset <- function(x, ...) {
  cat("SeismicDataset:\n")
  cat(sprintf("  Traces: %d x %d\n", x$n_traces, x$n_samples))
  cat(sprintf("  Sampling: %.4f s (%.1f Hz)\n", x$dt, 1/x$dt))
  cat(sprintf("  Duration: %.3f s\n", x$n_samples * x$dt))
  if (!is.null(x$coords)) {
    cat(sprintf("  Coords: %d fields\n", ncol(x$coords)))
  }
  invisible(x)
}

#' Normalize SeismicDataset traces
#' 
#' @param x SeismicDataset object
#' @param method Normalization method: "rms", "max", or "std"
#' @return New SeismicDataset with normalized traces
#' @export
normalize.SeismicDataset <- function(x, method = "rms") {
  if (method == "rms") {
    rms <- sqrt(rowMeans(x$traces^2))
    normalized <- x$traces / (rms + 1e-10)
  } else if (method == "max") {
    normalized <- x$traces / (max(abs(x$traces)) + 1e-10)
  } else if (method == "std") {
    normalized <- scale(t(x$traces))
    normalized <- t(normalized)
  } else {
    stop(sprintf("Unknown normalization method: %s", method))
  }
  SeismicDataset(normalized, x$dt, x$coords, x$metadata)
}

#' Subset SeismicDataset
#' 
#' @param x SeismicDataset object
#' @param trace_idx Trace indices to keep
#' @param sample_idx Sample indices to keep
#' @return Subsetted SeismicDataset
#' @export
subset.SeismicDataset <- function(x, trace_idx = NULL, sample_idx = NULL, ...) {
  traces <- x$traces
  coords <- x$coords
  
  if (!is.null(trace_idx)) {
    traces <- traces[trace_idx, , drop = FALSE]
    if (!is.null(coords)) coords <- coords[trace_idx, , drop = FALSE]
  }
  if (!is.null(sample_idx)) {
    traces <- traces[, sample_idx, drop = FALSE]
  }
  
  SeismicDataset(traces, x$dt, coords, x$metadata)
}


#' VelocityModel Constructor
#'
#' Create a velocity model for seismic processing.
#'
#' @param grid Numeric matrix of velocity values (m/s)
#' @param dx Horizontal grid spacing (m)
#' @param dz Vertical grid spacing (m)
#' @param origin Two-element vector (x0, z0) for grid origin
#' @param metadata Named list of metadata
#' @return VelocityModel S3 object
#' @export
VelocityModel <- function(grid, dx, dz, origin = c(0, 0), metadata = list()) {
  stopifnot(is.matrix(grid), dx > 0, dz > 0)
  
  structure(
    list(
      grid = grid,
      dx = dx,
      dz = dz,
      origin = origin,
      nx = ncol(grid),
      nz = nrow(grid),
      metadata = metadata
    ),
    class = "VelocityModel"
  )
}

#' @export
print.VelocityModel <- function(x, ...) {
  cat("VelocityModel:\n")
  cat(sprintf("  Grid: %d x %d\n", x$nz, x$nx))
  cat(sprintf("  Spacing: dx=%.1f m, dz=%.1f m\n", x$dx, x$dz))
  cat(sprintf("  Velocity range: %.0f - %.0f m/s\n", min(x$grid), max(x$grid)))
  invisible(x)
}
