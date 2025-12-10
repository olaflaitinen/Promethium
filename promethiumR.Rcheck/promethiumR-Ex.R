pkgname <- "promethiumR"
source(file.path(R.home("share"), "R", "examples-header.R"))
options(warn = 1)
options(pager = "console")
base::assign(".ExTimings", "promethiumR-Ex.timings", pos = 'CheckExEnv')
base::cat("name\tuser\tsystem\telapsed\n", file=base::get(".ExTimings", pos = 'CheckExEnv'))
base::assign(".format_ptime",
function(x) {
  if(!is.na(x[4L])) x[1L] <- x[1L] + x[4L]
  if(!is.na(x[5L])) x[2L] <- x[2L] + x[5L]
  options(OutDec = '.')
  format(x[1L:3L], digits = 7L)
},
pos = 'CheckExEnv')

### * </HEADER>
library('promethiumR')

base::assign(".oldSearch", base::search(), pos = 'CheckExEnv')
base::assign(".old_wd", base::getwd(), pos = 'CheckExEnv')
cleanEx()
nameEx("SeismicDataset")
### * SeismicDataset

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: SeismicDataset
### Title: Core Data Structures for promethiumR
### Aliases: SeismicDataset

### ** Examples

traces <- matrix(rnorm(1000), nrow = 10, ncol = 100)
ds <- SeismicDataset(traces, dt = 0.004)
print(ds)




base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("SeismicDataset", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("VelocityModel")
### * VelocityModel

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: VelocityModel
### Title: Create a Velocity Model
### Aliases: VelocityModel

### ** Examples

v <- matrix(1500, nrow = 50, ncol = 100)
vm <- VelocityModel(v, dx = 10, dz = 5)
print(vm)




base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("VelocityModel", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("bandpass_filter")
### * bandpass_filter

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: bandpass_filter
### Title: Bandpass Filter
### Aliases: bandpass_filter bandpass_filter.numeric
###   bandpass_filter.SeismicDataset

### ** Examples

ds <- promethium_synthetic(ntraces = 10, nsamples = 100)
filtered <- bandpass_filter(ds, low_freq = 5, high_freq = 80)




base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("bandpass_filter", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("compressive_sensing_fista")
### * compressive_sensing_fista

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: compressive_sensing_fista
### Title: Compressive Sensing via FISTA
### Aliases: compressive_sensing_fista

### ** Examples

# Sparse signal
n <- 50
x_true <- rep(0, n)
x_true[c(5, 15, 30)] <- c(2, -1.5, 1)

# Measurement
m <- 30
A <- matrix(rnorm(m * n), m, n)
y <- A %*% x_true + rnorm(m) * 0.01

# Recover
x_rec <- compressive_sensing_fista(y, A, lambda = 0.1)




base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("compressive_sensing_fista", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("compute_snr")
### * compute_snr

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: compute_snr
### Title: Compute Signal-to-Noise Ratio
### Aliases: compute_snr

### ** Examples

ref <- SeismicDataset(matrix(rnorm(100), 10, 10), dt = 0.004)
est <- SeismicDataset(ref$traces + 0.1 * rnorm(100), dt = 0.004)
snr <- compute_snr(ref, est)




base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("compute_snr", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("from_preset")
### * from_preset

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: from_preset
### Title: Create Pipeline from Preset
### Aliases: from_preset

### ** Examples

pipeline <- from_preset("wiener")




base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("from_preset", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("matrix_completion_ista")
### * matrix_completion_ista

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: matrix_completion_ista
### Title: Matrix Completion via ISTA
### Aliases: matrix_completion_ista

### ** Examples

# Create low-rank matrix
U <- matrix(rnorm(20 * 3), 20, 3)
V <- matrix(rnorm(20 * 3), 20, 3)
M <- U %*% t(V)

# Create mask (60% observed)
mask <- matrix(runif(400) < 0.6, 20, 20)
observed <- M * mask

# Complete matrix
completed <- matrix_completion_ista(observed, mask, lambda = 0.1)




base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("matrix_completion_ista", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("promethium_evaluate")
### * promethium_evaluate

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: promethium_evaluate
### Title: Evaluate All Metrics
### Aliases: promethium_evaluate

### ** Examples

ref <- SeismicDataset(matrix(rnorm(100), 10, 10), dt = 0.004)
est <- SeismicDataset(ref$traces + 0.1 * rnorm(100), dt = 0.004)
metrics <- promethium_evaluate(ref, est)




base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("promethium_evaluate", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("promethium_pipeline")
### * promethium_pipeline

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: promethium_pipeline
### Title: Recovery Pipeline for Seismic Data
### Aliases: promethium_pipeline

### ** Examples

pipeline <- promethium_pipeline(
  model_type = "matrix_completion",
  model_config = list(lambda = 0.1, max_iter = 50)
)




base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("promethium_pipeline", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("promethium_run")
### * promethium_run

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: promethium_run
### Title: Run Recovery Pipeline
### Aliases: promethium_run

### ** Examples

ds <- promethium_synthetic(ntraces = 20, nsamples = 100)
pipeline <- from_preset("wiener")
result <- promethium_run(pipeline, ds)




base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("promethium_run", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("promethium_synthetic")
### * promethium_synthetic

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: promethium_synthetic
### Title: I/O Functions for Seismic Data Formats
### Aliases: promethium_synthetic

### ** Examples

ds <- promethium_synthetic(ntraces = 50, nsamples = 200, seed = 42)
print(ds)




base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("promethium_synthetic", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("wiener_filter")
### * wiener_filter

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: wiener_filter
### Title: Signal Processing Functions for Seismic Data
### Aliases: wiener_filter wiener_filter.numeric
###   wiener_filter.SeismicDataset

### ** Examples

signal <- sin(seq(0, 10*pi, length.out = 100)) + rnorm(100) * 0.3
denoised <- wiener_filter(signal)




base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("wiener_filter", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
### * <FOOTER>
###
cleanEx()
options(digits = 7L)
base::cat("Time elapsed: ", proc.time() - base::get("ptime", pos = 'CheckExEnv'),"\n")
grDevices::dev.off()
###
### Local variables: ***
### mode: outline-minor ***
### outline-regexp: "\\(> \\)?### [*]+" ***
### End: ***
quit('no')
