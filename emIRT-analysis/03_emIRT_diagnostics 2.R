# =============================================================================
# 03_emIRT_diagnostics.R
# Diagnósticos y visualización del modelo dinámico emIRT
#
# Carga los resultados de dynIRT() y boot_emIRT(), genera visualizaciones
# para validar la estimación y diagnosticar posibles problemas.
# =============================================================================

cat("=== 03_emIRT_diagnostics.R ===\n")
cat("Diagnósticos del modelo emIRT...\n\n")

# --- Librerías ---
library(ggplot2)
library(data.table)

# =============================================================================
# PASO 1: Cargar resultados
# =============================================================================

cat("--- Paso 1: Cargando resultados ---\n")

lout <- readRDS("emIRT_model_output.rds")
boot_result <- readRDS("emIRT_bootstrap_output.rds")
metadata <- readRDS("emIRT_metadata.rds")
model_inputs <- readRDS("emIRT_model_inputs.rds")

votantes <- metadata$votantes
idx_derecha <- metadata$idx_derecha
idx_izquierda <- metadata$idx_izquierda
unique_dates <- metadata$unique_dates
N <- metadata$N
T_periods <- metadata$T_periods

cat("  N:", N, "| T:", T_periods, "\n")
cat("  Convergencia:", ifelse(lout$runtime$conv == 1, "SÍ ✓", "NO ✗"), "\n")
cat("  Iteraciones:", lout$runtime$iters, "\n")

# Crear directorio para plots
plots_dir <- "diagnostic_plots"
if (!dir.exists(plots_dir)) dir.create(plots_dir, recursive = TRUE)
cat("  Plots se guardarán en:", plots_dir, "/\n")

# =============================================================================
# PASO 2: Extraer ideal points
# =============================================================================

cat("\n--- Paso 2: Extrayendo ideal points ---\n")

x_hat <- lout$means$x # N × T matrix
x_var <- lout$vars$x # N × T matrix (varianzas del VEM — usar con cautela)

# Asignar nombres
rownames(x_hat) <- votantes
colnames(x_hat) <- format(unique_dates, "%Y-%m-%d")

cat("  Dimensiones x_hat:", nrow(x_hat), "×", ncol(x_hat), "\n")

# Bootstrap SEs
boot_se <- boot_result$bse$x
cat("  Dimensiones boot SE:", paste(dim(boot_se), collapse = " × "), "\n")

# =============================================================================
# PLOT 1: Convergencia y Runtime
# =============================================================================

cat("\n--- Plot 1: Información de convergencia ---\n")

cat("  Runtime info:\n")
cat("    Convergencia:", lout$runtime$conv, "\n")
cat("    Iteraciones:", lout$runtime$iters, "\n")
cat("    Threads:", lout$runtime$threads, "\n")
cat("    Tolerancia:", lout$runtime$tolerance, "\n")
cat("    N:", lout$runtime$N, "| J:", lout$runtime$J, "| T:", lout$runtime$T, "\n")

# =============================================================================
# PLOT 2: Trayectorias de anclas
# =============================================================================

cat("\n--- Plot 2: Trayectorias de anclas ---\n")

# Preparar datos para las anclas
anchor_data <- data.table(
  Periodo = rep(1:T_periods, 2),
  Fecha = rep(unique_dates, 2),
  Theta = c(x_hat[idx_derecha, ], x_hat[idx_izquierda, ]),
  Ancla = rep(c(
    paste0("Derecha: ", votantes[idx_derecha]),
    paste0("Izquierda: ", votantes[idx_izquierda])
  ), each = T_periods)
)

p2 <- ggplot(anchor_data, aes(x = Fecha, y = Theta, color = Ancla)) +
  geom_line(linewidth = 1) +
  geom_point(size = 1.5) +
  geom_hline(yintercept = 0, linetype = "dashed", alpha = 0.5) +
  scale_color_manual(values = c(
    "Derecha: Marinovic, Teresa" = "#d62728",
    "Izquierda: Baradit, Jorge" = "#1f77b4"
  )) +
  labs(
    title = "Trayectorias de los Anclas Ideológicos",
    subtitle = paste0(
      "Modelo emIRT dinámico | T = ", T_periods, " periodos | ω² = ",
      model_inputs$omega2_value
    ),
    x = "Fecha de sesión",
    y = "Ideal Point (θ)",
    color = NULL
  ) +
  theme_minimal(base_size = 12) +
  theme(
    legend.position = "bottom",
    plot.title = element_text(face = "bold"),
    axis.text.x = element_text(angle = 45, hjust = 1)
  )

ggsave(file.path(plots_dir, "plot2_anchor_trajectories.png"), p2,
  width = 12, height = 6, dpi = 150, device = grDevices::png, type = "cairo"
)
cat("  Guardado: plot2_anchor_trajectories.png\n")

# =============================================================================
# PLOT 3: Heatmap global de ideal points
# =============================================================================

cat("\n--- Plot 3: Heatmap global ---\n")

# Ordenar convencionales por su posición media global
mean_positions <- rowMeans(x_hat)
order_idx <- order(mean_positions)

# Preparar datos para heatmap
heatmap_data <- data.table(
  Legislador = rep(votantes[order_idx], each = T_periods),
  Periodo    = rep(1:T_periods, times = N),
  Fecha      = rep(unique_dates, times = N),
  Theta      = as.vector(t(x_hat[order_idx, ]))
)

# Factor ordenado para mantener el orden de izquierda a derecha
heatmap_data[, Legislador := factor(Legislador, levels = votantes[order_idx])]

p3 <- ggplot(heatmap_data, aes(x = Periodo, y = Legislador, fill = Theta)) +
  geom_tile() +
  scale_fill_gradient2(
    low = "#2166ac", mid = "#f7f7f7", high = "#b2182b",
    midpoint = 0, name = "Ideal Point (θ)"
  ) +
  labs(
    title = "Dinámica de Posiciones Ideológicas — Todos los Convencionales",
    subtitle = paste0("T = ", T_periods, " periodos | Ordenados por posición media"),
    x = "Periodo temporal",
    y = NULL
  ) +
  theme_minimal(base_size = 8) +
  theme(
    axis.text.y = element_text(size = 4),
    plot.title = element_text(face = "bold", size = 12),
    legend.position = "right"
  )

ggsave(file.path(plots_dir, "plot3_heatmap_global.png"), p3,
  width = 14, height = 20, dpi = 150, device = grDevices::png, type = "cairo"
)
cat("  Guardado: plot3_heatmap_global.png\n")

# =============================================================================
# PLOT 4: Distribución de ideal points por periodo
# =============================================================================

cat("\n--- Plot 4: Distribución por periodo ---\n")

# Preparar datos: solo periodos con votaciones
dist_data <- data.table(
  Periodo = rep(1:T_periods, each = N),
  Fecha   = rep(unique_dates, each = N),
  Theta   = as.vector(x_hat)
)

# Eliminar filas donde el ideal point es exactamente 0 (legislador no sirvió)
# En nuestro caso todos sirvieron, pero por seguridad
dist_data <- dist_data[Theta != 0 | TRUE] # Mantener todos

p4 <- ggplot(dist_data, aes(x = factor(Periodo), y = Theta)) +
  geom_boxplot(outlier.size = 0.5, fill = "#4292c6", alpha = 0.5) +
  geom_hline(yintercept = 0, linetype = "dashed", alpha = 0.5) +
  labs(
    title = "Distribución de Ideal Points por Periodo",
    subtitle = paste0("T = ", T_periods, " periodos | N = ", N, " convencionales"),
    x = "Periodo",
    y = "Ideal Point (θ)"
  ) +
  theme_minimal(base_size = 10) +
  theme(
    plot.title = element_text(face = "bold"),
    axis.text.x = element_text(angle = 90, hjust = 1, size = 6)
  )

ggsave(file.path(plots_dir, "plot4_distribution_by_period.png"), p4,
  width = 16, height = 6, dpi = 150, device = grDevices::png, type = "cairo"
)
cat("  Guardado: plot4_distribution_by_period.png\n")

# =============================================================================
# PLOT 5: Correlación con modelo antiguo (MCMC por ventana)
# =============================================================================

cat("\n--- Plot 5: Correlación con modelo antiguo (MCMC) ---\n")

# Definir las 9 ventanas originales y sus rangos de sesiones
# Las ventanas mapean a conjuntos de fechas del CSV original
window_definitions <- list(
  list(label = "01-15", csv = "votaciones_01_15.csv"),
  list(label = "16-21", csv = "votaciones_16_21.csv"),
  list(label = "22-37", csv = "votaciones_22_37.csv"),
  list(label = "38-46", csv = "votaciones_38_46.csv"),
  list(label = "47-55", csv = "votaciones_47_55.csv"),
  list(label = "56-75", csv = "votaciones_56_75.csv"),
  list(label = "76-99", csv = "votaciones_76_99.csv"),
  list(label = "100-106", csv = "votaciones_100_106.csv"),
  list(label = "107-109", csv = "votaciones_107_109.csv")
)

# Intentar cargar los resultados MCMC antiguos si existen
old_mcmc_path <- "../../ideological-scaling-files/03_orden_votantes_t_MCMC.rds"
old_wnom_path <- "../../ideological-scaling-files/03_orden_votantes_t.rds"

if (file.exists(old_mcmc_path)) {
  old_mcmc <- readRDS(old_mcmc_path)
  cat("  Resultados MCMC antiguos cargados desde:", old_mcmc_path, "\n")
  cat("  Columnas disponibles:", paste(names(old_mcmc), collapse = ", "), "\n")

  # Calcular posición media por ventana para el modelo emIRT
  # Para esto, necesitamos saber qué periodos (fechas) corresponden a cada ventana
  emIRT_data_input <- readRDS("emIRT_data_input.rds")
  bill_session_vec <- as.vector(emIRT_data_input$bill.session)

  DATA_DIR <- "../../ideological-scaling-files"

  # Para cada ventana, calcular la posición media en los periodos correspondientes
  cat("  Calculando correlaciones por ventana...\n")

  for (win in window_definitions) {
    # Encontrar las fechas de esta ventana
    csv_path <- file.path(DATA_DIR, win$csv)
    if (!file.exists(csv_path)) next

    csv_header <- readLines(csv_path, n = 1)
    csv_cols <- strsplit(csv_header, ",")[[1]]
    csv_dates_str <- regmatches(csv_cols, regexpr("[0-9]{8}", csv_cols))
    csv_dates <- unique(as.Date(csv_dates_str, format = "%d%m%Y"))
    csv_dates <- csv_dates[!is.na(csv_dates)]

    # Encontrar los índices de periodos correspondientes
    period_indices <- which(unique_dates %in% csv_dates)

    if (length(period_indices) == 0) {
      cat("    Ventana", win$label, ": sin periodos correspondientes\n")
      next
    }

    # Posición media del emIRT para esta ventana
    emirt_pos <- rowMeans(x_hat[, period_indices, drop = FALSE])

    cat(
      "    Ventana", win$label, ": periodos =", length(period_indices),
      ", fechas =", paste(format(range(csv_dates), "%d/%m/%y"), collapse = " → "), "\n"
    )
  }
} else {
  cat("  No se encontraron resultados MCMC antiguos en:", old_mcmc_path, "\n")
  cat("  Saltando comparación. Esto es normal si es la primera ejecución.\n")
}

# =============================================================================
# PLOT 6: Distribución de errores estándar bootstrap
# =============================================================================

cat("\n--- Plot 6: Errores estándar bootstrap ---\n")

# boot_se puede ser (N × 1) o depender de la implementación
if (!is.null(boot_se) && length(boot_se) > 0) {
  se_data <- data.table(
    Legislador = votantes,
    SE = as.numeric(boot_se)
  )
  se_data <- se_data[order(SE)]

  p6 <- ggplot(se_data, aes(x = SE)) +
    geom_histogram(bins = 30, fill = "#4292c6", color = "white", alpha = 0.8) +
    geom_vline(
      xintercept = mean(se_data$SE, na.rm = TRUE),
      linetype = "dashed", color = "red"
    ) +
    labs(
      title = "Distribución de Errores Estándar Bootstrap",
      subtitle = paste0("N = ", N, " convencionales | Ntrials = 50"),
      x = "Error Estándar",
      y = "Frecuencia"
    ) +
    theme_minimal(base_size = 12) +
    theme(plot.title = element_text(face = "bold"))

  ggsave(file.path(plots_dir, "plot6_bootstrap_se_distribution.png"), p6,
    width = 8, height = 5, dpi = 150, device = grDevices::png, type = "cairo"
  )
  cat("  Guardado: plot6_bootstrap_se_distribution.png\n")

  # Top 10 con mayor incertidumbre
  cat("\n  Top 10 convencionales con mayor SE bootstrap:\n")
  print(tail(se_data, 10))

  # Top 10 con menor incertidumbre
  cat("\n  Top 10 convencionales con menor SE bootstrap:\n")
  print(head(se_data, 10))
} else {
  cat("  Bootstrap SE no disponible o vacío.\n")
}

# =============================================================================
# RESUMEN: Tabla de posiciones medias por convencional
# =============================================================================

cat("\n--- Resumen: Posiciones medias globales ---\n")

summary_dt <- data.table(
  Legislador = votantes,
  Posicion_Media = rowMeans(x_hat),
  Posicion_SD = apply(x_hat, 1, sd),
  Posicion_Min = apply(x_hat, 1, min),
  Posicion_Max = apply(x_hat, 1, max),
  Rango_Total = apply(x_hat, 1, max) - apply(x_hat, 1, min)
)

# Agregar SE bootstrap si disponible
if (!is.null(boot_se) && length(boot_se) == N) {
  summary_dt[, Bootstrap_SE := as.numeric(boot_se)]
}

summary_dt <- summary_dt[order(Posicion_Media)]
summary_dt[, Ranking := 1:.N]

# Mostrar extremos
cat("\n  Los 10 más a la izquierda:\n")
print(head(summary_dt[, .(Ranking, Legislador, Posicion_Media, Rango_Total)], 10))

cat("\n  Los 10 más a la derecha:\n")
print(tail(summary_dt[, .(Ranking, Legislador, Posicion_Media, Rango_Total)], 10))

cat("\n  Los 10 más volátiles (mayor rango total):\n")
print(head(summary_dt[order(-Rango_Total), .(Ranking, Legislador, Posicion_Media, Rango_Total)], 10))

# Guardar tabla resumen
fwrite(summary_dt, "emIRT_summary_positions.csv")
saveRDS(summary_dt, "emIRT_summary_positions.rds")
cat("\n  Resumen guardado en: emIRT_summary_positions.csv/rds\n")

# =============================================================================
# ESTRUCTURA PARA SENSIBILIDAD DE omega2 (ejecución futura)
# =============================================================================

cat("\n--- Nota: Análisis de sensibilidad de omega2 ---\n")
cat("  Para probar diferentes valores de omega2, re-ejecutar 02_emIRT_model_run.R\n")
cat("  modificando OMEGA2_VALUE y comparar los resultados.\n")
cat("  Valores sugeridos: 0.01, 0.025 (actual), 0.05, 0.1, 0.2, 0.5, 1.0\n")

cat("\n=== 03_emIRT_diagnostics.R completado ===\n")
cat("  Plots guardados en:", plots_dir, "/\n")
cat("  Archivos de resumen:\n")
cat("    - emIRT_summary_positions.csv\n")
cat("    - emIRT_summary_positions.rds\n")
