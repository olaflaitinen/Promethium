#' promethiumR: Advanced Seismic Data Recovery and Reconstruction Framework
#'
#' Native R implementation of the Promethium framework for seismic data
#' recovery and reconstruction. Part of the multi-language Promethium ecosystem
#' with consistent implementations in Python, Julia, and Scala.
#'
#' @section Core Functions:
#' \itemize{
#'   \item \code{\link{SeismicDataset}}: Create seismic dataset objects
#'   \item \code{\link{VelocityModel}}: Create velocity model objects
#'   \item \code{\link{promethium_pipeline}}: Create recovery pipelines
#'   \item \code{\link{promethium_run}}: Execute recovery pipelines
#' }
#'
#' @section Algorithms:
#' \itemize{
#'   \item \code{\link{wiener_filter}}: Wiener filter denoising
#'   \item \code{\link{bandpass_filter}}: Frequency-domain bandpass filter
#'   \item \code{\link{matrix_completion_ista}}: ISTA matrix completion
#'   \item \code{\link{compressive_sensing_fista}}: FISTA sparse recovery
#' }
#'
#' @section Evaluation:
#' \itemize{
#'   \item \code{\link{compute_snr}}: Signal-to-Noise Ratio
#'   \item \code{\link{compute_mse}}: Mean Squared Error
#'   \item \code{\link{compute_psnr}}: Peak SNR
#'   \item \code{\link{compute_ssim}}: Structural Similarity Index
#' }
#'
#' @docType package
#' @name promethiumR-package
#' @aliases promethiumR
NULL

#' Package version
#' @export
PROMETHIUM_VERSION <- "1.0.4"
