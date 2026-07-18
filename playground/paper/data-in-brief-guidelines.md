# Guía para el paper en *Data in Brief* (Elsevier)

> Documento de trabajo para Aníbal y Vicente. Resume (1) los requisitos formales del journal, (2) cómo estructuró Jorge Fábrega su artículo publicado, (3) las referencias verificadas que usaremos, y (4) los pendientes específicos de nuestro dataset antes del envío.
> Última actualización: 2026-07-03.

---

## 1. Qué es un *data article* en Data in Brief

*Data in Brief* (ISSN 2352-3409, Elsevier) publica **descripciones de datasets**, no investigación. El dato **no se juzga por su significancia sino por su utilidad y potencial de reúso**. El artículo debe poder leerse de forma autónoma (self-contained) y su única función es anunciar, describir y hacer citable el dataset.

Reglas de oro del journal (fuente: plantilla oficial v.19, dic. 2024, y guía "How to write a good Data in Brief article" del Editor-in-Chief Hao-Ran Wang):

- **NO incluir** secciones de Conclusión, Discusión o Resumen.
- **NO usar** palabras como *study*, *results*, *conclusions* en el texto; **evitar** *effects*, *evidence*, *response*, *implications*, *influence* **en el título**.
- **Usar la palabra "data"** tantas veces como sea posible a lo largo del artículo.
- No interpretar ni inferir nada a partir de los datos: solo describir.
- Deletrear todos los acrónimos.
- Los datos deben estar **públicamente disponibles en el repositorio ANTES del envío** (el editor/revisor debe poder acceder de forma anónima).

## 2. ¿Se puede escribir en LaTeX? — **NO**

La plantilla oficial dice textualmente: *"Note that we can only consider data articles submitted using this template"*. Es decir, **el envío debe hacerse en la plantilla Word oficial** (partes del documento están bloqueadas para edición; solo se editan los campos destacados en amarillo).

**Flujo de trabajo recomendado**: escribir y versionar el draft en Markdown (este repo), y al momento del envío volcar el contenido a la plantilla Word:

- Plantilla oficial: <https://legacyfileshare.elsevier.com/promis_misc/data-in-brief-article-template.docx> (copia local: `dib-template.docx` si se descarga)
- Guide for Authors: <https://www.sciencedirect.com/journal/data-in-brief/publish/guide-for-authors>
- Guía rápida del EiC (PDF): <https://researcheracademy.elsevier.com/uploads/2024-07/Quick_guide_Data_in_brief.pdf>
- Conversión práctica: `pandoc paper-draft.md -o paper-draft.docx` y luego copiar sección por sección dentro de la plantilla (no enviar el .docx generado por pandoc directamente).

## 3. Estructura obligatoria y límites de extensión

Secciones en este orden exacto (plantilla v.19):

| # | Sección | Límite / regla |
|---|---------|----------------|
| 1 | **Article title** | Debe incluir la palabra **"data"** o **"dataset"**. Único y centrado en los datos. |
| 2 | **Authors + Affiliations** | Nombre-apellido; marcar autor de correspondencia con *; dirección postal completa de cada institución. |
| 3 | **Corresponding author** | Email institucional (+ Twitter/X handle opcional). |
| 4 | **Keywords** | 4–8, separadas por punto y coma, **sin repetir palabras del título**. |
| 5 | **Abstract** | **100–500 palabras.** Describe proceso de recolección, el dataset y potencial de reúso. Sin conclusiones ni interpretaciones. |
| 6 | **Specifications Table** | Campos fijos: Subject (dropdown); Specific subject area (**máx. 150 caracteres sin espacios**); Type of data; Data collection (**máx. 600 caracteres sin espacios**); Data source location; Data accessibility (repositorio + DOI + URL directa); Related research article (si no hay, escribir "None"). |
| 7 | **Value of the Data** | **3–6 bullets** (la guía del EiC recomienda 3–5), máx. 150 palabras c/u. Responder: ¿por qué valiosos? ¿cómo los reutilizarán otros? Sin conclusiones. |
| 8 | **Background** | **Máx. 200 palabras.** Motivación y contexto teórico/metodológico. |
| 9 | **Data Description** | Sin límite. **Describir TODOS los archivos y carpetas del repositorio, uno por uno**, con tablas/figuras con caption. El lector debe poder navegar el dataset. |
| 10 | **Experimental Design, Materials and Methods** | Sin límite; lo más completa posible. Incluir software, versiones, códigos y criterios de inclusión/exclusión. |
| 11 | **Limitations** | **Máx. 200 palabras.** Problemas de recolección/curatoría, sesgos, tamaño. Si no hay: "None". |
| 12 | **Ethics Statement** | Declaración estándar si no hay sujetos humanos/animales/redes sociales (ver §4 texto de Jorge). |
| 13 | **CRediT author statement** | Contribución de cada autor con categorías CRediT. |
| 14 | **Acknowledgements** | Contribuidores no-autores + **financiamiento** (formato estándar de funder; si no hay: frase estándar de "no funding"). |
| 15 | **Declaration of Competing Interests** | Elegir una de las dos frases estándar. |
| 16 | **References** | **Máx. 20 referencias**, numeradas `[n]` en el texto. **Citar el propio dataset en el repositorio** (obligatorio). Si hay related research article, debe ser la primera cita. |

**Extensión total**: el journal no fija un tope global de palabras, pero el artículo de Jorge (publicado) tiene **≈2.900 palabras** en total incluyendo tablas y referencias — ese es nuestro objetivo de calibración (rango razonable: 2.500–4.000).

## 4. Cómo lo hizo Jorge (artículo de referencia)

**Cita verificada (Crossref):** J. Fábrega, "Ideological positions in the Chilean Chamber of Deputies (2002–2026): A legislative roll-call dataset", *Data in Brief* 63 (2025) 112163. <https://doi.org/10.1016/j.dib.2025.112163>. Open access **CC BY-NC 4.0**. Dataset en Harvard Dataverse: <https://doi.org/10.7910/DVN/FOXOIT>.

Desglose de su artículo (archivo `Fabrega-Ideological-Estimates-Chile.docx` en esta carpeta):

- **Abstract**: ~350 palabras. Qué contiene el dataset → métodos de estimación → metadatos → usos posibles → integrabilidad.
- **Specifications Table**: Subject = "Social Sciences"; accesibilidad = nombre de repositorio + DOI + URL directa; Related research article = "None".
- **Value of the Data**: 5 bullets (qué permite estudiar, dispersión intra/inter partido, comparabilidad internacional, uso para policymakers, base para estudios futuros).
- **Background**: ~230 palabras; contexto institucional + motivación teórica + contribución metodológica.
- **Data Description**: la sección más larga (~1.200 palabras). Patrón: describe cada **tipo** de archivo, con **Tabla 1** (archivos, filas y columnas por período), **Tablas 2–4** (diccionario de variables columna por columna) y **Figuras 1–2** (correlación entre métodos; distribución por período). Nosotros replicaremos este patrón: tabla de archivos por comisión + diccionario de variables + 1–2 figuras.
- **Methods**: ~330 palabras; fuente oficial → scraping (R, paquetes) → filtrado → 3 métodos de estimación → nota de reproducibilidad (nombra los scripts del repositorio).
- **Limitations**: ~200 palabras; 3 problemas concretos de curatoría y cómo se corrigieron manualmente.
- **Ethics**: frase estándar "does not involve human subjects, animal experiments, or any data collected from social media platforms".
- **CRediT**: categorías por autor ("This is a sole author article." en su caso).
- **Acknowledgements**: FONDECYT Regular 1231131 (ANID).
- **Referencias**: solo 4 (3 metodológicas + la cita del propio dataset).

## 5. Requisitos del repositorio de datos (Harvard Dataverse)

- Depositar **antes** del envío; el DOI y la URL deben funcionar al momento de la submission (acceso anónimo para revisores).
- Harvard Dataverse está en la lista de repositorios soportados por Elsevier.
- La cita del dataset va en las referencias del paper, con el formato Dataverse (autores, año, título, DOI, versión, UNF). Ejemplo de Jorge: *Fábrega, Jorge, 2025, "Ideological Estimates of the Chilean Chamber of Deputies, 2002–2026", https://doi.org/10.7910/DVN/FOXOIT, Harvard Dataverse, V2*.
- Decidir **licencia** del dataset: Dataverse usa CC0 por defecto (el dataset de roll-calls de Bunker et al. usa CC0); Jorge publicó el artículo CC BY-NC. Recomendación: CC0 o CC BY para maximizar reúso.
- Publicar también un **README/codebook** dentro del propio Dataverse (los revisores lo valoran; Bunker et al. incluyen un codebook PDF).

## 6. Costos

- **APC: USD 1.330** (sin impuestos), con *Geographical Pricing* según país de afiliación de los autores. Confirmar si UDD/ANID cubre el APC.

## 7. Referencias verificadas para usar en el paper

Todas verificadas vía Crossref/Dataverse el 2026-07-03. Formato final: numeradas `[n]`.

**Artículo hermano y datasets existentes (posicionamiento):**

1. J. Fábrega, "Ideological positions in the Chilean Chamber of Deputies (2002–2026): A legislative roll-call dataset", *Data in Brief* 63 (2025) 112163. https://doi.org/10.1016/j.dib.2025.112163
2. J. Fábrega, "Ideological Estimates of the Chilean Chamber of Deputies, 2002–2026", Harvard Dataverse, V2 (2025). https://doi.org/10.7910/DVN/FOXOIT
3. K. Bunker, P. Toro, S. Contreras, "Roll Call Data of the Constitutional Convention of Chile", Harvard Dataverse (2021–2023, V3, licencia CC0). https://doi.org/10.7910/DVN/JLTSRL — **dataset ya existente sobre la Convención: solo votaciones roll-call. Nuestro aporte se diferencia: genealogía textual artículo-por-artículo + autoría de iniciativas/indicaciones.**

**Sobre la Convención Constitucional chilena:**

4. H. Campos-Parra, P. Navia, "Ideological polarization in roll call votes in constitutional conventions: The case of Chile in 2021–2", *Parliamentary Affairs* 78(1) (2024) 203–225. https://doi.org/10.1093/pa/gsae009
5. J. Rozas-Bugueño, "Between Hope and Disaffection: The Chilean Constitution-Making Process and the Intermediation Crisis", *PS: Political Science & Politics* 57(2) (2024) 274–281. https://doi.org/10.1017/S1049096523001130
6. R. Tapia, "When Ideology Trumps Deliberation: Evidence from Chile's 2022 Constitutional Proposal", *PS: Political Science & Politics* 59(1) (2025) 102–106. https://doi.org/10.1017/S1049096525101601 *(verificar volumen/año en la versión final; Crossref reporta 2025)*

**Metodológicas (tracking de texto legislativo y puntos ideales):**

7. J. Wilkerson, D. Smith, N. Stramp, "Tracing the Flow of Policy Ideas in Legislatures: A Text Reuse Approach", *American Journal of Political Science* 59(4) (2015) 943–956. https://doi.org/10.1111/ajps.12175 — **cita clave: es el enfoque conceptual más cercano a nuestro tracking de texto.**
8. K.T. Poole, H. Rosenthal, *Congress: A Political-Economic History of Roll Call Voting*, Oxford University Press, New York, 1997. *(solo si mencionamos estimación ideológica en el companion analysis)*
9. K. Imai, J. Lo, J. Olmsted, "Fast estimation of ideal points with massive data", *American Political Science Review* 110(4) (2016) 631–656. https://doi.org/10.1017/S0003055416000385 *(ídem: emIRT)*

**Nuestra cita del dataset (placeholder hasta depositar):**

10. A. Olivera-Morales, V. [apellido de Vicente], [demás autores], "Article-level Genealogy of the Chilean Constitutional Convention Draft (2021–2022)", Harvard Dataverse, V1 (2026). https://doi.org/10.7910/DVN/XXXXXX

## 8. Lecturas recomendadas (no necesariamente citables en el paper)

- C. Heiss, "The new Chilean constituent process: exercising the 'muscle' of public participation in an adverse context", ConstitutionNet (2023) — panorama del mecanismo de participación (78 iniciativas populares llegaron a la Convención).
- "Constitution-Making in the 21st Century: Lessons from the Chilean Process", *PS: Political Science & Politics* (2024) — lecciones generales del proceso.
- S. Palestini, "The 'Withdrawn Citizen': Making Sense of the Failed Constitutional Process in Chile", *Bulletin of Latin American Research* (2025/2026). https://doi.org/10.1111/blar.70019 — argumenta que los mecanismos participativos tuvieron impacto limitado en las decisiones finales; útil para motivar por qué IMPORTA rastrear qué texto sobrevivió.
- "Parliamentary roll-call voting as a complex dynamical system: The case of Chile", *PLOS ONE* (2023). https://doi.org/10.1371/journal.pone.0281837
- Z. Elkins, T. Ginsburg, J. Melton, *The Endurance of National Constitutions*, Cambridge University Press, 2009 — y el Comparative Constitutions Project como estándar de datos constitucionales comparados.
- Sitios fuente: Convención Constitucional (<https://www.chileconvencion.cl>), plataforma de iniciativas (<https://iniciativas.chileconvencion.cl>), Biblioteca del Congreso Nacional (BCN).

## 9. Hechos verificados del proceso (para el Background)

- Elección de convencionales: 15–16 de mayo de 2021. Instalación: 4 de julio de 2021. Disolución: 4 de julio de 2022.
- 155 convencionales; paridad de género; 17 escaños reservados para pueblos originarios.
- Regla de 2/3 de los convencionales en ejercicio para aprobar normas en el pleno (~103 votos con 154 en ejercicio). **Verificar redacción exacta antes del envío.**
- 7 comisiones temáticas.
- Iniciativas populares de norma: **2.496 presentadas**, ~1 millón de participantes firmando; **77–78 alcanzaron las 15.000 firmas** (de al menos 4 regiones) antes del 1 de febrero de 2022. **Confirmar 77 vs 78 con fuente oficial.**
- Borrador aprobado por el pleno: 14 de mayo de 2022 (**499 artículos** según prensa; nuestro `coincidencias_comisiones.csv` registra 498 filas — conciliar antes del envío).
- Propuesta final entregada el 4 de julio de 2022: 388 artículos + 57 transitorias.
- Plebiscito de salida: 4 de septiembre de 2022; Rechazo ≈62%, Apruebo ≈38% (voto obligatorio).

## 10. Pendientes específicos de NUESTRO dataset antes del envío

- [ ] **Corregir encoding de `coincidencias_comisiones.csv`**: hoy NO es UTF-8 (extended-ASCII con terminadores NEL; "Artículo" aparece corrupto). Convertir a UTF-8 con LF y separador consistente (`;` → considerar `,` o documentar). Detectado el 2026-07-03.
- [ ] Conciliar 498 filas del CSV vs 499 artículos del borrador oficial (¿falta "Artículo 1"? la primera fila es "Artículo 2").
- [ ] Estandarizar nombres de archivos GENESIS (`C1_GENESIS_master_merged.json` vs `C2_GENESIS_master.json`) — idealmente un solo patrón.
- [ ] Escribir codebook/README en inglés para el depósito en Dataverse (variables de cada JSON, valores posibles de `final_status`, convención de `article_uid`).
- [ ] Depositar en Harvard Dataverse y obtener DOI (antes del envío a DiB).
- [ ] Decidir orden de autores y CRediT (Aníbal, Vicente, ¿Jorge?).
- [ ] Decidir licencia (recomendado CC0/CC BY).
- [ ] Confirmar financiamiento a declarar (¿ANID/beca doctoral?).
- [ ] Volcar `paper-draft.md` a la plantilla Word oficial y borrar textos de instrucción.
- [ ] "Related research article": por ahora **None** (el paper de SNA/TERGM/SAOM aún no existe; si se envía antes, citarlo como primera referencia).
