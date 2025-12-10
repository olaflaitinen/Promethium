#' Core Data Structures for promethiumR
#'
#' Defines SeismicDataset and VelocityModel S3 classes.

# ============== SeismicDataset ==============

#' Create a Seismic Dataset
#'
#' Constructor for SeismicDataset S3 class containing multi-trace seismic data.
#'
#' @param traces Numeric matrix (ntraces x nsamples) of trace data.
#' @param dt Numeric scalar, sampling interval in seconds.
#' @param coords Optional data.frame or matrix with spatial coordinates.
#' @param metadata Optional named list of metadata fields.
#'
#' @return An object of class "SeismicDataset".
#'
#' @examples
#' traces <- matrix(rnorm(1000), nrow = 10, ncol = 100)
#' ds <- SeismicDataset(traces, dt = 0.004)
#' print(ds)
#'
#' @export
SeismicDataset <- function(traces, dt, coords = NULL, metadata = list()) {
  # Input validation
  if (!is.numeric(traces) || !is.matrix(traces)) {
    stop("`traces` must be a numeric matrix")
  }
  if (!is.numeric(dt) || length(dt) != 1L || dt <= 0) {
    stop("`dt` must be a positive numeric scalar")
  }
  if (!is.null(coords) && !is.data.frame(coords) && !is.matrix(coords)) {
    stop("`coords` must be a data.frame or matrix, if provided")
  }
  if (!is.list(metadata)) {
    stop("`metadata` must be a list")
  }
  
  structure(
    list(
      traces = traces,
      dt = dt,
      coords = coords,
      metadata = metadata
    ),
    class = "SeismicDataset"
  )
}

#' @export
print.SeismicDataset <- function(x, ...) {
  cat(sprintf("SeismicDataset: %d traces, %d samples, dt=%.4fs, duration=%.3fs\n",
              nrow(x$traces), ncol(x$traces), x$dt, 
              (ncol(x$traces) - 1) * x$dt))
  invisible(x)
}

#' @export
summary.SeismicDataset <- function(object, ...) {
  traces <- object$traces
  cat("SeismicDataset Summary\n")
  cat("======================\n")
  cat(sprintf("  Traces: %d\n", nrow(traces)))
  cat(sprintf("  Samples per trace: %d\n", ncol(traces)))
  cat(sprintf("  Sampling interval: %.4f s\n", object$dt))
  cat(sprintf("  Duration: %.3f s\n", (ncol(traces) - 1) * object$dt))
  cat(sprintf("  Min value: %.4f\n", min(traces)))
  cat(sprintf("  Max value: %.4f\n", max(traces)))
  cat(sprintf("  Mean: %.4f\n", mean(traces)))
  cat(sprintf("  RMS: %.4f\n", sqrt(mean(traces^2))))
  invisible(object)
}

#' Get number of traces in dataset
#' @param x SeismicDataset object
#' @return Integer number of traces
#' @export
n_traces <- function(x) {
  UseMethod("n_traces")
}

#' @export
n_traces.SeismicDataset <- function(x) {
  nrow(x$traces)
}

#' Get number of samples per trace
#' @param x SeismicDataset object
#' @return Integer number of samples
#' @export
n_samples <- function(x) {
  UseMethod("n_samples")
}

#' @export
n_samples.SeismicDataset <- function(x) {
  ncol(x$traces)
}

#' Get time axis vector
#' @param x SeismicDataset object
#' @return Numeric vector of time values
#' @export
time_axis <- function(x) {
  UseMethod("time_axis")
}

#' @export
time_axis.SeismicDataset <- function(x) {
  seq(from = 0, by = x$dt, length.out = n_samples(x))
}

#' Normalize traces
#' 
#' @param x SeismicDataset object
#' @param method Character, normalization method: "max", "rms", or "standard"
#' @return Normalized SeismicDataset
#' @export
normalize <- function(x, method = "rms") {
  UseMethod("normalize")
}

#' @export
normalize.SeismicDataset <- function(x, method = "rms") {
  traces <- x$traces
  normalized <- matrix(0, nrow = nrow(traces), ncol = ncol(traces))
  
  for (i in seq_len(nrow(traces))) {
    row <- traces[i, ]
    
    if (method == "max") {
      max_val <- max(abs(row))
      if (max_val > 1e-10) {
        normalized[i, ] <- row / max_val
      }
    } else if (method == "rms") {
      rms <- sqrt(mean(row^2))
      if (rms > 1e-10) {
        normalized[i, ] <- row / rms
      }
    } else if (method == "standard") {
      m <- mean(row)
      s <- sd(row)
      if (s > 1e-10) {
        normalized[i, ] <- (row - m) / s
      } else {
        normalized[i, ] <- row - m
      }
    } else {
      stop("Unknown normalization method: ", method)
    }
  }
  
  x$traces <- normalized
  x
}

#' Subset traces by indices
#' 
#' @param x SeismicDataset object
#' @param indices Integer vector of trace indices
#' @return Subset SeismicDataset
#' @export
subset_traces <- function(x, indices) {
  UseMethod("subset_traces")
}

#' @export
subset_traces.SeismicDataset <- function(x, indices) {
  x$traces <- x$traces[indices, , drop = FALSE]
  if (!is.null(x$coords)) {
    if (is.data.frame(x$coords)) {
      x$coords <- x$coords[indices, , drop = FALSE]
    } else {
      x$coords <- x$coords[indices, , drop = FALSE]
    }
  }
  x
}


# ============== VelocityModel ==============

#' Create a Velocity Model
#'
#' Constructor for VelocityModel S3 class containing 2D velocity grid.
#'
#' @param velocities Numeric matrix (nz x nx) of velocity values (m/s).
#' @param dx Numeric scalar, horizontal grid spacing (m).
#' @param dz Numeric scalar, vertical grid spacing (m).
#' @param origin Numeric vector c(x0, z0) of grid origin.
#' @param metadata Optional named list of metadata fields.
#'
#' @return An object of class "VelocityModel".
#'
#' @examples
#' v <- matrix(1500, nrow = 50, ncol = 100)
#' vm <- VelocityModel(v, dx = 10, dz = 5)
#' print(vm)
#'
#' @export
VelocityModel <- function(velocities, dx, dz, origin = c(0, 0), 
                          metadata = list()) {
  # Input validation
  if (!is.numeric(velocities) || !is.matrix(velocities)) {
    stop("`velocities` must be a numeric matrix")
  }
  if (!is.numeric(dx) || length(dx) != 1L || dx <= 0) {
    stop("`dx` must be a positive numeric scalar")
  }
  if (!is.numeric(dz) || length(dz) != 1L || dz <= 0) {
    stop("`dz` must be a positive numeric scalar")
  }
  
  structure(
    list(
      velocities = velocities,
      dx = dx,
      dz = dz,
      origin = origin,
      metadata = metadata
    ),
    class = "VelocityModel"
  )
}

#' @export
print.VelocityModel <- function(x, ...) {
  cat(sprintf("VelocityModel: %dx%d, v=%.0f-%.0f m/s\n",
              nrow(x$velocities), ncol(x$velocities),
              min(x$velocities), max(x$velocities)))
  invisible(x)
}

#' Create constant velocity model
#' @param velocity Constant velocity value (m/s)
#' @param nx Number of horizontal points
#' @param nz Number of vertical points
#' @param dx Horizontal spacing (m)
#' @param dz Vertical spacing (m)
#' @return VelocityModel object
#' @export
constant_velocity <- function(velocity, nx, nz, dx, dz) {
  v <- matrix(velocity, nrow = nz, ncol = nx)
  VelocityModel(v, dx, dz)
}

#' Create linear velocity gradient model
#' @param v0 Surface velocity (m/s)
#' @param gradient Velocity gradient (1/s)
#' @param nx Number of horizontal points
#' @param nz Number of vertical points
#' @param dx Horizontal spacing (m)
#' @param dz Vertical spacing (m)
#' @return VelocityModel object
#' @export
linear_velocity <- function(v0, gradient, nx, nz, dx, dz) {
  v <- matrix(0, nrow = nz, ncol = nx)
  for (i in seq_len(nz)) {
    v[i, ] <- v0 + gradient * (i - 1) * dz
  }
  VelocityModel(v, dx, dz)
}

#' Bilinear interpolation of velocity at position
#' @param vm VelocityModel object
#' @param x Horizontal position (m)
#' @param z Vertical position (m)
#' @return Interpolated velocity value
#' @export
interpolate_at <- function(vm, x, z) {
  x0 <- vm$origin[1]
  z0 <- vm$origin[2]
  
  ix <- (x - x0) / vm$dx
  iz <- (z - z0) / vm$dz
  
  nz <- nrow(vm$velocities)
  nx <- ncol(vm$velocities)
  
  i0 <- max(1, min(nz - 1, floor(iz) + 1))
  j0 <- max(1, min(nx - 1, floor(ix) + 1))
  i1 <- i0 + 1
  j1 <- j0 + 1
  
  fx <- ix - (j0 - 1)
  fz <- iz - (i0 - 1)
  
  v00 <- vm$velocities[i0, j0]
  v01 <- vm$velocities[i0, j1]
  v10 <- vm$velocities[i1, j0]
  v11 <- vm$velocities[i1, j1]
  
  (1 - fx) * (1 - fz) * v00 +
  fx * (1 - fz) * v01 +
  (1 - fx) * fz * v10 +
  fx * fz * v11
}
