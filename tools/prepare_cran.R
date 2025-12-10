# Helper script to prepare promethiumR for CRAN submission
# Run this script in R: source("tools/prepare_cran.R")

if (!requireNamespace("devtools", quietly = TRUE)) {
  install.packages("devtools")
}
if (!requireNamespace("roxygen2", quietly = TRUE)) {
  install.packages("roxygen2")
}

pkg_path <- "packages/promethiumR"

cat("=== 1. Generating Documentation (roxygen2) ===\n")
devtools::document(pkg_path)

cat("\n=== 2. Running R CMD check (CRAN strict) ===\n")
# Using --as-cran for strict checking
devtools::check(pkg_path, remote = TRUE, manual = TRUE, cran = TRUE)

cat("\n=== 3. Building Source Package ===\n")
built_path <- devtools::build(pkg_path)

cat(sprintf("\n\nSUCCESS! Package built at:\n%s\n", built_path))
cat("If step 2 passed with 0 ERRORs, 0 WARNINGs, and 0 NOTEs, you are ready to submit.\n")
cat("Upload the .tar.gz file to: https://xmpalantir.wu.ac.at/cransubmit/\n")
