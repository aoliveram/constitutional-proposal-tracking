# =============================================================================
# 01_emIRT_data_prep.R
# Preparación de datos para estimación dinámica con emIRT::dynIRT()
#
# Carga los 9 archivos votaciones_*.csv, los unifica en una sola matriz
# rc (N×J) con codificación {-1, 0, 1} y construye el objeto .data
# que espera dynIRT(), usando cada fecha de sesión como un periodo temporal.
# =============================================================================

cat("=== 01_emIRT_data_prep.R ===\n")
cat("Preparando datos para emIRT...\n\n")

# --- Librerías ---
library(data.table)

# --- Configuración ---

# Ruta base al directorio de datos (relativa al proyecto raíz)
# Ajustar si se ejecuta desde un directorio diferente
DATA_DIR <- "../../ideological-scaling-files"

# Archivos de votación en orden cronológico
csv_files <- c(
  "votaciones_01_15.csv",
  "votaciones_16_21.csv",
  "votaciones_22_37.csv",
  "votaciones_38_46.csv",
  "votaciones_47_55.csv",
  "votaciones_56_75.csv",
  "votaciones_76_99.csv",
  "votaciones_100_106.csv",
  "votaciones_107_109.csv"
)

# Legislador a remover
REMOVE_LEGISLATOR <- "Rojas Vade, Rodrigo"

# --- Lista canónica de votantes (sin Rojas Vade) ---
# Idéntica a la usada en 01_ord_pleno_all.R y 02_ord_pleno_ventanas_samples_MCMC.R

votantes_apellido_nombre <- c(
  "Abarca, Damaris",
  "Abarca, Jorge",
  "Achurra, Ignacio",
  "Aguilera, Tiare",
  "Alvarado, Gloria",
  "Alvarez, Julio",
  "Alvarez, Rodrigo",
  "Alvez, Amaya",
  "Ampuero, Adriana",
  "Andrade, Cristobal",
  "Galleguillos, Felix",
  "Arancibia, Jorge",
  "Arauna, Francisca",
  "Arellano, Marco",
  "Arrau, Martin",
  "Atria, Fernando",
  "Bacian, Wilfredo",
  "Baradit, Jorge",
  "Baranda, Benito",
  "Barcelo, Luis",
  "Barraza, Marcos",
  "Bassa, Jaime",
  "Botto, Miguel Angel",
  "Bown, Carol",
  "Bravo, Daniel",
  "Caamano, Francisco",
  "Antilef, Victorino",
  "Chinga, Eric",
  "Calvo, Carlos",
  "Cancino, Adriana",
  "Cantuarias, Rocio",
  "Carrillo, Alondra",
  "Castillo, Maria Trinidad",
  "Castillo, Eduardo",
  "Castro, Claudia",
  "Catrileo, Rosa",
  "Celedon, Roberto",
  "Celis, Raul",
  "Cespedes, Lorena",
  "Chahin, Fuad",
  "Cozzi, Ruggero",
  "Cretton, Eduardo",
  "Cruz, Andres",
  "Cubillos, Marcela",
  "Daza, Mauricio",
  "De la Maza, Bernardo",
  "Delgado, Aurora",
  "Dominguez, Gaspar",
  "Dorador, Cristina",
  "Fernandez, Patricio",
  "Flores, Alejandra",
  "Fontaine, Bernardo",
  "Fuchslocher, Javier",
  "Gallardo, Bessy",
  "Garin, Renato",
  "Giustinianovich, Elisa",
  "Godoy, Isabel",
  "Gomez, Claudio",
  "Gomez, Yarela",
  "Gonzalez, Dayana",
  "Gonzalez, Lidia",
  "Grandon, Giovanna",
  "Grandon, Paola",
  "Gutierrez, Hugo",
  "Harboe, Felipe",
  "Henriquez, Natalia",
  "Hoppe, Vanessa",
  "Hube, Constanza",
  "Hurtado, Ruth",
  "Hurtado, Maximiliano",
  "Caiguan, Alexis",
  "Jimenez, Luis",
  "Jofre, Alvaro",
  "Jurgensen, Harry",
  "Labbe, Bastian",
  "Labra, Patricia",
  "Labrana, Elsa",
  "Laibe, Tomas",
  "Larrain, Hernan",
  "Letelier, Margarita",
  "Linconao, Francisca",
  "Llanquileo, Natividad",
  "Logan, Rodrigo",
  "Loncon, Elisa",
  "Madriaga, Tania",
  "Mamani, Isabella",
  "Marinovic, Teresa",
  "Martin, Juan Jose",
  "Martinez, Helmuth",
  "Mayol, Luis",
  "Mella, Jeniffer",
  "Mena, Felipe",
  "Meneses, Janis",
  "Millabur, Adolfo",
  "Miranda, Valentina",
  "Monckeberg, Cristian",
  "Montealegre, Katerine",
  "Montero, Ricardo",
  "Moreno, Alfredo",
  "Munoz, Pedro",
  "Namor, Guillermo",
  "Navarrete, Geoconda",
  "Neumann, Ricardo",
  "Nunez, Nicolas",
  "Olivares, Ivanna",
  "Orellana, Matias",
  "Ossandon, Manuel",
  "Oyarzun, Maria Jose",
  "Perez, Alejandra",
  "Pinto, Malucha",
  "Politzer, Patricia",
  "Portilla, Ericka",
  "Pustilnick, Tammy",
  "Quinteros, Maria Elisa",
  "Rebolledo, Barbara",
  "Reyes, Maria Ramona",
  "Rivera, Pollyana",
  "Rivera, Maria Magdalena",
  "Roa, Giovanna",
  "Rojas, Rodrigo",      # <--- Será removido (posición 120)
  "Royo, Manuela",
  "Saldana, Alvin",
  "Salinas, Fernando",
  "San Juan, Constanza",
  "Sanchez, Beatriz",
  "Schonhaut, Constanza",
  "Sepulveda, Barbara",
  "Sepulveda, Carolina",
  "Serey, Mariela",
  "Silva, Luciano",
  "Squella, Agustin",
  "Stingo, Daniel",
  "Tepper, Maria Angelica",
  "Tirado, Fernando",
  "Toloza, Pablo",
  "Ubilla, Maria Cecilia",
  "Uribe, Cesar",
  "Urrutia, Tatiana",
  "Valenzuela, Cesar",
  "Valenzuela, Paulina",
  "Vallejos, Loreto",
  "Vargas, Margarita",
  "Vargas, Mario",
  "Vega, Roberto",
  "Velasquez, Hernan",
  "Veloso, Paulina",
  "Vergara, Lisette",
  "Vidal, Rossana",
  "Videla, Carolina",
  "Viera, Christian",
  "Vilches, Carolina",
  "Villena, Ingrid",
  "Woldarsky, Manuel",
  "Zarate, Camila",
  "Zuniga, Luis Arturo"
)

# Remover Rojas Vade del vector de nombres canónicos
idx_rojas <- which(votantes_apellido_nombre == "Rojas, Rodrigo")
if (length(idx_rojas) == 1) {
  votantes_apellido_nombre <- votantes_apellido_nombre[-idx_rojas]
  cat("Removido 'Rojas, Rodrigo' del vector (posición", idx_rojas, ")\n")
} else {
  warning("No se encontró 'Rojas, Rodrigo' en el vector de nombres. Verificar.")
}
N <- length(votantes_apellido_nombre)

cat("Legisladores (tras remover Rojas Vade):", N, "\n")

# --- Identificar anclas ---
idx_derecha   <- which(votantes_apellido_nombre == "Marinovic, Teresa")
idx_izquierda <- which(votantes_apellido_nombre == "Baradit, Jorge")

cat("Ancla derecha (Marinovic)  -> idx_derecha =", idx_derecha, "\n")
cat("Ancla izquierda (Baradit)  -> idx_izquierda =", idx_izquierda, "\n\n")

stopifnot(length(idx_derecha) == 1, length(idx_izquierda) == 1)

# =============================================================================
# PASO 1: Cargar y limpiar los 9 CSVs
# =============================================================================

cat("--- Paso 1: Cargando y limpiando CSVs ---\n")

all_vote_matrices <- list()
all_col_names     <- character(0)

for (i in seq_along(csv_files)) {
  filepath <- file.path(DATA_DIR, csv_files[i])
  cat("  Cargando:", csv_files[i], "...")
  
  # Leer CSV
  df <- as.data.frame(read.csv(filepath, check.names = FALSE))
  
  # La primera columna es el nombre del votante
  # Remover a Rojas Vade usando match exacto del string "Rojas Vade"
  name_col <- df[[1]]
  if (is.factor(name_col)) name_col <- as.character(name_col)
  
  # Filtrar Rojas Vade usando match exacto (evita falsos positivos como "Caamaño Rojas")
  rojas_mask <- grepl("Rojas Vade", name_col, fixed = TRUE)
  df <- df[!rojas_mask, , drop = FALSE]
  
  # Extraer solo las columnas de votación (sin la columna de nombres)
  vote_data <- df[, -1, drop = FALSE]
  
  # Convertir todo a numérico
  vote_data <- as.data.frame(lapply(vote_data, function(x) {
    suppressWarnings(as.numeric(as.character(x)))
  }))
  
  cat(" ", nrow(vote_data), "legisladores,", ncol(vote_data), "votaciones\n")
  
  # Guardar
  all_vote_matrices[[i]] <- as.matrix(vote_data)
  all_col_names <- c(all_col_names, colnames(vote_data))
}

# =============================================================================
# PASO 2: Concatenar horizontalmente
# =============================================================================

cat("\n--- Paso 2: Concatenando matrices ---\n")

# Verificar que todas tienen el mismo número de filas
n_rows <- sapply(all_vote_matrices, nrow)
cat("  Filas por CSV:", paste(n_rows, collapse = ", "), "\n")

# Algunas ventanas pueden tener un número ligeramente diferente de filas
# (ej. votaciones_47_55 tenía filas extras removidas en el script original).
# Usamos N = 153 como referencia y verificamos.
# Si alguna tiene más de 153 filas, cortamos a las primeras 153.
# Si tiene menos, es un error.
for (i in seq_along(all_vote_matrices)) {
  if (nrow(all_vote_matrices[[i]]) > N) {
    cat("  ADVERTENCIA:", csv_files[i], "tiene", nrow(all_vote_matrices[[i]]),
        "filas. Truncando a", N, ".\n")
    all_vote_matrices[[i]] <- all_vote_matrices[[i]][1:N, , drop = FALSE]
  } else if (nrow(all_vote_matrices[[i]]) < N) {
    stop(paste("ERROR:", csv_files[i], "tiene solo", nrow(all_vote_matrices[[i]]),
               "filas. Se esperaban", N))
  }
}

# Concatenar
rc_raw <- do.call(cbind, all_vote_matrices)
J <- ncol(rc_raw)

cat("  Matriz concatenada: ", N, "x", J, "\n")
cat("  Total votaciones:", J, "\n")

# Asignar nombres de filas (legisladores)
rownames(rc_raw) <- votantes_apellido_nombre

# =============================================================================
# PASO 3: Recodificar votos para emIRT
# =============================================================================

cat("\n--- Paso 3: Recodificando votos ---\n")
cat("  Codificación original: 1=Yea, 0=Nay, NA=Missing\n")
cat("  Codificación emIRT:    1=Yea, -1=Nay, 0=Missing\n")

# Distribución antes de recodificar
cat("  Distribución original:\n")
cat("    1 (Yea):", sum(rc_raw == 1, na.rm = TRUE), "\n")
cat("    0 (Nay):", sum(rc_raw == 0, na.rm = TRUE), "\n")
cat("    NA (Missing):", sum(is.na(rc_raw)), "\n")

# Recodificar: IMPORTANTE - el orden de operaciones importa
# Primero: NA → placeholder, luego 0 → -1, luego placeholder → 0
rc_mat <- rc_raw
rc_mat[is.na(rc_mat)] <- 99     # Placeholder temporal
rc_mat[rc_mat == 0]   <- -1     # Nay: 0 → -1
rc_mat[rc_mat == 99]  <- 0      # Missing: NA → 0

cat("  Distribución emIRT:\n")
cat("     1 (Yea):", sum(rc_mat == 1), "\n")
cat("    -1 (Nay):", sum(rc_mat == -1), "\n")
cat("     0 (Missing):", sum(rc_mat == 0), "\n")

# Verificación
unique_vals <- sort(unique(as.vector(rc_mat)))
cat("  Valores únicos en rc_mat:", paste(unique_vals, collapse = ", "), "\n")
stopifnot(all(unique_vals %in% c(-1, 0, 1)))

# =============================================================================
# PASO 4: Extraer fechas y construir bill.session
# =============================================================================

cat("\n--- Paso 4: Extrayendo fechas de columnas y construyendo bill.session ---\n")

# Los nombres de columna tienen formato: XDDMMYYYY_VotacionID
# Extraemos la parte de la fecha

col_names <- all_col_names
# Limpiar comillas si existen
col_names <- gsub('"', '', col_names)

# Extraer la parte DDMMYYYY de cada nombre de columna
extract_date <- function(col_name) {
  # Formato: XDDMMYYYY_VotacionID  o  "XDDMMYYYY_VotacionID"
  # Extraemos los 8 dígitos después de la X
  date_str <- regmatches(col_name, regexpr("[0-9]{8}", col_name))
  if (length(date_str) == 0) return(NA)
  
  # Parsear DDMMYYYY → Date
  as.Date(date_str, format = "%d%m%Y")
}

# Aplicar a todas las columnas
vote_dates <- sapply(col_names, extract_date)
vote_dates <- as.Date(vote_dates, origin = "1970-01-01")

# Verificar si hay columnas con fechas no parseables (ej. XNA_4185)
n_na_dates <- sum(is.na(vote_dates))
if (n_na_dates > 0) {
  bad_cols <- col_names[is.na(vote_dates)]
  cat("  ADVERTENCIA:", n_na_dates, "columna(s) sin fecha parseable:\n")
  cat("    ", paste(bad_cols, collapse = ", "), "\n")
  cat("  Removiendo estas columnas de rc_mat y de la lista de columnas...\n")
  
  # Encontrar los índices de columnas válidas
  valid_cols <- !is.na(vote_dates)
  
  # Filtrar la matriz de votos y las fechas
  rc_mat <- rc_mat[, valid_cols, drop = FALSE]
  vote_dates <- vote_dates[valid_cols]
  col_names <- col_names[valid_cols]
  J <- ncol(rc_mat)  # Actualizar J
  
  cat("  Nueva dimensión rc_mat:", nrow(rc_mat), "×", J, "\n")
}

stopifnot(length(vote_dates) == J)
stopifnot(sum(is.na(vote_dates)) == 0)  # No NAs restantes

# Obtener fechas únicas ordenadas cronológicamente
unique_dates <- sort(unique(vote_dates))
T_periods <- length(unique_dates)

cat("  Fechas únicas (periodos):", T_periods, "\n")
cat("  Rango temporal:", format(min(unique_dates), "%d/%m/%Y"), "→",
    format(max(unique_dates), "%d/%m/%Y"), "\n")

# Construir bill.session: para cada votación, su índice de periodo (0-based)
bill_session <- match(vote_dates, unique_dates) - 1L  # 0-indexed

# CRÍTICO: dynIRT requiere que bill_session esté ordenado cronológicamente
# (monotónicamente no-decreciente). El C++ interno (getLast_dynIRT.cpp) asume
# que las votaciones están ordenadas por periodo.
sort_order <- order(bill_session)
bill_session <- bill_session[sort_order]
rc_mat <- rc_mat[, sort_order, drop = FALSE]
vote_dates <- vote_dates[sort_order]
col_names <- col_names[sort_order]

cat("  bill_session ordenado cronológicamente ✓\n")
cat("  Rango bill.session:", min(bill_session), "-", max(bill_session), "\n")
cat("  ¿Monotónicamente no-decreciente?:", all(diff(bill_session) >= 0), "\n")

stopifnot(length(bill_session) == J)
stopifnot(!anyNA(bill_session))
stopifnot(min(bill_session) == 0)
stopifnot(max(bill_session) == T_periods - 1)
stopifnot(all(diff(bill_session) >= 0))  # DEBE ser monotónicamente no-decreciente

# Tabla de votaciones por periodo
votes_per_period <- table(bill_session)
cat("\n  Distribución de votaciones por periodo (primeros 10):\n")
print(head(votes_per_period, 10))
cat("  ...\n")
cat("  Min votos/periodo:", min(votes_per_period),
    "| Max:", max(votes_per_period),
    "| Mediana:", median(as.numeric(votes_per_period)), "\n")

# =============================================================================
# PASO 5: Construir startlegis y endlegis
# =============================================================================

cat("\n--- Paso 5: Construyendo startlegis y endlegis ---\n")

# Todos los convencionales sirvieron durante todo el periodo
startlegis <- matrix(0L, nrow = N, ncol = 1)
endlegis   <- matrix(as.integer(T_periods - 1), nrow = N, ncol = 1)

cat("  startlegis: todos =", startlegis[1], "\n")
cat("  endlegis:   todos =", endlegis[1], "\n")

# =============================================================================
# PASO 6: Ensamblar y exportar objeto .data
# =============================================================================

cat("\n--- Paso 6: Ensamblando objeto .data para dynIRT ---\n")

emIRT_data <- list(
  rc           = rc_mat,                          # N × J matrix
  startlegis   = startlegis,                      # N × 1 matrix
  endlegis     = endlegis,                        # N × 1 matrix
  bill.session = matrix(bill_session, ncol = 1),  # J × 1 matrix
  T            = as.integer(T_periods)             # integer
)

# Resumen final
cat("  Dimensiones finales:\n")
cat("    rc:           ", nrow(emIRT_data$rc), "×", ncol(emIRT_data$rc), "\n")
cat("    startlegis:   ", nrow(emIRT_data$startlegis), "×", ncol(emIRT_data$startlegis), "\n")
cat("    endlegis:     ", nrow(emIRT_data$endlegis), "×", ncol(emIRT_data$endlegis), "\n")
cat("    bill.session: ", nrow(emIRT_data$bill.session), "×", ncol(emIRT_data$bill.session), "\n")
cat("    T:            ", emIRT_data$T, "\n")

# Guardar
output_path <- "emIRT_data_input.rds"
saveRDS(emIRT_data, output_path)
cat("\n  Objeto .data guardado en:", output_path, "\n")

# También guardamos metadatos útiles
metadata <- list(
  votantes       = votantes_apellido_nombre,
  idx_derecha    = idx_derecha,
  idx_izquierda  = idx_izquierda,
  unique_dates   = unique_dates,
  N              = N,
  J              = J,
  T_periods      = T_periods,
  csv_files_used = csv_files
)
saveRDS(metadata, "emIRT_metadata.rds")
cat("  Metadatos guardados en: emIRT_metadata.rds\n")

cat("\n=== 01_emIRT_data_prep.R completado ===\n")
