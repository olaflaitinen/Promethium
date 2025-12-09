#' promethiumR: Advanced Seismic Data Recovery Framework
#'
#' Native R implementation of the Promethium seismic data recovery framework.
#' Provides algorithms for denoising, interpolation, matrix completion, and
#' deep learning-based reconstruction.
#'
#' @section Core Types:
#' \itemize{
#'   \item \code{\link{SeismicDataset}}: Container for seismic trace data
#'   \item \code{\link{VelocityModel}}: Velocity model representation
#'   \item \code{\link{RecoveryPipeline}}: Processing pipeline configuration
#' }
#'
#' @section Algorithms:
#' \itemize{
#'   \item \code{\link{wiener_filter}}: Frequency-domain Wiener denoising
#'   \item \code{\link{matrix_completion_ista}}: Nuclear norm matrix completion
#'   \item \code{\link{compressive_sensing_fista}}: L1-regularized recovery
#' }
#'
#' @section Evaluation:
#' \itemize{
#'   \item \code{\link{compute_snr}}: Signal-to-Noise Ratio
#'   \item \code{\link{compute_mse}}: Mean Squared Error
#'   \item \code{\link{compute_psnr}}: Peak SNR
#' }
#'
#' @docType package
#' @name promethiumR
"_PACKAGE"

# Package version aligned with global Promethium spec
.promethium_version <- "1.0.4"
