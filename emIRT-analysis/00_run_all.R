#!/usr/bin/env Rscript
# =============================================================================
# 00_run_all.R — Master script para la estimación dinámica con emIRT
#
# Ejecuta la pipeline completa:
#   01_emIRT_data_prep.R     → Preparación de datos
#   02_emIRT_model_run.R     → Estimación dynIRT() + bootstrap
#   03_emIRT_diagnostics.R   → Diagnósticos y visualización
#
# Uso:
#   cd playground/emIRT-analysis/
#   Rscript 00_run_all.R
# =============================================================================

cat("╔═══════════════════════════════════════════════════════════════╗\n")
cat("║     emIRT Dynamic Ideal Point Estimation Pipeline            ║\n")
cat("║     Convención Constitucional de Chile (2021-2022)           ║\n")
cat("╚═══════════════════════════════════════════════════════════════╝\n\n")

pipeline_start <- Sys.time()
cat("Inicio:", format(pipeline_start, "%Y-%m-%d %H:%M:%S"), "\n\n")

# --- Paso 1: Preparación de datos ---
cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
cat("  PASO 1/3: Preparación de datos\n")
cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
source("01_emIRT_data_prep.R")
cat("\n")

# --- Paso 2: Estimación del modelo + Bootstrap ---
cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
cat("  PASO 2/3: Estimación del modelo + Bootstrap\n")
cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
source("02_emIRT_model_run.R")
cat("\n")

# --- Paso 3: Diagnósticos ---
cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
cat("  PASO 3/3: Diagnósticos y visualización\n")
cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
source("03_emIRT_diagnostics.R")
cat("\n")

# --- Resumen final ---
pipeline_end <- Sys.time()
total_time <- difftime(pipeline_end, pipeline_start, units = "mins")

cat("╔═══════════════════════════════════════════════════════════════╗\n")
cat("║                   PIPELINE COMPLETADA                        ║\n")
cat("╠═══════════════════════════════════════════════════════════════╣\n")
cat(sprintf("║  Tiempo total: %.1f minutos                                  \n", as.numeric(total_time)))
cat(sprintf("║  Fin: %s                            \n", format(pipeline_end, "%Y-%m-%d %H:%M:%S")))
cat("╠═══════════════════════════════════════════════════════════════╣\n")
cat("║  Archivos generados:                                         ║\n")
cat("║    - emIRT_data_input.rds     (datos preparados)             ║\n")
cat("║    - emIRT_metadata.rds       (metadatos)                    ║\n")
cat("║    - emIRT_model_output.rds   (modelo dynIRT)                ║\n")
cat("║    - emIRT_model_inputs.rds   (starts/priors/control)        ║\n")
cat("║    - emIRT_bootstrap_output.rds (bootstrap SEs)              ║\n")
cat("║    - emIRT_summary_positions.csv/rds (resumen)               ║\n")
cat("║    - diagnostic_plots/        (visualizaciones)              ║\n")
cat("╚═══════════════════════════════════════════════════════════════╝\n")
