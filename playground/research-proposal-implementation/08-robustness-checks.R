# =============================================================================
# 08-robustness-checks.R
# Robustness checks across all three models.
#
# Model 1: ERGM per commission (C1, C3, C5 separately)
# Model 2: Alternative lags, falsification test
# Model 3: Embedding similarity, binary W, alternative specifications
# =============================================================================

cat("=== 08-robustness-checks.R ===\n")
cat("Robustness Checks\n\n")

if (!requireNamespace("jsonlite", quietly = TRUE)) install.packages("jsonlite", repos = "http://cran.us.r-project.org")
if (!requireNamespace("statnet", quietly = TRUE)) install.packages("statnet", repos = "http://cran.us.r-project.org")
if (!requireNamespace("spdep", quietly = TRUE)) install.packages("spdep", repos = "http://cran.us.r-project.org")
if (!requireNamespace("spatialreg", quietly = TRUE)) install.packages("spatialreg", repos = "http://cran.us.r-project.org")

library(jsonlite)
library(statnet)
library(spdep)
library(spatialreg)

set.seed(42)

base_dir <- "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking"
impl_dir <- file.path(base_dir, "playground/research-proposal-implementation")
data_dir <- file.path(impl_dir, "data")

profiles <- fromJSON(file.path(base_dir,
                               "conventionals-bcn-webscrapping/conventional-profiles.json"))

get_attr <- function(name, attr_col, default_val) {
  idx <- match(name, profiles$nombre_armonizado)
  if (!is.na(idx) && !is.na(profiles[[attr_col]][idx])) return(profiles[[attr_col]][idx])
  return(default_val)
}

# #############################################################################
# ROBUSTNESS 1: Per-Commission Valued ERGMs
# #############################################################################

cat("=== ROBUSTNESS 1: Per-Commission Valued ERGMs ===\n\n")

comm_results <- list()

for (comm in c("C1", "C3", "C5")) {
  cat(sprintf("--- %s ---\n", comm))

  # Load per-commission network
  net_file <- file.path(impl_dir, "network-visualization",
                        paste0(comm, "_dynamic_networks.json"))
  net_data <- fromJSON(net_file, simplifyVector = FALSE)

  # Use the final wave (last cumulative snapshot)
  wave_names <- names(net_data)
  final_wave <- net_data[[wave_names[length(wave_names)]]]

  # Extract edges
  sources <- sapply(final_wave, function(e) e$source)
  targets <- sapply(final_wave, function(e) e$target)
  weights <- sapply(final_wave, function(e) e$weight)

  all_nodes <- sort(unique(c(sources, targets)))
  n_nodes <- length(all_nodes)

  # Build network
  net <- network.initialize(n_nodes, directed = FALSE)
  network.vertex.names(net) <- all_nodes

  set.vertex.attribute(net, "afiliacion_agrupada",
                       sapply(all_nodes, function(n) get_attr(n, "afiliacion_agrupada", "Desconocida")))
  set.vertex.attribute(net, "es_abogado",
                       sapply(all_nodes, function(n) get_attr(n, "es_abogado", 0)))
  set.vertex.attribute(net, "es_mujer",
                       sapply(all_nodes, function(n) get_attr(n, "es_mujer", 0)))
  set.vertex.attribute(net, "edad_al_asumir",
                       sapply(all_nodes, function(n) get_attr(n, "edad_al_asumir", 45)))
  set.vertex.attribute(net, "experiencia_previa_institucional",
                       sapply(all_nodes, function(n) get_attr(n, "experiencia_previa_institucional", 0)))

  add.edges(net, tail = match(sources, all_nodes), head = match(targets, all_nodes))
  set.edge.attribute(net, "weight", weights)

  cat(sprintf("  Nodes: %d, Edges: %d\n", n_nodes, network.edgecount(net)))

  tryCatch({
    fit <- ergm(net ~ sum +
                  nodematch("afiliacion_agrupada") +
                  nodematch("experiencia_previa_institucional") +
                  nodematch("es_abogado") +
                  nodematch("es_mujer") +
                  absdiff("edad_al_asumir") +
                  nodecov("edad_al_asumir"),
                response = "weight",
                reference = ~Poisson,
                control = control.ergm(seed = 42))

    cat("  Coefficients:\n")
    coefs <- coef(summary(fit))
    print(round(coefs, 4))
    comm_results[[comm]] <- coefs
  }, error = function(e) {
    cat("  ERGM failed:", e$message, "\n")
  })
  cat("\n")
}

# Compare coefficients across commissions
cat("\n--- Coefficient Comparison Across Commissions ---\n")
if (length(comm_results) >= 2) {
  terms <- rownames(comm_results[[1]])
  cat(sprintf("%-50s %10s %10s %10s\n", "Term", "C1", "C3", "C5"))
  for (term in terms) {
    vals <- sapply(names(comm_results), function(c) {
      if (term %in% rownames(comm_results[[c]])) {
        sprintf("%.4f", comm_results[[c]][term, "Estimate"])
      } else "NA"
    })
    cat(sprintf("%-50s %10s %10s %10s\n", term, vals[1], vals[2],
                ifelse(length(vals) >= 3, vals[3], "NA")))
  }
}

# #############################################################################
# ROBUSTNESS 2: Model 2 — Falsification test
# #############################################################################

cat("\n\n=== ROBUSTNESS 2: Model 2 Falsification ===\n")
cat("Test: Does FUTURE network predict PAST ideology change? (Should be null)\n\n")

panel <- read.csv(file.path(data_dir, "network_exposure_panel.csv"),
                  stringsAsFactors = FALSE)

# Compute "lead" exposure: net_exposure at t+1 instead of t-1
panel$net_exposure_lead <- NA
for (comm in c("C1", "C3", "C5")) {
  for (leg in unique(panel$legislator)) {
    idx <- which(panel$legislator == leg & panel$commission == comm)
    if (length(idx) < 2) next
    sub <- panel[idx, ]
    for (j in 1:(length(idx) - 1)) {
      panel$net_exposure_lead[idx[j]] <- sub$network_exposure[j + 1]
    }
  }
}

# Falsification regression: delta_theta ~ theta_lag + net_exposure_LEAD
falsi_df <- panel[!is.na(panel$delta_theta) &
                  !is.na(panel$net_exposure_lead) &
                  !is.na(panel$theta_lag), ]

if (nrow(falsi_df) > 10) {
  cat(sprintf("  Falsification sample: %d observations\n", nrow(falsi_df)))
  mod_falsi <- lm(delta_theta ~ theta_lag + net_exposure_lead, data = falsi_df)
  cat("  Coefficients:\n")
  print(round(coef(summary(mod_falsi)), 4))
  cat(sprintf("\n  net_exposure_lead p-value: %.4f\n",
              coef(summary(mod_falsi))["net_exposure_lead", "Pr(>|t|)"]))
  cat("  Interpretation: ", ifelse(
    coef(summary(mod_falsi))["net_exposure_lead", "Pr(>|t|)"] > 0.05,
    "Not significant -> falsification passes (future network doesn't predict past change)",
    "Significant -> potential concern (reverse causality or confounding)"), "\n")
} else {
  cat("  Insufficient observations for falsification test\n")
}

# #############################################################################
# ROBUSTNESS 3: Model 3 — Alternative specifications
# #############################################################################

cat("\n\n=== ROBUSTNESS 3: Model 3 Alternative Specifications ===\n")

dataset <- read.csv(file.path(data_dir, "integrated_dataset.csv"),
                    stringsAsFactors = FALSE)
edges <- read.csv(file.path(data_dir, "pooled_cumulative_network.csv"),
                  stringsAsFactors = FALSE)

# Complete cases
complete <- dataset[!is.na(dataset$mean_tfidf_retention) &
                    !is.na(dataset$theta_mean) &
                    !is.na(dataset$theta_sd) &
                    !is.na(dataset$es_mujer) &
                    !is.na(dataset$es_abogado) &
                    !is.na(dataset$experiencia_previa_institucional) &
                    !is.na(dataset$edad_al_asumir) &
                    !is.na(dataset$ego_heterophily) &
                    dataset$degree > 0, ]

sample_names <- complete$nombre_armonizado
n <- length(sample_names)

# --- 3A: Embedding-based similarity as DV ---
cat("\n  [3A] Embedding-based similarity as dependent variable:\n")
if (!is.null(complete$mean_embedding_retention) &&
    sum(!is.na(complete$mean_embedding_retention)) > 50) {

  mod_emb_ols <- lm(mean_embedding_retention ~ degree + betweenness +
                       es_abogado + experiencia_previa_institucional + es_mujer +
                       edad_al_asumir + theta_mean + theta_sd + ego_heterophily,
                     data = complete)
  cat("  OLS with embedding retention:\n")
  print(round(coef(summary(mod_emb_ols)), 4))
} else {
  cat("  Insufficient embedding data\n")
}

# --- 3B: Binary (unweighted) W matrix ---
cat("\n  [3B] SAR with binary W matrix:\n")

W_binary <- matrix(0, nrow = n, ncol = n,
                   dimnames = list(sample_names, sample_names))
for (i in seq_len(nrow(edges))) {
  s <- edges$source[i]
  t <- edges$target[i]
  if (s %in% sample_names && t %in% sample_names) {
    W_binary[s, t] <- 1
    W_binary[t, s] <- 1
  }
}

# Row-normalize binary W
row_sums_b <- rowSums(W_binary)
row_sums_b[row_sums_b == 0] <- 1
W_binary_norm <- W_binary / row_sums_b

set.ZeroPolicyOption(TRUE)
W_binary_listw <- mat2listw(W_binary_norm, style = "W")

formula_base <- mean_tfidf_retention ~ degree + betweenness +
  es_abogado + experiencia_previa_institucional + es_mujer +
  edad_al_asumir + theta_mean + theta_sd + ego_heterophily

tryCatch({
  mod_sar_binary <- lagsarlm(formula_base, data = complete, listw = W_binary_listw)
  cat("  SAR (binary W) rho:", mod_sar_binary$rho, "\n")
  cat("  SAR (binary W) AIC:", AIC(mod_sar_binary), "\n")
  cat("  Coefficients:\n")
  print(round(coef(summary(mod_sar_binary)), 4))
}, error = function(e) cat("  Error:", e$message, "\n"))

# --- 3C: Reduced specification (fewer covariates) ---
cat("\n  [3C] Reduced specification (key variables only):\n")

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
row_sums <- rowSums(W_raw)
row_sums[row_sums == 0] <- 1
W_norm <- W_raw / row_sums
W_listw <- mat2listw(W_norm, style = "W")

formula_reduced <- mean_tfidf_retention ~ betweenness +
  theta_mean + theta_sd + ego_heterophily

tryCatch({
  mod_sar_reduced <- lagsarlm(formula_reduced, data = complete, listw = W_listw)
  cat("  SAR (reduced) rho:", mod_sar_reduced$rho, "\n")
  cat("  SAR (reduced) AIC:", AIC(mod_sar_reduced), "\n")
  cat("  Coefficients:\n")
  print(round(coef(summary(mod_sar_reduced)), 4))
}, error = function(e) cat("  Error:", e$message, "\n"))

# =============================================================================
# Save results
# =============================================================================

cat("\n\n--- Saving Robustness Results ---\n")

robustness <- list(
  commission_ergms = comm_results,
  falsification_sample_n = nrow(falsi_df)
)
if (exists("mod_falsi")) robustness$falsification_model <- mod_falsi
if (exists("mod_emb_ols")) robustness$embedding_ols <- mod_emb_ols
if (exists("mod_sar_binary")) robustness$sar_binary <- mod_sar_binary
if (exists("mod_sar_reduced")) robustness$sar_reduced <- mod_sar_reduced

saveRDS(robustness, file.path(data_dir, "robustness_results.rds"))
cat(sprintf("  Saved: %s\n", file.path(data_dir, "robustness_results.rds")))

cat("\n--- Done ---\n")
