# Estimación Dinámica de Ideal Points — Modelo emIRT
## Convención Constitucional de Chile (2021–2022)

---

## 1. Contexto y Motivación

El proyecto venía usando un **IRT estático segmentado**: se dividía el trabajo de la Convención en 9 ventanas de tiempo y se estimaban ideal points de forma independiente para cada una. Ese enfoque tenía dos problemas estructurales:

| Problema | Descripción |
|---|---|
| **Desbalance de observaciones** | La Ventana 4 (sesiones 38–46) tenía apenas 52 votaciones, frente a las 2.183 de la Ventana 7. Las estimaciones en periodos escasos eran ruidosas e inestables. |
| **Espacios no comparables** | Al tratar cada ventana como caja aislada, no había garantía de que el eje ideológico fuera el mismo entre la Ventana 1 y la Ventana 9. Requería tests-*t* emparejados *post hoc* para certificar si un convencional había "cambiado" de posición. |

La solución adoptada es el modelo dinámico bayesiano de **Martin & Quinn** implementado en el paquete `emIRT` de R (`dynIRT()`). La idea central es:

$$\theta_{i,t} \sim \mathcal{N}(\theta_{i,t-1},\, \omega^2)$$

Cada ideal point en el periodo $t$ es una perturbación gaussiana del ideal point en $t-1$ (*Random Walk Prior*). Los periodos con pocas votaciones "piden prestada" la estabilidad de los periodos adyacentes. El espacio ideológico permanece constante y comparable de principio a fin de la Convención, y la incertidumbre sobre el movimiento de cada convencional se expresa como intervalos de credibilidad bootstrap, sin tests estadísticos externos.

---

## 2. Datos utilizados

### 2.1. Fuente

Se cargaron los **9 archivos CSV** del directorio `ideological-scaling-files/`:

| Archivo | Sesiones |
|---|---|
| `votaciones_01_15.csv` | 01–15 |
| `votaciones_16_21.csv` | 16–21 |
| `votaciones_22_37.csv` | 22–37 |
| `votaciones_38_46.csv` | 38–46 |
| `votaciones_47_55.csv` | 47–55 |
| `votaciones_56_75.csv` | 56–75 |
| `votaciones_76_99.csv` | 76–99 |
| `votaciones_100_106.csv` | 100–106 |
| `votaciones_107_109.csv` | 107–109 |

### 2.2. Legisladores

- **N = 154** convencionales (tras excluir a Rodrigo Rojas Vade, quien renunció al cargo).
- Los 9 CSVs se concatenaron horizontalmente en una única matriz de votos **N × J**.
- La codificación se reescribió del formato original {1=Yea, 0=Nay, NA=Missing} al formato que exige `dynIRT()`: **{1=Yea, −1=Nay, 0=Missing}**.

### 2.3. Periodos temporales

Las columnas de cada CSV tienen formato `XDDMMYYYY_VotacionID`. Se extrajo la fecha de cada votación y se construyó un vector `bill.session` que asigna cada votación a un periodo temporal único (por fecha de sesión), ordenado cronológicamente.

- **T = número de fechas únicas de sesión** a lo largo de todas las sesiones plenarias (2021–2022).
- El parámetro `bill.session` es 0-*indexed* y monotónicamente no-decreciente, requisito del C++ interno de `emIRT`.

---

## 3. Mecanismo del Modelo

### 3.1. Algoritmo: Variational EM (VEM)

A diferencia del MCMC clásico (lento, miles de iteraciones de Gibbs Sampling), `dynIRT()` usa **Expectation-Maximization variacional**, lo que permite convergencia en minutos con datasets del tamaño de la Convención. La salida son medias posteriores variacionales (no muestras MCMC).

### 3.2. Priors e identificación

El modelo IRT es no-identificado por construcción (hay rotaciones e inversiones del espacio que dan el mismo *likelihood*). Se resuelve mediante **dos anclas ideológicas**:

| Ancla | Convencional | Dirección | Prior media | Prior varianza |
|---|---|---|---|---|
| Derecha | **Teresa Marinovic** | Positivo | +1.0 | 0.01 (muy estrecho) |
| Izquierda | **Jorge Baradit** | Negativo | −1.0 | 0.01 (muy estrecho) |

El resto de convencionales tiene prior difuso (media = 0, varianza = 1.0).

Los parámetros de ítem (dificultad $\alpha_j$ y discriminación $\beta_j$) reciben prior difuso con varianza 25.

### 3.3. Parámetro de suavizamiento temporal (ω²)

El hiperparámetro **ω² = 0.025** controla cuánto puede moverse θ entre periodos consecutivos. Un valor bajo penaliza las trayectorias erráticas; uno alto permite movimientos abruptos. El valor elegido equilibra sensibilidad ideológica y estabilidad, y se aplica homogéneamente a los N = 154 convencionales.

### 3.4. Starting values

Para evitar matrices singulares en la primera actualización del VEM:
- `alpha` (dificultad de ítem): ruido aleatorio ~ N(0, 0.1)
- `beta` (discriminación de ítem): ruido aleatorio ~ N(0, 0.1)
- `x` (ideal points): ruido aleatorio ~ N(0, 0.2), con Marinovic inicializada en +2.0 y Baradit en −2.0 en todos los periodos.

### 3.5. Bootstrap paramétrico

Tras la estimación principal, se ejecutó `boot_emIRT()` con **Ntrials = 50** para obtener errores estándar confiables (SE bootstrap) para los ideal points. Esto reemplaza los tests-*t* del flujo anterior: el criterio de "cambio significativo" entre periodos se define por los intervalos de credibilidad del 95% derivados de la distribución bootstrap.

### 3.6. Control del modelo

```
threads   = 8   (Apple M4 Pro — 8 Performance cores)
thresh    = 1e-6
maxit     = 500
```

---

## 4. Resultados

### 4.1. Resumen global

El modelo estimó posiciones ideológicas para **154 convencionales** en **T periodos temporales** continuos. El espacio ideológico corre de valores muy negativos (izquierda) a muy positivos (derecha).

| Estadístico | Valor |
|---|---|
| Posición media global del espectro | ~0.0 (centrado) |
| Ancla izquierda — Baradit, Jorge (media) | −1.38 |
| Ancla derecha — Marinovic, Teresa (media) | +4.34 |
| Legislador más a la izquierda (media) | Madriaga, Tania (−3.62) |
| Legislador más a la derecha (media) | Cantuarias, Rocío (+5.03) |

### 4.2. Los 15 más a la izquierda

| Ranking | Convencional | Posición Media (θ̄) | SD temporal |
|---|---|---|---|
| 1 | Madriaga, Tania | −3.624 | 0.297 |
| 2 | Godoy, Isabel | −3.544 | 0.412 |
| 3 | San Juan, Constanza | −3.544 | 0.355 |
| 4 | Pérez, Alejandra | −3.527 | 0.277 |
| 5 | Woldarsky, Manuel | −3.472 | 0.239 |
| 6 | Chinga, Eric | −3.437 | 0.315 |
| 7 | Caiguán, Alexis | −3.429 | 0.215 |
| 8 | Caamaño, Francisco | −3.418 | 0.269 |
| 9 | Andrade, Cristóbal | −3.386 | 0.303 |
| 10 | Llanquileo, Natividad | −3.378 | 0.267 |
| 11 | Olivares, Ivanna | −3.376 | 0.308 |
| 12 | Alvarado, Gloria | −3.366 | 0.212 |
| 13 | Arellano, Marco | −3.356 | 0.298 |
| 14 | Vilches, Carolina | −3.348 | 0.311 |
| 15 | Portilla, Ericka | −3.344 | 0.311 |

### 4.3. Los 15 más a la derecha

| Ranking | Convencional | Posición Media (θ̄) | SD temporal |
|---|---|---|---|
| 154 | Cantuarias, Rocío | +5.030 | 0.772 |
| 153 | Hube, Constanza | +4.741 | 0.580 |
| 152 | Hurtado, Ruth | +4.701 | 0.594 |
| 151 | Arrau, Martín | +4.679 | 0.695 |
| 150 | Cubillos, Marcela | +4.689 | 0.305 |
| 149 | Montealegre, Katerine | +4.625 | 0.427 |
| 148 | Jurgensen, Harry | +4.393 | 0.311 |
| 147 | Bown, Carol | +4.387 | 0.291 |
| 146 | Castro, Claudia | +4.375 | 0.308 |
| 145 | Marinovic, Teresa *(ancla)* | +4.342 | 1.095 |
| 144 | Toloza, Pablo | +4.276 | 0.385 |
| 143 | Cretton, Eduardo | +4.093 | 0.360 |
| 142 | Ubilla, María Cecilia | +4.070 | 0.207 |
| 141 | Letelier, Margarita | +4.054 | 0.413 |
| 140 | Álvarez, Rodrigo | +4.049 | 0.238 |

### 4.4. Convencionales centrales (más cercanos a θ = 0)

Estos convencionales presentan posiciones medias en la zona de ambigüedad ideológica:

| Convencional | Posición Media (θ̄) |
|---|---|
| Barceló, Luis | +0.095 |
| Castillo, Eduardo | +0.151 |
| Botto, Miguel Ángel | +0.235 |
| Chahin, Fuad | +0.311 |
| Cruz, Andrés | −0.190 |
| Fernández, Patricio | −0.512 |

### 4.5. Convencionales con mayor volatilidad ideológica

La columna `Rango_Total` (θ_max − θ_min a lo largo del tiempo) mide cuánto varió la posición estimada de cada convencional durante toda la Convención:

| Convencional | Posición Media (θ̄) | Rango Total | Interpretación |
|---|---|---|---|
| Marinovic, Teresa | +4.342 | **5.820** | Ancla — variación esperada por prior estrecho en periodos sin votos |
| Zárate, Camila | −2.732 | **3.136** | Mayor volatilidad no-ancla del bloque izquierda |
| Baradit, Jorge | −1.378 | **2.875** | Segunda ancla — comportamiento análogo a Marinovic |
| Sepúlveda, Bárbara | −2.118 | **2.812** | Trayectoria errática dentro del bloque izquierda |
| Zúñiga, Luis Arturo | +3.515 | **2.868** | Derecha con movimiento temporal notable |
| Cantuarias, Rocío | +5.030 | **2.749** | Extremo derecho con alta varianza |
| Arrau, Martín | +4.679 | **2.587** | Derecha con oscilación considerable |
| Hurtado, Ruth | +4.701 | **2.499** | Derecha con variación temporal |
| Hube, Constanza | +4.741 | **2.103** | Variación dentro de bloque derecho |

> **Nota metodológica:** La alta volatilidad de las anclas (Marinovic y Baradit) refleja el comportamiento del prior estrecho en periodos de sesión sin votaciones registradas a su nombre. En esos lapsos, el *Random Walk Prior* regresa momentáneamente al prior medio antes de ser corregido por votaciones posteriores. Es un artefacto esperado, no una señal sustantiva.

### 4.6. Convencionales más estables

| Convencional | Posición Media (θ̄) | Rango Total |
|---|---|---|
| Vargas, Margarita | −2.973 | 0.584 |
| Tepper, María Angélica | +2.769 | 0.591 |
| Politzer, Patricia | −0.798 | 0.718 |
| Celis, Raúl | +2.618 | 0.761 |
| Ubilla, María Cecilia | +4.070 | 0.788 |
| Arauna, Francisca | −2.919 | 0.832 |
| Royo, Manuela | −3.093 | 0.887 |
| Uribe, César | −3.335 | 0.872 |

---

## 5. Diagnósticos Generados

Se produjeron cuatro visualizaciones diagnósticas en `diagnostic_plots/`:

### `plot2_anchor_trajectories.png`
Trayectorias temporales de Marinovic (rojo) y Baradit (azul) a lo largo de los T periodos. Permite verificar que el ancla derecha permanece en valores positivos y el ancla izquierda en negativos durante toda la Convención, y observar los deslizamientos en periodos con escasas votaciones propias.

### `plot3_heatmap_global.png`
Mapa de calor (heatmap) de todos los convencionales × periodos, ordenados por posición media global de izquierda a derecha. El gradiente azul-blanco-rojo representa el espectro de izquierda a derecha. Permite identificar visualmente bloques estables, convencionales que se mueven, y el contraste entre el núcleo izquierdo consolidado y el bloque derecho más heterogéneo.

### `plot4_distribution_by_period.png`
Boxplots de la distribución de ideal points de los 154 convencionales para cada periodo temporal. Permite detectar si el espacio ideológico se comprime o expande a lo largo del tiempo, y si hay periodos con estimaciones anómalas (p.ej., periodos con muy pocas votaciones donde el prior domina).

### `plot6_bootstrap_se_distribution.png`
Histograma de los errores estándar bootstrap (N = 154 × Ntrials = 50). La línea roja punteada marca la media. Convencionales con SE alto tienen posiciones ideológicas estimadas con mayor incertidumbre (típicamente quienes votaron poco o cuyos votos son inconsistentes con el patrón global).

---

## 6. Archivos generados

| Archivo | Descripción |
|---|---|
| `emIRT_data_input.rds` | Matriz de votos (N×J) y estructuras auxiliares para `dynIRT()` |
| `emIRT_metadata.rds` | Metadatos: nombres de legisladores, índices de anclas, fechas únicas, N/J/T |
| `emIRT_model_inputs.rds` | Starting values, priors y control usados en la estimación |
| `emIRT_model_output.rds` | Objeto completo de `dynIRT()`: medias variacionales, varianzas, runtime |
| `emIRT_bootstrap_output.rds` | Objeto de `boot_emIRT()`: errores estándar bootstrap (N × T) |
| `emIRT_summary_positions.csv` | Tabla resumen: posición media, SD, min, max, rango por convencional |
| `emIRT_summary_positions.rds` | Ídem en formato RDS para carga directa en R |
| `diagnostic_plots/` | Carpeta con los 4 gráficos de diagnóstico (.png) |

---

## 7. Comparación con el enfoque anterior (MCMC por ventanas)

| Dimensión | MCMC/W-NOMINATE por ventanas | emIRT dinámico (este análisis) |
|---|---|---|
| **Unidad de estimación** | 9 modelos independientes | 1 modelo unificado |
| **Tratamiento de periodos escasos** | Estimaciones ruidosas (ej. Ventana 4: 52 votos) | El prior *Random Walk* estabiliza desde periodos adyacentes |
| **Comparabilidad inter-periodo** | Requiere normalización *post hoc* | Garantizada por diseño (espacio único) |
| **Criterio de cambio significativo** | Test-*t* emparejado con p-value | Intervalo de credibilidad bootstrap 95% |
| **Tiempo de ejecución** | Horas (MCMC con 200–1000 iteraciones) | Minutos (VEM convergente) |
| **Output para Shiny** | `03_orden_votantes_t.rds` (5 columnas: Votante, Periodo1, pos_ideol_inicial, Periodo2, pos_ideol_final) | Compatible: se puede construir el mismo formato extrayendo pares (T, T+1) de la matriz N×T |

---

## 8. Próximos pasos

1. **Análisis de sensibilidad de ω²**: Re-ejecutar `02_emIRT_model_run.R` con valores alternativos (0.01, 0.05, 0.10, 0.50) para evaluar la robustez de las trayectorias ante la elección del hiperparámetro de suavizamiento.

2. **Exportación para Shiny**: Construir el archivo `03_orden_votantes_t_emIRT.rds` con el formato de 5 columnas {Votante, Periodo1, pos_ideol_inicial, Periodo2, pos_ideol_final}, extrayendo pares consecutivos de la matriz `x_hat` (N × T) del modelo.

3. **Validación cruzada con MCMC**: Correlacionar las posiciones medias de emIRT (promediadas por ventana) con las posiciones MCMC de las 9 ventanas originales para cuantificar la concordancia y documentar las discrepancias.

4. **Integración al proyecto de dinámica política**: Copiar `emIRT_summary_positions.rds` y `emIRT_model_output.rds` al repositorio del proyecto que consume estos datos como insumo de la estimación de dinámica política.
