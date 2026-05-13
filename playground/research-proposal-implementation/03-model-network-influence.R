# =============================================================================
# 03-model-network-influence.R
# Model 2: Ideological Dynamics — Network Influence on Ideology
#
# Tests whether co-authorship network connections at t-1 predict ideological
# convergence at time t, using panel regression with fixed effects.
#
# Model:
#   Delta_theta_it = alpha_i + beta_1*theta_i,t-1 + beta_3*NetworkExposure_i,t-1
#                    + gamma*X_i + epsilon_it
#
# NetworkExposure = weighted average ideal point of co-authorship partners
# =============================================================================

cat("=== 03-model-network-influence.R ===\n")
cat("Model 2: Network Influence on Ideological Dynamics\n\n")

if (!requireNamespace("jsonlite", quietly = TRUE)) install.packages("jsonlite", repos = "http://cran.us.r-project.org")
if (!requireNamespace("plm", quietly = TRUE)) install.packages("plm", repos = "http://cran.us.r-project.org")
if (!requireNamespace("lmtest", quietly = TRUE)) install.packages("lmtest", repos = "http://cran.us.r-project.org")
if (!requireNamespace("sandwich", quietly = TRUE)) install.packages("sandwich", repos = "http://cran.us.r-project.org")

library(jsonlite)
library(plm)
library(lmtest)
library(sandwich)

set.seed(42)

base_dir <- "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking"
impl_dir <- file.path(base_dir, "playground/research-proposal-implementation")
data_dir <- file.path(impl_dir, "data")

# =============================================================================
# 1. Load ideal points and commission network data
# =============================================================================

cat("--- Step 1: Loading data ---\n")

# Full ideal point matrix (long format)
ip_full <- read.csv(file.path(data_dir, "emirt_ideal_points_full.csv"),
                    stringsAsFactors = FALSE)
cat(sprintf("  Ideal points: %d rows (%d legislators x %d periods)\n",
            nrow(ip_full), length(unique(ip_full$legislator)),
            length(unique(ip_full$period))))

# Aligned ideal points to commission steps
ip_aligned <- read.csv(file.path(data_dir, "emirt_aligned_to_commissions.csv"),
                       stringsAsFactors = FALSE)
cat(sprintf("  Aligned to commissions: %d rows\n", nrow(ip_aligned)))

# Profiles for covariates
profiles <- fromJSON(file.path(base_dir,
                               "conventionals-bcn-webscrapping/conventional-profiles.json"))
cat(sprintf("  Profiles: %d\n", nrow(profiles)))

# =============================================================================
# 2. Load dynamic networks and build cumulative adjacency at each step
# =============================================================================

cat("\n--- Step 2: Building cumulative adjacency matrices per commission step ---\n")

commissions <- c("C1", "C3", "C5")

# Load per-commission dynamic networks
load_dynamic_network <- function(comm) {
  fpath <- file.path(impl_dir, "network-visualization",
                     paste0(comm, "_dynamic_networks.json"))
  fromJSON(fpath, simplifyVector = FALSE)
}

# Build adjacency matrix from edge list
edges_to_adj <- function(edges, node_names) {
  n <- length(node_names)
  adj <- matrix(0, nrow = n, ncol = n,
                dimnames = list(node_names, node_names))
  for (e in edges) {
    s <- e$source
    t <- e$target
    w <- e$weight
    if (s %in% node_names && t %in% node_names) {
      adj[s, t] <- w
      adj[t, s] <- w
    }
  }
  return(adj)
}

# Get the full set of legislators from ideal points
all_legislators <- sort(unique(ip_full$legislator))
n_leg <- length(all_legislators)

# Build cumulative adjacency matrices indexed by (commission, step)
# Each step's network is cumulative (includes all prior edges)
adj_by_step <- list()

for (comm in commissions) {
  net_data <- load_dynamic_network(comm)
  wave_names <- names(net_data)
  cat(sprintf("  %s: %d waves (%s)\n", comm, length(wave_names),
              paste(wave_names, collapse = ", ")))

  for (w in seq_along(wave_names)) {
    key <- paste0(comm, "_", w - 1)  # 0-indexed step
    edges <- net_data[[wave_names[w]]]
    adj_by_step[[key]] <- edges_to_adj(edges, all_legislators)
  }
}

# =============================================================================
# 3. Compute NetworkExposure for each legislator at each commission step
# =============================================================================

cat("\n--- Step 3: Computing NetworkExposure ---\n")

# NetworkExposure_i,t = sum_j(w_ij * theta_j,t) / sum_j(w_ij)
# Uses the network at step t and ideal points at the corresponding emIRT period

# Get unique (commission, step) pairs from aligned data
comm_steps <- unique(ip_aligned[, c("commission", "step", "step_label",
                                     "emirt_period", "emirt_date")])

panel_rows <- list()

for (r in seq_len(nrow(comm_steps))) {
  comm <- comm_steps$commission[r]
  step <- comm_steps$step[r]
  period <- comm_steps$emirt_period[r]
  step_label <- comm_steps$step_label[r]

  # Get adjacency at this step
  adj_key <- paste0(comm, "_", step)
  if (!(adj_key %in% names(adj_by_step))) next

  adj <- adj_by_step[[adj_key]]

  # Get ideal points at this period for all legislators
  ip_period <- ip_full[ip_full$period == period, ]
  theta_vec <- setNames(ip_period$theta, ip_period$legislator)

  for (leg in all_legislators) {
    # Own theta
    own_theta <- theta_vec[leg]
    if (is.na(own_theta)) next

    # Weighted neighbors' thetas
    if (leg %in% rownames(adj)) {
      weights <- adj[leg, ]
      connected <- weights > 0
      if (sum(connected) > 0) {
        neighbor_names <- names(weights[connected])
        neighbor_thetas <- theta_vec[neighbor_names]
        neighbor_weights <- weights[connected]
        # Remove NAs
        valid <- !is.na(neighbor_thetas)
        if (sum(valid) > 0) {
          net_exposure <- sum(neighbor_thetas[valid] * neighbor_weights[valid]) /
                          sum(neighbor_weights[valid])
          n_partners <- sum(valid)
          total_weight <- sum(neighbor_weights[valid])
        } else {
          net_exposure <- NA
          n_partners <- 0
          total_weight <- 0
        }
      } else {
        net_exposure <- NA
        n_partners <- 0
        total_weight <- 0
      }
    } else {
      net_exposure <- NA
      n_partners <- 0
      total_weight <- 0
    }

    panel_rows[[length(panel_rows) + 1]] <- data.frame(
      legislator = leg,
      commission = comm,
      step = step,
      step_label = step_label,
      emirt_period = period,
      theta = own_theta,
      network_exposure = net_exposure,
      n_partners = n_partners,
      total_weight = total_weight,
      stringsAsFactors = FALSE
    )
  }
}

panel_df <- do.call(rbind, panel_rows)
cat(sprintf("  Panel rows: %d\n", nrow(panel_df)))

# =============================================================================
# 4. Compute delta_theta (ideological shift) and lag variables
# =============================================================================

cat("\n--- Step 4: Computing delta_theta and lags ---\n")

# Sort by legislator, commission, step
panel_df <- panel_df[order(panel_df$legislator, panel_df$commission, panel_df$step), ]

# Compute delta_theta = theta_t - theta_{t-1} (within each commission)
panel_df$delta_theta <- NA
panel_df$theta_lag <- NA
panel_df$net_exposure_lag <- NA

for (comm in commissions) {
  for (leg in all_legislators) {
    idx <- which(panel_df$legislator == leg & panel_df$commission == comm)
    if (length(idx) < 2) next

    sub <- panel_df[idx, ]
    for (j in 2:length(idx)) {
      panel_df$delta_theta[idx[j]] <- sub$theta[j] - sub$theta[j - 1]
      panel_df$theta_lag[idx[j]] <- sub$theta[j - 1]
      panel_df$net_exposure_lag[idx[j]] <- sub$network_exposure[j - 1]
    }
  }
}

# Add profile covariates
panel_df$es_abogado <- sapply(panel_df$legislator, function(n) {
  idx <- match(n, profiles$nombre_armonizado)
  if (!is.na(idx)) profiles$es_abogado[idx] else NA
})
panel_df$experiencia_previa <- sapply(panel_df$legislator, function(n) {
  idx <- match(n, profiles$nombre_armonizado)
  if (!is.na(idx)) profiles$experiencia_previa_institucional[idx] else NA
})
panel_df$es_mujer <- sapply(panel_df$legislator, function(n) {
  idx <- match(n, profiles$nombre_armonizado)
  if (!is.na(idx)) profiles$es_mujer[idx] else NA
})

# Save full panel
panel_path <- file.path(data_dir, "network_exposure_panel.csv")
write.csv(panel_df, panel_path, row.names = FALSE)
cat(sprintf("  Saved panel: %s\n", panel_path))

# =============================================================================
# 5. Estimate panel regression models
# =============================================================================

cat("\n--- Step 5: Panel Regression ---\n")

# Filter to rows with valid delta_theta and lagged exposure
reg_df <- panel_df[!is.na(panel_df$delta_theta) &
                   !is.na(panel_df$net_exposure_lag) &
                   !is.na(panel_df$theta_lag), ]

cat(sprintf("  Regression sample: %d observations\n", nrow(reg_df)))
cat(sprintf("  Unique legislators: %d\n", length(unique(reg_df$legislator))))
cat(sprintf("  Commissions: %s\n", paste(unique(reg_df$commission), collapse = ", ")))

# Create panel data frame
pdata <- pdata.frame(reg_df, index = c("legislator", "step"), drop.index = FALSE)

# Model A: OLS pooled (baseline)
cat("\n  [Model A] Pooled OLS:\n")
mod_ols <- lm(delta_theta ~ theta_lag + net_exposure_lag +
                es_abogado + experiencia_previa + es_mujer,
              data = reg_df)
cat("    Coefficients:\n")
print(round(coef(summary(mod_ols)), 4))

# Model B: Fixed effects (within estimator)
cat("\n  [Model B] Fixed Effects (within):\n")
tryCatch({
  mod_fe <- plm(delta_theta ~ theta_lag + net_exposure_lag,
                data = pdata, model = "within")
  cat("    Coefficients:\n")
  print(round(coef(summary(mod_fe)), 4))

  # Cluster-robust standard errors
  cat("\n    With cluster-robust SEs:\n")
  robust_fe <- coeftest(mod_fe, vcov = vcovHC(mod_fe, type = "HC1",
                                               cluster = "group"))
  print(round(robust_fe, 4))
}, error = function(e) {
  cat("    Fixed effects model could not be estimated:", e$message, "\n")
  cat("    Falling back to pooled OLS with cluster-robust SEs\n")
})

# Model C: Random effects
cat("\n  [Model C] Random Effects:\n")
tryCatch({
  mod_re <- plm(delta_theta ~ theta_lag + net_exposure_lag +
                  es_abogado + experiencia_previa + es_mujer,
                data = pdata, model = "random")
  cat("    Coefficients:\n")
  print(round(coef(summary(mod_re)), 4))

  # Hausman test (FE vs RE)
  cat("\n    Hausman test (FE vs RE):\n")
  if (exists("mod_fe")) {
    ht <- phtest(mod_fe, mod_re)
    cat(sprintf("    chi-sq = %.3f, p = %.4f\n", ht$statistic, ht$p.value))
    cat(sprintf("    Interpretation: %s\n",
                ifelse(ht$p.value < 0.05,
                       "Reject RE -> use Fixed Effects",
                       "Cannot reject RE -> Random Effects acceptable")))
  }
}, error = function(e) {
  cat("    Random effects model could not be estimated:", e$message, "\n")
})

# Model D: OLS with commission fixed effects (alternative)
cat("\n  [Model D] OLS with Commission Fixed Effects:\n")
reg_df$commission_f <- factor(reg_df$commission)
mod_comm_fe <- lm(delta_theta ~ theta_lag + net_exposure_lag +
                    es_abogado + experiencia_previa + es_mujer +
                    commission_f,
                  data = reg_df)
cat("    Coefficients:\n")
print(round(coef(summary(mod_comm_fe)), 4))

# Cluster-robust SEs for Model D
cat("\n    With cluster-robust SEs (clustered by legislator):\n")
robust_d <- coeftest(mod_comm_fe,
                     vcov = vcovCL(mod_comm_fe, cluster = reg_df$legislator))
print(round(robust_d, 4))

# =============================================================================
# 6. Save results
# =============================================================================

cat("\n--- Step 6: Saving results ---\n")

results <- list(
  mod_ols = mod_ols,
  mod_comm_fe = mod_comm_fe
)
# Add FE and RE models if they exist
if (exists("mod_fe")) results$mod_fe <- mod_fe
if (exists("mod_re")) results$mod_re <- mod_re

saveRDS(results, file.path(data_dir, "panel_regression_results.rds"))
cat(sprintf("  Saved: %s\n", file.path(data_dir, "panel_regression_results.rds")))

# =============================================================================
# 7. Summary and interpretation
# =============================================================================

cat("\n--- Summary ---\n")
cat("Key coefficient: net_exposure_lag (beta_3)\n")
cat("  Interpretation: A positive beta_3 means that legislators whose\n")
cat("  co-authorship partners have a higher (more right-wing) average\n")
cat("  ideal point at t-1 tend to shift rightward at t, and vice versa.\n")
cat("  This would indicate network influence on ideological convergence.\n")
cat("\n  A negative beta_3 would indicate polarization (divergence from\n")
cat("  network partners' positions).\n")

cat("\n--- Done ---\n")
