# =============================================================================
# 02-extract-emirt-temporal.R
# Extract emIRT N x T ideal point matrix, align to commission time steps,
# and compute per-legislator summary metrics.
# =============================================================================

cat("=== 02-extract-emirt-temporal.R ===\n")
cat("Extracting and aligning emIRT ideal points...\n\n")

base_dir <- "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking"
emirt_dir <- file.path(base_dir, "emIRT-analysis")
data_dir <- file.path(base_dir, "playground/research-proposal-implementation/data")

# =============================================================================
# 1. Load emIRT model output and metadata
# =============================================================================

cat("--- Step 1: Loading emIRT outputs ---\n")

lout <- readRDS(file.path(emirt_dir, "emIRT_model_output.rds"))
metadata <- readRDS(file.path(emirt_dir, "emIRT_metadata.rds"))

x_hat <- lout$means$x  # N x T ideal point matrix
N <- nrow(x_hat)
T_periods <- ncol(x_hat)
legislator_names <- metadata$votantes

cat(sprintf("  Legislators (N): %d\n", N))
cat(sprintf("  Time periods (T): %d\n", T_periods))

# Load bootstrap SEs if available
boot_file <- file.path(emirt_dir, "emIRT_bootstrap_output.rds")
has_bootstrap <- file.exists(boot_file)
if (has_bootstrap) {
  boot_result <- readRDS(boot_file)
  x_se <- boot_result$bse$x  # N x T bootstrap SEs
  cat("  Bootstrap SEs loaded\n")
} else {
  x_se <- matrix(NA, nrow = N, ncol = T_periods)
  cat("  No bootstrap SEs found\n")
}

# =============================================================================
# 2. Extract unique session dates from metadata
# =============================================================================

cat("\n--- Step 2: Extracting temporal structure ---\n")

# The unique dates are stored in metadata
unique_dates <- metadata$unique_dates
cat(sprintf("  Unique session dates: %d\n", length(unique_dates)))
cat(sprintf("  Date range: %s to %s\n",
            format(min(unique_dates), "%Y-%m-%d"),
            format(max(unique_dates), "%Y-%m-%d")))

# Verify dimension match
if (length(unique_dates) != T_periods) {
  cat(sprintf("  WARNING: dates (%d) != T (%d). Using sequential indices.\n",
              length(unique_dates), T_periods))
  unique_dates <- paste0("T", seq_len(T_periods))
}

# =============================================================================
# 3. Export full ideal points in long format
# =============================================================================

cat("\n--- Step 3: Exporting full ideal points (long format) ---\n")

# Vectorized construction (avoids slow nested loop)
grid <- expand.grid(period = seq_len(T_periods), legislator_idx = seq_len(N))
full_long <- data.frame(
  legislator = legislator_names[grid$legislator_idx],
  period = grid$period,
  date = format(unique_dates[grid$period], "%Y-%m-%d"),
  theta = x_hat[cbind(grid$legislator_idx, grid$period)],
  theta_se = x_se[cbind(grid$legislator_idx, grid$period)],
  stringsAsFactors = FALSE
)
# Sort by legislator then period
full_long <- full_long[order(full_long$legislator, full_long$period), ]

full_path <- file.path(data_dir, "emirt_ideal_points_full.csv")
write.csv(full_long, full_path, row.names = FALSE)
cat(sprintf("  Saved: %s (%d rows = %d legislators x %d periods)\n",
            full_path, nrow(full_long), N, T_periods))

# =============================================================================
# 4. Compute per-legislator summary metrics
# =============================================================================

cat("\n--- Step 4: Computing summary metrics ---\n")

summary_df <- data.frame(
  nombre_armonizado = legislator_names,
  theta_mean = rowMeans(x_hat),
  theta_sd = apply(x_hat, 1, sd),
  theta_min = apply(x_hat, 1, min),
  theta_max = apply(x_hat, 1, max),
  theta_range = apply(x_hat, 1, function(x) max(x) - min(x)),
  theta_first = x_hat[, 1],
  theta_last = x_hat[, T_periods],
  theta_shift = x_hat[, T_periods] - x_hat[, 1],
  mean_se = if (has_bootstrap) rowMeans(x_se, na.rm = TRUE) else NA,
  stringsAsFactors = FALSE
)

summary_path <- file.path(data_dir, "emirt_summary_metrics.csv")
write.csv(summary_df, summary_path, row.names = FALSE)
cat(sprintf("  Saved: %s (%d legislators)\n", summary_path, nrow(summary_df)))

# Print summary statistics
cat("\n  Distribution of mean positions:\n")
cat(sprintf("    Min: %.3f | Q1: %.3f | Median: %.3f | Q3: %.3f | Max: %.3f\n",
            min(summary_df$theta_mean), quantile(summary_df$theta_mean, 0.25),
            median(summary_df$theta_mean), quantile(summary_df$theta_mean, 0.75),
            max(summary_df$theta_mean)))
cat(sprintf("  Mean volatility (SD): %.3f\n", mean(summary_df$theta_sd)))
cat(sprintf("  Mean range: %.3f\n", mean(summary_df$theta_range)))

# =============================================================================
# 5. Align ideal points to commission time steps
# =============================================================================

cat("\n--- Step 5: Aligning ideal points to commission time steps ---\n")

# Commission timestamps are month-day codes from 2022
# Commission work happened roughly January-May 2022
commission_steps <- list(
  C1 = c("T0_Genesis", "03-17", "04-01", "04-18", "04-30"),
  C3 = c("T0_Genesis", "02-14", "03-01", "03-14", "03-24", "04-06", "04-19", "04-26"),
  C5 = c("T0_Genesis", "03-01", "03-16", "03-17", "04-09", "05-04")
)

# Convert commission month-day to full dates (all 2022)
to_full_date <- function(md) {
  if (grepl("Genesis", md)) return(NA)
  # Handle sub-session suffixes like "03-01-2" -> "03-01"
  parts <- strsplit(md, "-")[[1]]
  month <- parts[1]
  day <- parts[2]
  as.Date(paste0("2022-", month, "-", day))
}

# Find the nearest preceding emIRT period for a given date
find_nearest_period <- function(target_date, session_dates) {
  diffs <- as.numeric(target_date - session_dates)
  # Only consider sessions on or before the target date
  valid <- which(diffs >= 0)
  if (length(valid) == 0) return(1)  # fallback to first period
  return(valid[which.min(diffs[valid])])
}

# unique_dates is already Date class
session_dates <- unique_dates

# Pre-compute the emIRT period index for each commission step
step_index <- list()
for (comm in names(commission_steps)) {
  steps <- commission_steps[[comm]]
  indices <- integer(length(steps))
  for (s in seq_along(steps)) {
    step_label <- steps[s]
    if (grepl("Genesis", step_label)) {
      if (length(steps) > 1) {
        next_date <- to_full_date(steps[2])
        indices[s] <- find_nearest_period(next_date, session_dates)
      } else {
        indices[s] <- 1L
      }
    } else {
      indices[s] <- find_nearest_period(to_full_date(step_label), session_dates)
    }
  }
  step_index[[comm]] <- indices
}

# Build aligned data frame efficiently
aligned_parts <- list()
for (comm in names(commission_steps)) {
  steps <- commission_steps[[comm]]
  indices <- step_index[[comm]]
  for (s in seq_along(steps)) {
    pidx <- indices[s]
    aligned_parts[[length(aligned_parts) + 1]] <- data.frame(
      legislator = legislator_names,
      commission = comm,
      step = s - 1L,
      step_label = steps[s],
      emirt_period = pidx,
      emirt_date = format(session_dates[pidx], "%Y-%m-%d"),
      theta = x_hat[, pidx],
      theta_se = x_se[, pidx],
      stringsAsFactors = FALSE
    )
  }
}
aligned_df <- do.call(rbind, aligned_parts)

aligned_path <- file.path(data_dir, "emirt_aligned_to_commissions.csv")
write.csv(aligned_df, aligned_path, row.names = FALSE)
cat(sprintf("  Saved: %s (%d rows)\n", aligned_path, nrow(aligned_df)))

# Summary of alignment
cat("\n  Alignment summary:\n")
for (comm in names(commission_steps)) {
  sub <- aligned_df[aligned_df$commission == comm & aligned_df$legislator == legislator_names[1], ]
  cat(sprintf("    %s: %d steps -> emIRT periods %s\n",
              comm, nrow(sub), paste(sub$emirt_period, collapse = ", ")))
}

cat("\n--- Done ---\n")
