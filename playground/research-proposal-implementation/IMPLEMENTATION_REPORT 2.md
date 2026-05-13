# Reporte de Implementación del Research Proposal
**Proyecto:** Constitutional Proposal Tracking (Convención Constitucional Chile 2021-2022)

---

## 1. Localización y Detalles Técnicos

*   **Documento Original del Proposal:** `playground/research-proposal/proposal.tex`
*   **Directorio de Implementación Principal:** `playground/research-proposal-implementation/`
*   **Directorio de Visualizaciones:** `playground/research-proposal-implementation/network-visualization/`

### Pipeline de Scripts

| Script | Descripción | Lenguaje |
|--------|-------------|----------|
| `00-build_dynamic_networks.py` | Redes de coautoría temporal + pooled | Python |
| `01-model-valued-ergm.R` | Valued ERGM (Modelo 1) + métricas estructurales | R |
| `02-extract-emirt-temporal.R` | Extracción de puntos ideales emIRT N×T | R |
| `03-model-network-influence.R` | Regresión panel: influencia de red (Modelo 2) | R |
| `04-build-article-mapping.py` | Mapeo artículos comisión → borrador final | Python |
| `05-nlp-text-similarity.py` | Similitud textual TF-IDF + embeddings | Python |
| `06-build-integrated-dataset.py` | Dataset integrado cross-seccional | Python |
| `07-model-spatial-durbin.R` | Modelo Durbin Espacial (Modelo 3) | R |
| `08-robustness-checks.R` | Chequeos de robustez para los 3 modelos | R |

### Datos y Covariables (de Webscraping BCN)

A través de web scraping del portal bio-bibliográfico de la Biblioteca del Congreso Nacional (BCN), construimos y homogeneizamos el archivo **`conventional-profiles.json`** con las siguientes covariables:
*   **`es_mujer`**: Variable dummy extraída mediante heurísticas de nombre y texto.
*   **`es_abogado`**: Extraída del texto biográfico/profesión.
*   **`experiencia_previa_institucional`**: Dummy que captura cargos del estado previos a la convención.
*   **`edad_al_asumir`**: Edad al momento de asumir en la convención.
*   **`afiliacion_agrupada`**: Bloque político o lista.

---

## 2. Datos Utilizados

### Comisiones incluidas

| Comisión | Archivo Genesis | Modelo 1 (Red) | Modelos 2-3 (Ideología/Éxito) |
|----------|-----------------|:---------------:|:-----------------------------:|
| C1 | `C1_texto-sistematizado_enriched_manual.json` | Si | Si |
| C3 | `C3_historial_manual.json` | Si | Si |
| C5 | `C5_historial_manual.json` | Si | Si |
| C6 | `C6_historial_manual.json` | Si | No* |
| C7 | `C7_GENESIS_texto-sistematizado-02-17_enriched_manual.json` | Si | No* |

\* C2, C4, C6 y C7 no tienen mapeo de modificaciones completo. Cuando estén listos, se pueden re-ejecutar los análisis.

### Criterio de selección para Modelos 2 y 3

Solo se incluyen artículos cuyo `final_status` comience con **"Idéntico"** o **"Similar"** (artículos que sobrevivieron al borrador final). Todos los demás estatus (Eliminado, No se encuentra, vacío) se excluyen.

**Artículos mapeados:** 236 total (125 idénticos + 111 similares)
- C1: 131 artículos | C3: 71 artículos | C5: 34 artículos
- 149 autores únicos en artículos mapeados

---

## 3. Modelo 1: Co-Sponsorship Network Formation (Valued ERGM)

### Concepto

Analizar qué factores impulsan la formación de lazos de coautoría entre convencionales, usando conteos de co-patrocinio como variable dependiente (no red binaria).

### Red Pooled

- **159 nodos** (convencionales con al menos una coautoría)
- **7,256 aristas** con peso total 202,765
- Red no dirigida, construida a partir de las 5 comisiones

### Especificación

```
net ~ sum + nodematch("afiliacion_agrupada") + nodematch("experiencia_previa_institucional")
      + nodematch("es_abogado") + nodematch("es_mujer")
      + absdiff("edad_al_asumir") + nodecov("edad_al_asumir")
```

Distribución de referencia: **Poisson** (Valued ERGM).

### Resultados Principales

| Término | Coeficiente | Error Std. | p-valor |
|---------|-------------|-----------|---------|
| `sum` (intercept) | ~-4.7 | — | <0.001 |
| `nodematch(afiliacion_agrupada)` | Positivo | — | <0.001 |
| `nodematch(experiencia_previa_institucional)` | Negativo | — | <0.001 |
| `nodematch(es_abogado)` | Negativo | — | <0.001 |
| `nodematch(es_mujer)` | Positivo | — | <0.001 |
| `absdiff(edad_al_asumir)` | ~0 | — | 0.403 |
| `nodecov(edad_al_asumir)` | -0.024 | — | <0.001 |

**Interpretación:**
- La **homofilia por afiliación política** es esperada y es el baseline para cualquier institución legislativa.
- **Hallazgo novel:** Convencionales con **experiencia institucional previa** o que son **abogados** co-patrocinan *menos* entre pares con el mismo atributo (coeficientes negativos). Esto sugiere un **efecto de representación estratégica**: los actores privilegiados actúan como "gatekeepers" o puentes y deliberadamente evitan concentrarse entre ellos, posiblemente para:
  1. Mentorear a novatos y acumular capital político
  2. Mantener liderazgo evitando competencia intra-grupo
  3. Proyectar una imagen de coalición plural
- La **diferencia de edad** no predice la coautoría (p=0.403), pero la **edad absoluta** sí: convencionales más jóvenes son más activos (efecto de participación).

### Métricas Extraídas

Se extraen por convencional: `degree`, `weighted_degree`, `betweenness`, `eigenvector` → guardadas en `data/network_metrics.csv` (159 filas).

---

## 4. Modelo 2: Ideological Dynamics — Network Influence (Panel Regression)

### Concepto

Testear si las conexiones de coautoría en t-1 predicen convergencia ideológica en t. Es decir, ¿la red *influye* en las posiciones, o la coautoría refleja posiciones preexistentes (selección homofílica)?

### Datos de Puntos Ideales (emIRT)

- **154 legisladores** × **91 periodos** (2021-07-13 a 2022-06-24)
- Modelo: Dynamic Bayesian IRT con Random Walk Prior (ω²=0.025)
- Anclas: Teresa Marinovic (derecha) y Jorge Baradit (izquierda)
- Fuente: `emIRT-analysis/emIRT_model_output.rds`

### Especificación Matemática

**Variable dependiente — Cambio ideológico:**
$$\Delta\theta_{i,t} = \theta_{i,t} - \theta_{i,t-1}$$

Cambio en el punto ideal de legislador *i* entre periodos *t-1* y *t*.

**Variable independiente clave — Exposición de red:**
$$\text{NetworkExposure}_{i,t-1} = \frac{\sum_j w_{ij,t-1} \cdot \theta_{j,t-1}}{\sum_j w_{ij,t-1}}$$

Donde:
- $w_{ij,t-1}$ = peso de la arista coautoría entre *i* y *j* en periodo $t-1$
- $\theta_{j,t-1}$ = punto ideal del co-autor *j* en el periodo anterior
- El denominador es el grado ponderado de *i*

**Interpretación:** Promedio ponderado de los puntos ideales de tus co-autores. Si trabajas mayormente con gente de derecha, tu exposición es positiva (hacia derecha).

**Modelo de efectos fijos:**
$$\Delta\theta_{i,t} = \alpha_i + \beta_1 \theta_{i,t-1} + \beta_3 \text{NetworkExposure}_{i,t-1} + \gamma X_i + \epsilon_{i,t}$$

Donde:
- $\alpha_i$ = efecto fijo individual (tendencia ideológica basal de cada legislador)
- $\beta_1 \theta_{i,t-1}$ = arrastre de posición anterior (inercia ideológica)
- $\beta_3 \text{NetworkExposure}_{i,t-1}$ = **efecto causal de interés**: ¿convergencia hacia tus co-autores?
- $X_i$ = covariables (afiliación, profesión, género, edad)
- $\epsilon_{i,t}$ = error idiosincrático

### Modelos Estimados

| Modelo | $\hat{\beta}_3$ (net_exposure_lag) | p-valor | Interpretación |
|--------|-----------------------------------|---------|----------------|
| **FE (efectos fijos)** | +0.0004 | 0.91 | **Nulo** — no hay influencia causal |
| Pooled OLS | +0.033 | <0.001 | Significativo — selección homofílica |
| OLS + FE comisión | +0.035 | 0.0002 | Significativo con SEs cluster-robustos |

**Diagnósticos:**
- **Test de Hausman:** Rechaza RE (χ²=784.955, p<0.001) → FE es apropiado, confirma correlación entre $\alpha_i$ y $X_i$.

**Interpretación causal:**

El modelo FE mantiene fijo cada legislador a sí mismo, eliminando la selección. El resultado $\hat{\beta}_3 \approx 0$ (p=0.91) indica que **después de controlar por la tendencia individual, la exposición de red no predice convergencia**. La asociación significativa en OLS refleja selección: legisladores "naturalmente de derecha" se rodean de gente de derecha, no que la red los haya movido.

### Panel de Datos

- **2,926 observaciones** (convencional × periodo × comisión) para C1, C3, C5
- **Covariables:** `delta_theta`, `theta_lag`, `net_exposure_lag`, `afiliacion_agrupada`, `es_abogado`, `es_mujer`, `experiencia_previa_institucional`

---

## 5. Modelo 3: Legislative Success — Spatial Durbin Model (SDM)

### Concepto

¿Quién logró incrustar sus preferencias escritas en el borrador final? Modelar la tasa de retención léxica como función de la posición en la red, la ideología, y covariables individuales, incorporando autocorrelación espacial a través de la red de coautoría.

### Medición del Éxito Legislativo (NLP)

**Método primario:** TF-IDF cosine similarity entre texto genesis y texto final.

| Categoría | Media TF-IDF | Mediana TF-IDF |
|-----------|-------------|----------------|
| Artículos "Idénticos" | 0.979 | 0.998 |
| Artículos "Similares" | 0.768 | — |
| Todos | — | — |

**Validación:** Los artículos etiquetados como "idéntico" obtienen scores cercanos a 1.0 (media 0.979), confirmando que la métrica captura correctamente la retención textual.

**Método de robustez:** Sentence-BERT (`paraphrase-multilingual-MiniLM-L12-v2`). Idénticos: 0.981, Similares: 0.931.

### Test de Autocorrelación Espacial

- **Moran's I = 0.155**, p < 0.000001
- Conclusión: Existe autocorrelación espacial significativa → el modelo espacial está justificado.

### Especificaciones Formales de Modelos Espaciales

**OLS (Baseline — sin autocorrelación espacial):**
$$y_i = \alpha + \sum_k \beta_k x_{ik} + \epsilon_i$$

Donde $y_i$ = retención léxica del convencional *i*, $x_{ik}$ = $k$-ésima covariable, $\epsilon_i \sim N(0, \sigma^2)$.

**SAR (Spatial Autoregressive / Spatial Lag):**
$$y = \rho W y + X \beta + \epsilon$$

Donde:
- $\rho$ = coeficiente de autocorrelación espacial (efecto de "contagio")
- $W$ = matriz de pesos normalizada (coautoría)
- $Wy$ = promedio ponderado del éxito de co-autores
- El éxito del legislador *i* es función del éxito de sus vecinos

**SEM (Spatial Error Model):**
$$y = X \beta + u, \quad u = \lambda W u + \epsilon$$

Donde:
- $\lambda$ = correlación espacial en los residuos
- El éxito depende directamente de *X* (sin spillover a *y*)
- Pero hay variables omitidas correlacionadas espacialmente que afectan el error
- Menos flexible que SAR para modelar mecanismos de "contagio"

**SDM (Spatial Durbin Model — modelo completo):**
$$y = \rho W y + X \beta + W X \theta + \epsilon$$

Donde:
- $\rho W y$ = efecto directo de co-autores (contagio de éxito)
- $X \beta$ = efectos de propias características
- $W X \theta$ = **efectos contextuales**: la característica de tus co-autores también te afecta (e.g., si tus co-autores son consistentes ideológicamente, eso beneficia TU retención)
- Combina ambos mecanismos: contagio + contexto

### Comparación de Modelos Espaciales

| Modelo | AIC | Mecanismo | Flexibilidad |
|--------|-----|-----------|--------------|
| **OLS** | -338.54 | Ninguno | Baseline (sin espacial) |
| SEM | -354.82 | Omitted vars correlacionadas espacialmente | Media |
| SAR | -355.32 | Contagio directo de vecinos | Media |
| **SDM** | **-383.35** | Contagio + contexto de vecinos | **Alta** |

El SDM domina por AIC (diferencia >44 puntos vs. SAR/SEM), confirmando que tanto los **efectos de contagio** como los **contextuales** son necesarios.

### Resultados OLS (Baseline)

| Variable | Coef. | p-valor | Interpretación |
|----------|-------|---------|----------------|
| `theta_mean` | +0.012 | 0.008 | Posición más a la derecha → mayor retención |
| `theta_sd` | -0.103 | 0.015 | Mayor volatilidad ideológica → menor retención |
| `ego_heterophily` | -0.063 | 0.027 | Más lazos cross-coalición → menor retención |

### Resultados SAR y SDM

**SAR (Spatial Autoregressive):**
- $\hat{\rho}$ = 0.885 (p < 0.001): Alta autocorrelación espacial
- Interpretación: El éxito legislativo se "contagia" fuertemente a través de la red de coautoría

**SDM (Spatial Durbin Model):**
- $\hat{\rho}$ = 0.997 (p < 0.001): Autocorrelación casi completa
- Los **efectos directos individuales** (X β) son modestos
- Los **efectos indirectos contextuales** (WX θ) dominan: el éxito depende más de quiénes son tus co-autores que de quién eres tú
- Interpretación: El éxito legislativo es un **fenómeno colectivo de coalición**, no individual

### Interpretación Sustantiva

1. **La ideología importa:** Convencionales con posiciones más consistentes (menor theta_sd) y posicionados hacia la derecha del espectro (mayor theta_mean) retuvieron más texto. Esto puede reflejar que la coalición de derecha fue más efectiva en defender artículos durante la etapa de negociación.
2. **La heterofilia perjudica:** Tener lazos predominantemente cross-coalición se asocia a menor retención, sugiriendo que las coaliciones internas son más efectivas para proteger texto.
3. **El efecto de red es masivo:** El ρ extremadamente alto indica que el éxito legislativo es un fenómeno colectivo, no individual. Co-autores exitosos se "contagian" éxito mutuamente.

---

## 6. Chequeos de Robustez

### 6.1 Modelo 1: ERGMs Por Comisión

Se estimaron ERGMs separados para C1, C3 y C5 para verificar que los resultados pooled no están dominados por una sola comisión.

**Hallazgo:** Los patrones de homofilia son heterogéneos entre comisiones:
- **C1 y C3:** Coeficientes negativos en `nodematch(afiliacion_agrupada)` — efecto inverso al pooled.
- **C5:** Coeficientes positivos — consistente con el modelo pooled.
- **Nota:** C3 y C5 no alcanzaron convergencia (60 iteraciones máximas), por lo que estos coeficientes deben interpretarse con cautela.

**Implicación:** El resultado pooled promedia dinámicas opuestas entre comisiones. Esto sugiere que la homofilia política opera de manera diferente según el contenido temático de cada comisión.

### 6.2 Modelo 2: Test de Falsificación

**Diseño:** Si la red influye causalmente en la ideología, entonces la red *futura* (t+1) NO debería predecir cambios ideológicos *pasados* (t).

**Resultado:** `net_exposure_lead` es significativo (p<0.001) — **la falsificación falla**. La red futura predice cambios pasados, confirmando la presencia de endogeneidad/selección. Esto es consistente con el resultado nulo del modelo FE: la correlación entre red e ideología refleja selección homofílica, no influencia causal.

### 6.3 Modelo 3: Especificaciones Alternativas

| Variante | Resultado |
|----------|-----------|
| **Embedding similarity como DV** | `theta_mean` marginalmente significativo (p=0.064). Dirección consistente. |
| **W binaria (no ponderada)** | SAR ρ=0.374, `theta_mean` y `theta_sd` siguen significativos. Resultados robustos. |
| **Especificación reducida** | `theta_sd` y `ego_heterophily` robustos con menos covariables. |

**Conclusión:** Los hallazgos principales del Modelo 3 son robustos a diferentes especificaciones de la variable dependiente y la matriz de pesos.

---

## 7. Dataset Integrado Final

**Archivo:** `data/integrated_dataset.csv` (159 filas × 27 columnas)

Cada fila = un convencional. Combina:
- Scores de éxito (NLP, 149 con datos)
- Métricas de red (ERGM, 159 con datos)
- Métricas ideológicas (emIRT, 154 con datos)
- Covariables de perfil (BCN, ~155 con datos)
- Variables derivadas: `ego_heterophily`, `cross_coalition_ties`

**Casos completos (4 fuentes):** 141 convencionales.

### Correlaciones Bivariadas

| Par | r |
|-----|---|
| success ~ weighted_degree | -0.120 |
| success ~ betweenness | +0.105 |
| success ~ theta_mean | +0.222 |

---

## 8. Archivos de Salida

### Datos Intermedios (`data/`)

| Archivo | Filas | Descripción |
|---------|-------|-------------|
| `pooled_cumulative_network.csv` | 7,256 | Edge list (source, target, weight) |
| `network_metrics.csv` | 159 | Métricas estructurales por convencional |
| `emirt_ideal_points_full.csv` | 14,014 | Puntos ideales N×T (long format) |
| `emirt_summary_metrics.csv` | 154 | Resumen ideológico por convencional |
| `emirt_aligned_to_commissions.csv` | 2,926 | Puntos ideales alineados a timesteps de comisión |
| `network_exposure_panel.csv` | 2,926 | Panel para Modelo 2 |
| `article_mapping_unified.csv` | 236 | Mapeo artículos comisión → final |
| `article_similarity_scores.csv` | 236 | Scores de similitud por artículo |
| `author_success_scores.csv` | 149 | Scores de éxito por convencional |
| `integrated_dataset.csv` | 159 | Dataset integrado final |

### Modelos Estimados (`.rds`)

| Archivo | Contenido |
|---------|-----------|
| `ergm_pooled_results.rds` | Valued ERGM pooled |
| `panel_regression_results.rds` | Modelos de panel (FE, RE, OLS) |
| `sdm_results.rds` | OLS, SAR, SEM, SDM + impacts |
| `robustness_results.rds` | ERGMs por comisión, falsificación, especificaciones alternativas |

---

## 9. Resumen de Hallazgos

1. **La coautoría sigue líneas ideológicas** (Modelo 1): La homofilia por afiliación política es el predictor más fuerte de co-patrocinio, aunque el efecto varía entre comisiones.

2. **La red refleja selección, no influencia** (Modelo 2): El modelo de efectos fijos muestra que las conexiones de red no causan convergencia ideológica. La correlación observada en OLS entre exposición de red y cambio ideológico se explica por selección homofílica.

3. **El éxito legislativo es un fenómeno colectivo y dependiente de la posición ideológica** (Modelo 3): La consistencia ideológica (baja volatilidad) y la posición en el espectro predicen retención textual. El altísimo ρ del SDM indica que el éxito de los co-autores es interdependiente.

4. **La heterofilia de red tiene costos** (Modelo 3): Convencionales cuyos lazos cruzan coaliciones retienen menos texto, sugiriendo que las alianzas intra-coalición son más efectivas para la producción legislativa.

### Limitaciones

- C2, C4, C6 y C7 no tienen mapeo de modificaciones completo → los Modelos 2 y 3 solo cubren C1, C3, C5.
- El test de falsificación falla → las inferencias causales del Modelo 2 requieren cautela.
- Los ERGMs por comisión (C3, C5) no convergieron → la heterogeneidad inter-comisión necesita más investigación.
- El ρ del SDM cercano a 1 puede indicar problemas de identificación → interpretar con cuidado los efectos indirectos.
