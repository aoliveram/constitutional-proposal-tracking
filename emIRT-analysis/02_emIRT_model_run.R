# =============================================================================
# 02_emIRT_model_run.R
# Estimación dinámica de ideal points con emIRT::dynIRT() + bootstrap
#
# Carga el objeto .data preparado por 01_emIRT_data_prep.R,
# define priors y starting values, y ejecuta el modelo dinámico.
# Luego ejecuta boot_emIRT() para obtener errores estándar confiables.
# =============================================================================

cat("=== 02_emIRT_model_run.R ===\n")
cat("Estimación dinámica con emIRT...\n\n")

# --- Librerías ---
if (!requireNamespace("emIRT", quietly = TRUE)) {
  stop("El paquete 'emIRT' no está instalado. Instálalo con:\n  install.packages('emIRT')")
}
library(emIRT)

# =============================================================================
# PASO 1: Cargar datos preparados
# =============================================================================

cat("--- Paso 1: Cargando datos preparados ---\n")

emIRT_data <- readRDS("emIRT_data_input.rds")
metadata <- readRDS("emIRT_metadata.rds")

N <- metadata$N
J <- metadata$J
T_periods <- metadata$T_periods
idx_derecha <- metadata$idx_derecha
idx_izquierda <- metadata$idx_izquierda

cat("  N (legisladores):", N, "\n")
cat("  J (votaciones):", J, "\n")
cat("  T (periodos):", T_periods, "\n")
cat("  Ancla derecha (Marinovic):", metadata$votantes[idx_derecha], "-> idx =", idx_derecha, "\n")
cat("  Ancla izquierda (Baradit):", metadata$votantes[idx_izquierda], "-> idx =", idx_izquierda, "\n")

# =============================================================================
# PASO 2: Definir Starting Values (.starts)
# =============================================================================

cat("\n--- Paso 2: Definiendo starting values ---\n")

# Semilla para reproducibilidad de los starts
set.seed(42)

# alpha: Item difficulty (J × 1) — small random noise, not zeros
# (All-zero starts cause singular matrices in the VEM update)
start_alpha <- matrix(rnorm(J, mean = 0, sd = 0.1), nrow = J, ncol = 1)

# beta: Item discrimination (J × 1) — small random noise
start_beta <- matrix(rnorm(J, mean = 0, sd = 0.1), nrow = J, ncol = 1)

# x: Ideal points (N × T) — small random noise for non-anchors
start_x <- matrix(rnorm(N * T_periods, mean = 0, sd = 0.2), nrow = N, ncol = T_periods)

# Anclaje: Asignar valores extremos a las anclas en todos los periodos
start_x[idx_derecha, ] <- 2.0 # Marinovic → derecha (positivo)
start_x[idx_izquierda, ] <- -2.0 # Baradit → izquierda (negativo)

cat("  start_alpha: ", nrow(start_alpha), "x", ncol(start_alpha), " (random ~ N(0, 0.1))\n")
cat("  start_beta:  ", nrow(start_beta), "x", ncol(start_beta), " (random ~ N(0, 0.1))\n")
cat("  start_x:     ", nrow(start_x), "x", ncol(start_x), "\n")
cat("    Marinovic (todos periodos):", unique(start_x[idx_derecha, ]), "\n")
cat("    Baradit (todos periodos):", unique(start_x[idx_izquierda, ]), "\n")

starts <- list(
  alpha = start_alpha,
  beta  = start_beta,
  x     = start_x
)

# =============================================================================
# PASO 3: Definir Priors (.priors)
# =============================================================================

cat("\n--- Paso 3: Definiendo priors ---\n")

# x.mu0: Prior means para ideal points (N × 1)
# Las anclas reciben prior informativo, el resto difuso
prior_x_mu0 <- matrix(0, nrow = N, ncol = 1)
prior_x_mu0[idx_derecha, ] <- 1.0 # Marinovic → derecha
prior_x_mu0[idx_izquierda, ] <- -1.0 # Baradit → izquierda

# x.sigma0: Prior variances para ideal points (N × 1)
# Las anclas reciben varianza MUY pequeña (prior fuertemente informativo)
prior_x_sigma0 <- matrix(1.0, nrow = N, ncol = 1)
prior_x_sigma0[idx_derecha, ] <- 0.01 # Prior muy estrecho para ancla
prior_x_sigma0[idx_izquierda, ] <- 0.01 # Prior muy estrecho para ancla

# beta.mu: Prior means para parámetros de ítems (2 × 1)
# [1] = alpha_j (dificultad), [2] = beta_j (discriminación)
prior_beta_mu <- matrix(0, nrow = 2, ncol = 1)

# beta.sigma: Prior covariance para parámetros de ítems (2 × 2)
# Varianza amplia para priors difusos
prior_beta_sigma <- matrix(c(25, 0, 0, 25), nrow = 2, ncol = 2)

# omega2: Varianza evolutiva del random walk (N × 1)
# Controla cuánto puede cambiar θ_{i,t} entre periodos consecutivos
# ω² = 0.025 → penaliza saltos drásticos resolviendo el colapso de espacio sin datos
OMEGA2_VALUE <- 0.025
prior_omega2 <- matrix(OMEGA2_VALUE, nrow = N, ncol = 1)

cat("  x.mu0:       ", nrow(prior_x_mu0), "x", ncol(prior_x_mu0), "\n")
cat(
  "    Marinovic:", prior_x_mu0[idx_derecha], "| Baradit:", prior_x_mu0[idx_izquierda],
  "| Resto: 0\n"
)
cat("  x.sigma0:    ", nrow(prior_x_sigma0), "x", ncol(prior_x_sigma0), "\n")
cat("    Anclas: 0.01 | Resto: 1.0\n")
cat("  beta.mu:     ", nrow(prior_beta_mu), "x", ncol(prior_beta_mu), "\n")
cat("  beta.sigma:  ", nrow(prior_beta_sigma), "x", ncol(prior_beta_sigma), "\n")
cat("  omega2:       all =", OMEGA2_VALUE, "\n")

priors <- list(
  x.mu0      = prior_x_mu0,
  x.sigma0   = prior_x_sigma0,
  beta.mu    = prior_beta_mu,
  beta.sigma = prior_beta_sigma,
  omega2     = prior_omega2
)

# =============================================================================
# PASO 4: Definir Control
# =============================================================================

cat("\n--- Paso 4: Definiendo control ---\n")

control <- list(
  threads   = 8, # M4 Pro: 8 P-cores
  verbose   = TRUE,
  thresh    = 1e-6,
  maxit     = 500,
  checkfreq = 50
)

cat("  threads:", control$threads, "\n")
cat("  thresh:", control$thresh, "\n")
cat("  maxit:", control$maxit, "\n")

# =============================================================================
# PASO 5: Ejecutar dynIRT()
# =============================================================================

cat("\n--- Paso 5: Ejecutando dynIRT() ---\n")
cat("  Esto puede tomar varios minutos...\n\n")

start_time <- Sys.time()

lout <- dynIRT(
  .data    = emIRT_data,
  .starts  = starts,
  .priors  = priors,
  .control = control
)

end_time <- Sys.time()
elapsed <- difftime(end_time, start_time, units = "mins")

cat("\n  dynIRT() completado en", round(as.numeric(elapsed), 2), "minutos\n")
cat("  Convergencia:", ifelse(lout$runtime$conv == 1, "SÍ ✓", "NO ✗ (máximo de iteraciones alcanzado)"), "\n")
cat("  Iteraciones:", lout$runtime$iters, "\n")
cat("  N:", lout$runtime$N, "| J:", lout$runtime$J, "| T:", lout$runtime$T, "\n")

# =============================================================================
# PASO 6: Verificación rápida de polaridad
# =============================================================================

cat("\n--- Paso 6: Verificación de polaridad ---\n")

x_means <- lout$means$x # N × T matrix

marinovic_positions <- x_means[idx_derecha, ]
baradit_positions <- x_means[idx_izquierda, ]

cat(
  "  Marinovic (derecha) - media:", round(mean(marinovic_positions), 4),
  "| rango: [", round(min(marinovic_positions), 4), ",",
  round(max(marinovic_positions), 4), "]\n"
)
cat(
  "  Baradit (izquierda) - media:", round(mean(baradit_positions), 4),
  "| rango: [", round(min(baradit_positions), 4), ",",
  round(max(baradit_positions), 4), "]\n"
)

# Polaridad correcta: Marinovic positiva, Baradit negativa
polarity_ok <- mean(marinovic_positions) > 0 & mean(baradit_positions) < 0
cat("  Polaridad correcta:", ifelse(polarity_ok, "SÍ ✓", "NO ✗ — aplicando post-hoc flip"), "\n")

if (!polarity_ok) {
  cat("  NOTA: Aplicando inversión de signo (post-hoc flip) a ideal points y betas.\n")
  cat("        Esto es práctica estándar en IRT cuando el VEM converge con signo opuesto.\n")
  lout$means$x <- -lout$means$x
  lout$means$beta <- -lout$means$beta

  # Verificar de nuevo
  marinovic_positions <- lout$means$x[idx_derecha, ]
  baradit_positions <- lout$means$x[idx_izquierda, ]
  polarity_ok <- mean(marinovic_positions) > 0 & mean(baradit_positions) < 0
  cat(
    "  Tras flip - Marinovic media:", round(mean(marinovic_positions), 4),
    "| Baradit media:", round(mean(baradit_positions), 4), "\n"
  )
  cat("  Polaridad correcta tras flip:", ifelse(polarity_ok, "SÍ ✓", "NO ✗ — PROBLEMA GRAVE"), "\n")
}

# =============================================================================
# PASO 7: Guardar modelo
# =============================================================================

cat("\n--- Paso 7: Guardando modelo ---\n")

saveRDS(lout, "emIRT_model_output.rds")
cat("  Modelo guardado en: emIRT_model_output.rds\n")

# También guardar los inputs para reproducibilidad
model_inputs <- list(
  starts = starts,
  priors = priors,
  control = control,
  omega2_value = OMEGA2_VALUE,
  timestamp = Sys.time()
)
saveRDS(model_inputs, "emIRT_model_inputs.rds")
cat("  Inputs del modelo guardados en: emIRT_model_inputs.rds\n")

# =============================================================================
# PASO 8: Bootstrap paramétrico (boot_emIRT)
# =============================================================================

cat("\n--- Paso 8: Ejecutando bootstrap paramétrico (boot_emIRT) ---\n")
cat("  Ntrials = 50. Esto puede tomar un tiempo considerable...\n\n")

boot_start_time <- Sys.time()

boot_result <- boot_emIRT(
  emIRT.out = lout,
  .data = emIRT_data,
  .starts = starts,
  .priors = priors,
  .control = list(
    threads = 8, # M4 Pro: 8 P-cores
    verbose = FALSE,
    thresh  = 1e-6,
    maxit   = 500
  ),
  Ntrials = 50,
  verbose = 10
)

boot_end_time <- Sys.time()
boot_elapsed <- difftime(boot_end_time, boot_start_time, units = "mins")

cat("\n  Bootstrap completado en", round(as.numeric(boot_elapsed), 2), "minutos\n")

# Resumen de errores estándar bootstrap
boot_se <- boot_result$bse$x
cat("  Dimensiones boot SE:", paste(dim(boot_se), collapse = " × "), "\n")
cat(
  "  Rango de SE:", round(min(boot_se, na.rm = TRUE), 4), "-",
  round(max(boot_se, na.rm = TRUE), 4), "\n"
)
cat("  Media de SE:", round(mean(boot_se, na.rm = TRUE), 4), "\n")

# Guardar
saveRDS(boot_result, "emIRT_bootstrap_output.rds")
cat("  Bootstrap guardado en: emIRT_bootstrap_output.rds\n")

# =============================================================================
# Resumen final
# =============================================================================

total_elapsed <- difftime(Sys.time(), start_time, units = "mins")
cat("\n=== 02_emIRT_model_run.R completado ===\n")
cat("  Tiempo total (modelo + bootstrap):", round(as.numeric(total_elapsed), 2), "minutos\n")
cat("  Archivos generados:\n")
cat("    - emIRT_model_output.rds (modelo dynIRT)\n")
cat("    - emIRT_model_inputs.rds (starts/priors/control)\n")
cat("    - emIRT_bootstrap_output.rds (bootstrap SEs)\n")
