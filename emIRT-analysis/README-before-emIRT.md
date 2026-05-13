# Reporte y Plan de Implementación: Modelo Dinámico Bayesiano (emIRT)

Este documento sirve como "banco de memoria" y guía estructural para la transición del modelo de estimación por ventanas discretas de tiempo (W-NOMINATE / MCMC clásico) hacia un modelo dinámico continuo bayesiano (Dynamic Ideal Point Estimation / Martin-Quinn Model) utilizando el paquete `emIRT` en R.

---

## 1. El Objetivo Filosófico (Dynamic IRT vs Static IRT)
Históricamente en este proyecto, se implementó un **IRT Estático sobre subconjuntos temporales** dividiendo el trabajo de la Convención en 9 ventanas de tiempo y estimando ideal points para cada ventana de forma separada.
*   **Problema actual:** Disparidad gigantesca en el tamaño de las observaciones (ej. Ventana 7 = 2183 votos vs Ventana 4 = 52 votos). Al asumir los periodos como cajas aisladas, se pierde información (la estimación de la ventana 4 tiene márgenes de error enormes por falta de datos) y se asume falsamente que el "espacio" es idéntico entre la ventana 1 y la 9, requiriendo validaciones *post-hoc* como pruebas $t$ acopladas.
*   **La Solución emIRT (Martin-Quinn):** Un modelo unificado que asume una trayectoria dependiente del tiempo (*Random Walk Prior*: $\theta_{i,t} \sim \mathcal{N}(\theta_{i,t-1}, \Delta)$). En los periodos con pocos votos (Ventana 4), el algoritmo "pide prestada" la estabilidad de los periodos adyacentes. El espacio se vuelve constante y comparable de principio a fin, y las diferencias de posición decantan orgánicamente de la densidad del modelo bayesiano mediante intervalos de credibilidad, sin requerir tests estadísticos externos.

---

## 2. El Ecosistema Actual (MCMC / W-NOMINATE)

Si necesitas revisar el comportamiento antiguo de la estimación, estos son los archivos clave que debes mirar:

### A. Los Datos (Insumos)
*   `00_merged_pleno_all.R` y `01_ord_pleno_all.R`: Estos son los responsables de tomar los datos brutos de la Convención y consolidarlos.
*   `ideological-scaling-files/votaciones_*.csv` *(ej. votaciones_01_15.csv)*: Estos son los extractos crudos de votos `(Nay, Yea, Abstain, NA)` segmentados para que el modelo funcione. **Esttos son los archivos que tendrás que volver a cargar para armar la nueva matriz global de emIRT**.

### B. Los Modelos Actuales (Runners)
*   `02_ord_pleno_ventanas_t_MCMC.R` y `02_ord_pleno_ventanas_t_WNOM.R`.
*   **Cálculos internos de los modelos:** Con el enfoque antiguo, estos scripts no solo estimaban posiciones. Se encargaban dolorosamente de estimar la distribución (o de remuestrear via *Bootstrap* por 200/1000 repeticiones), y luego calculaban matemáticamente un **T-Test emparejado** (`dif_media := pos_ideol_final - pos_ideol_inicial` con cálculo de p-values) para poder certificar si, efectivamente, un convencional modificó o no su posición de un bloque $T$ a un bloque $T+1$.

---

## 3. Compatibilidad Visual: El Requisito RShiny

Para que no tengas que reconstruir tu código frontend de RShiny ni modificar un ápice de la visualización (`04_bump_chart_RShiny_coaliciones.R`), tu nueva arquitectura `emIRT` debe entregar los datos exactamente igual a como los entrega hoy el ecosistema MCMC.

El objetivo final de tus nuevos scripts es parsear los resultados de `emIRT` y re-construir el archivo `.rds` (actualmente `03_orden_votantes_t.rds`) con exactamente **5 columnas estrictas** que representan los "tramos" o deltas temporales:
1.  `Votante`: Nombre limpio del convencional (para cruzar con `coaliciones_convencionales.rds`).
2.  `Periodo1`: String indicando el inicio del bloque (ej. "01-15").
3.  `pos_ideol_inicial`: Coordenada latente en T1.
4.  `Periodo2`: String indicando el término del salto (ej. "16-21").
5.  `pos_ideol_final`: Coordenada latente en T2.

*(Nota: Shiny agrupa estos datos usando funciones como `bind_rows` para construir evoluciones o deltas, por tanto, el formato par (T1 -> T2) debe mantenerse intacto).*

---

## 4. Plan de Archivos a Desarrollar (Directorio `playground/emIRT-analysis/`)

Cuando retomes el proyecto, deberás enfocarte en crear y programar tres (3) scripts secuenciales de R dentro de esta carpeta, que reemplazarán eficientemente la serie `02_` y `03_` del método antiguo.

*   **Paso 1: `01_emIRT_data_prep.R`**
    *   **Objetivo:** Modificar el input estático. En vez de enviar 9 dataframes separados, `emIRT::dynIRT` (o sus variaciones) comúnmente requieren una lista de matrices cronológicas o un cubo de datos (`Legisladores x Votaciones x Tiempo`).
    *   **Acción:** Levantar todos los `votaciones_*.csv` y reestructurar a los estándares binarios que exige el `rollcall` de emIRT (-1, 1, NA).
*   **Paso 2: `02_emIRT_model_run.R`**
    *   **Objetivo:** La ejecución del modelo (Variational EM en vez de MCMC tradicional por lentitud).
    *   **Acción:** Definir priors (los anclajes de derecha e izquierda siguen existiendo para orientar la escala, como en el caso de Teresa Marinovic y los escaños reservados), establecer la varianza temporal $\Delta$, y correr la función principal (ej. `dynIRT()`). Guardar un `.rds` con el objeto crudo del modelo porque suele tardar bastante en converger.
*   **Paso 3: `03_emIRT_significance_and_shiny.R`**
    *   **Objetivo:** Digerir el modelo bayesiano para alimentar a Shiny y calcular el "significado" matemático del movimiento sin acudir a T-Tests post-hoc.
    *   **Acción:** Extraer la esperanza (Mean) y desviación estándar posterior (SD) para cada $(\theta_{t}, \theta_{t+1})$. En vez del t-test de antaño, calcular el cuantil empírico de la diferencia o los Intervalos de Credibilidad del 95% para cada convencional.
    *   **Salida Final:** Formatear los resultados y emular perfectamente las 5 columnas estructurales. Exportar como `03_orden_votantes_t_emIRT.rds`.
