# =============================================================================
# 07-model-spatial-durbin.R
# Model 3: Legislative Success — Spatial Durbin Model (SDM)
#
# y = rho*W*y + X*beta + W*X*theta + epsilon
#
# y = mean TF-IDF retention score
# W = row-normalized pooled co-authorship matrix
# X = individual + network + ideological covariates
# =============================================================================

cat("=== 07-model-spatial-durbin.R ===\n")
cat("Model 3: Spatial Durbin Model for Legislative Success\n\n")

if (!requireNamespace("spdep", quietly = TRUE)) install.packages("spdep", repos = "http://cran.us.r-project.org")
if (!requireNamespace("spatialreg", quietly = TRUE)) install.packages("spatialreg", repos = "http://cran.us.r-project.org")

library(spdep)
library(spatialreg)

set.seed(42)

base_dir <- "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking"
data_dir <- file.path(base_dir, "playground/research-proposal-implementation/data")

# =============================================================================
# 1. Load data
# =============================================================================

cat("--- Step 1: Loading data ---\n")

dataset <- read.csv(file.path(data_dir, "integrated_dataset.csv"),
                    stringsAsFactors = FALSE)
edges <- read.csv(file.path(data_dir, "pooled_cumulative_network.csv"),
                  stringsAsFactors = FALSE)

cat(sprintf("  Dataset: %d rows, %d columns\n", nrow(dataset), ncol(dataset)))
cat(sprintf("  Edges: %d\n", nrow(edges)))

# =============================================================================
# 2. Filter to complete cases for SDM
# =============================================================================

cat("\n--- Step 2: Filtering to complete cases ---\n")

# Only convencionales with: success score, ideology, network, profile
# Also ensure all model covariates are non-missing
complete <- dataset[!is.na(dataset$mean_tfidf_retention) &
                    !is.na(dataset$theta_mean) &
                    !is.na(dataset$theta_sd) &
                    !is.na(dataset$es_mujer) &
                    !is.na(dataset$es_abogado) &
                    !is.na(dataset$experiencia_previa_institucional) &
                    !is.na(dataset$edad_al_asumir) &
                    !is.na(dataset$ego_heterophily) &
                    dataset$degree > 0, ]
cat(sprintf("  Complete cases: %d (from %d)\n", nrow(complete), nrow(dataset)))

# =============================================================================
# 3. Build spatial weight matrix W
# =============================================================================

cat("\n--- Step 3: Building spatial weight matrix ---\n")

# Build NxN adjacency matrix for the complete-case sample
sample_names <- complete$nombre_armonizado
n <- length(sample_names)

W_raw <- matrix(0, nrow = n, ncol = n,
                dimnames = list(sample_names, sample_names))

for (i in seq_len(nrow(edges))) {
  s <- edges$source[i]
  t <- edges$target[i]
  w <- edges$weight[i]
  if (s %in% sample_names && t %in% sample_names) {
    W_raw[s, t] <- w
    W_raw[t, s] <- w
  }
}

# Row-normalize
row_sums <- rowSums(W_raw)
# Handle isolates (shouldn't exist since we filtered degree > 0)
row_sums[row_sums == 0] <- 1
W_norm <- W_raw / row_sums

cat(sprintf("  W matrix: %d x %d\n", n, n))
cat(sprintf("  Non-zero entries: %d\n", sum(W_raw > 0)))
cat(sprintf("  Mean row sum (pre-normalization): %.1f\n", mean(rowSums(W_raw))))

# Convert to listw object for spatial regression
# Use zero.policy=TRUE to handle any remaining isolates gracefully
W_listw <- mat2listw(W_norm, style = "W")
set.ZeroPolicyOption(TRUE)

# =============================================================================
# 4. Moran's I test for spatial dependence
# =============================================================================

cat("\n--- Step 4: Moran's I test ---\n")

moran_result <- moran.test(complete$mean_tfidf_retention, W_listw)
cat(sprintf("  Moran's I: %.4f\n", moran_result$estimate[1]))
cat(sprintf("  Expected:  %.4f\n", moran_result$estimate[2]))
cat(sprintf("  z-score:   %.4f\n", moran_result$statistic))
cat(sprintf("  p-value:   %.6f\n", moran_result$p.value))
cat(sprintf("  Interpretation: %s\n",
            ifelse(moran_result$p.value < 0.05,
                   "Significant spatial autocorrelation -> spatial model justified",
                   "No significant spatial autocorrelation")))

# =============================================================================
# 5. OLS baseline
# =============================================================================

cat("\n--- Step 5: OLS Baseline ---\n")

formula_base <- mean_tfidf_retention ~ degree + betweenness +
  es_abogado + experiencia_previa_institucional + es_mujer +
  edad_al_asumir + theta_mean + theta_sd + ego_heterophily

mod_ols <- lm(formula_base, data = complete)
cat("  OLS Summary:\n")
print(summary(mod_ols))

# LM tests for spatial dependence
cat("\n  Lagrange Multiplier tests:\n")
tryCatch({
  lm_tests <- lm.RStests(mod_ols, W_listw,
                          test = c("RSerr", "RSlag", "adjRSerr", "adjRSlag", "SARMA"))
  print(lm_tests)
}, error = function(e) {
  cat("  LM tests could not be computed:", e$message, "\n")
  cat("  Proceeding with spatial models based on Moran's I result.\n")
})

# =============================================================================
# 6. Spatial models
# =============================================================================

cat("\n--- Step 6: Spatial Models ---\n")

# SAR (Spatial Autoregressive / Spatial Lag)
cat("\n  [A] SAR (Spatial Lag):\n")
tryCatch({
  mod_sar <- lagsarlm(formula_base, data = complete, listw = W_listw)
  print(summary(mod_sar))
}, error = function(e) cat("  Error:", e$message, "\n"))

# SEM (Spatial Error Model)
cat("\n  [B] SEM (Spatial Error):\n")
tryCatch({
  mod_sem <- errorsarlm(formula_base, data = complete, listw = W_listw)
  print(summary(mod_sem))
}, error = function(e) cat("  Error:", e$message, "\n"))

# SDM (Spatial Durbin Model = SAR + WX terms)
cat("\n  [C] SDM (Spatial Durbin):\n")
tryCatch({
  mod_sdm <- lagsarlm(formula_base, data = complete, listw = W_listw,
                       type = "mixed")
  print(summary(mod_sdm))

  # Direct, indirect, and total effects
  cat("\n  SDM Impacts (direct/indirect/total):\n")
  imp <- impacts(mod_sdm, listw = W_listw, R = 500)
  print(summary(imp, zstats = TRUE))
}, error = function(e) cat("  Error:", e$message, "\n"))

# =============================================================================
# 7. Model comparison
# =============================================================================

cat("\n--- Step 7: Model Comparison ---\n")

models <- list()
models[["OLS"]] <- c(AIC = AIC(mod_ols), logLik = as.numeric(logLik(mod_ols)))
if (exists("mod_sar")) models[["SAR"]] <- c(AIC = AIC(mod_sar), logLik = as.numeric(logLik(mod_sar)))
if (exists("mod_sem")) models[["SEM"]] <- c(AIC = AIC(mod_sem), logLik = as.numeric(logLik(mod_sem)))
if (exists("mod_sdm")) models[["SDM"]] <- c(AIC = AIC(mod_sdm), logLik = as.numeric(logLik(mod_sdm)))

cat("  Model    AIC        logLik\n")
for (m_name in names(models)) {
  cat(sprintf("  %-6s   %.2f   %.2f\n", m_name, models[[m_name]]["AIC"], models[[m_name]]["logLik"]))
}

# =============================================================================
# 8. Save results
# =============================================================================

cat("\n--- Step 8: Saving results ---\n")

results <- list(
  mod_ols = mod_ols,
  moran_test = moran_result
)
if (exists("mod_sar")) results$mod_sar <- mod_sar
if (exists("mod_sem")) results$mod_sem <- mod_sem
if (exists("mod_sdm")) {
  results$mod_sdm <- mod_sdm
  results$sdm_impacts <- imp
}

saveRDS(results, file.path(data_dir, "sdm_results.rds"))
cat(sprintf("  Saved: %s\n", file.path(data_dir, "sdm_results.rds")))

# Save impacts as CSV if SDM succeeded
if (exists("imp")) {
  tryCatch({
    imp_summary <- summary(imp, zstats = TRUE)
    # Extract impacts from the summary object
    direct_vals <- imp_summary$res$direct
    indirect_vals <- imp_summary$res$indirect
    total_vals <- imp_summary$res$total
    var_names <- names(direct_vals)
    if (is.null(var_names)) var_names <- rownames(imp_summary$res$direct)

    impacts_df <- data.frame(
      variable = var_names,
      direct = as.numeric(direct_vals),
      indirect = as.numeric(indirect_vals),
      total = as.numeric(total_vals),
      stringsAsFactors = FALSE
    )
    impacts_path <- file.path(data_dir, "sdm_impacts.csv")
    write.csv(impacts_df, impacts_path, row.names = FALSE)
    cat(sprintf("  Saved: %s\n", impacts_path))
  }, error = function(e) {
    cat("  Could not save impacts CSV:", e$message, "\n")
    cat("  Impacts are saved within sdm_results.rds\n")
  })
}

cat("\n--- Done ---\n")
