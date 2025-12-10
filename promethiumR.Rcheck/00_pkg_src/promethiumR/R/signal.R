#' Signal Processing Functions for Seismic Data
#'
#' Provides Wiener filter, bandpass filter, and DC offset removal.

#' Wiener Filter for Noise Attenuation
#'
#' Apply frequency-domain Wiener filter to signal.
#' H(f) = Pxx(f) / (Pxx(f) + Pnn(f))
#'
#' @param x Numeric vector (single trace) or SeismicDataset
#' @param noise_var Noise variance estimate (NULL for auto-estimate)
#' @return Filtered signal/dataset of same type as input
#'
#' @examples
#' signal <- sin(seq(0, 10*pi, length.out = 100)) + rnorm(100) * 0.3
#' denoised <- wiener_filter(signal)
#'
#' @export
wiener_filter <- function(x, noise_var = NULL) {
  UseMethod("wiener_filter")
}

#' @rdname wiener_filter
#' @export
wiener_filter.numeric <- function(x, noise_var = NULL) {
  n <- length(x)
  
  # FFT
  Y <- fft(x)
  Py <- Mod(Y)^2 / n
  
  # Estimate noise PSD
  if (is.null(noise_var)) {
    tail_start <- floor(n / 2)
    Pn <- rep(mean(Py[tail_start:n]), n)
  } else {
    Pn <- rep(noise_var, n)
  }
  
  # Wiener filter
  Ps <- pmax(Py - Pn, 0)
  H <- (Ps + EPSILON) / (Ps + Pn + EPSILON)
  
  # Apply filter
  Y_filtered <- Y * H
  
  # Inverse FFT
  Re(fft(Y_filtered, inverse = TRUE) / n)
}

#' @rdname wiener_filter
#' @export
wiener_filter.SeismicDataset <- function(x, noise_var = NULL) {
  result <- matrix(0, nrow = n_traces(x), ncol = n_samples(x))
  
  for (i in seq_len(n_traces(x))) {
    result[i, ] <- wiener_filter.numeric(x$traces[i, ], noise_var)
  }
  
  x$traces <- result
  x
}

#' Bandpass Filter
#'
#' Apply frequency-domain bandpass filter with cosine taper.
#'
#' @param x Numeric vector or SeismicDataset
#' @param dt Sampling interval (required for vectors)
#' @param low_freq Low cutoff frequency (Hz)
#' @param high_freq High cutoff frequency (Hz)
#' @param taper_width Taper width in Hz for smooth rolloff
#' @return Filtered signal/dataset
#'
#' @examples
#' ds <- promethium_synthetic(ntraces = 10, nsamples = 100)
#' filtered <- bandpass_filter(ds, low_freq = 5, high_freq = 80)
#'
#' @export
bandpass_filter <- function(x, dt = NULL, low_freq, high_freq, 
                            taper_width = 5) {
  UseMethod("bandpass_filter")
}

#' @rdname bandpass_filter
#' @export
bandpass_filter.numeric <- function(x, dt, low_freq, high_freq, 
                                    taper_width = 5) {
  if (is.null(dt)) stop("`dt` is required for numeric input")
  
  n <- length(x)
  X <- fft(x)
  df <- 1 / (n * dt)
  
  # Create bandpass mask with cosine taper
  mask <- rep(0, n)
  
  for (i in seq_len(n)) {
    freq <- if (i <= floor(n/2) + 1) (i - 1) * df else (i - 1 - n) * df
    abs_freq <- abs(freq)
    
    if (abs_freq >= low_freq && abs_freq <= high_freq) {
      mask[i] <- 1
    } else if (abs_freq >= low_freq - taper_width && abs_freq < low_freq) {
      mask[i] <- 0.5 * (1 + cos(pi * (low_freq - abs_freq) / taper_width))
    } else if (abs_freq > high_freq && abs_freq <= high_freq + taper_width) {
      mask[i] <- 0.5 * (1 + cos(pi * (abs_freq - high_freq) / taper_width))
    }
  }
  
  X_filtered <- X * mask
  Re(fft(X_filtered, inverse = TRUE) / n)
}

#' @rdname bandpass_filter
#' @export
bandpass_filter.SeismicDataset <- function(x, dt = NULL, low_freq, high_freq,
                                           taper_width = 5) {
  result <- matrix(0, nrow = n_traces(x), ncol = n_samples(x))
  
  for (i in seq_len(n_traces(x))) {
    result[i, ] <- bandpass_filter.numeric(
      x$traces[i, ], x$dt, low_freq, high_freq, taper_width
    )
  }
  
  x$traces <- result
  x
}

#' Remove DC Offset
#'
#' Remove mean (DC component) from signal.
#'
#' @param x Numeric vector or SeismicDataset
#' @return Signal with zero mean
#'
#' @export
remove_dc <- function(x) {
  UseMethod("remove_dc")
}

#' @rdname remove_dc
#' @export
remove_dc.numeric <- function(x) {
  x - mean(x)
}

#' @rdname remove_dc
#' @export
remove_dc.SeismicDataset <- function(x) {
  result <- matrix(0, nrow = n_traces(x), ncol = n_samples(x))
  
  for (i in seq_len(n_traces(x))) {
    result[i, ] <- x$traces[i, ] - mean(x$traces[i, ])
  }
  
  x$traces <- result
  x
}
