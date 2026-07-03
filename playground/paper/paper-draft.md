<!--
DRAFT v0.1 (2026-07-03) — Data in Brief data article.
Escrito en Markdown para versionar en git; al enviar, volcar a la plantilla Word
oficial (ver data-in-brief-guidelines.md §2). Los [PLACEHOLDERS] marcan decisiones
pendientes del equipo. Cifras congeladas al commit fb78ef0 (merge a main, 2026-07-03).
-->

# ARTICLE INFORMATION

## Article title

From initiative to constitutional draft: an article-level genealogy dataset of Chile's Constitutional Convention (2021–2022)

## Authors

Aníbal Olivera Morales\*, Vicente [APELLIDO — completar], [¿Jorge Fábrega? — decidir orden de autores]

## Affiliations

[COMPLETAR: afiliación institucional completa con dirección postal de cada autor]

## Corresponding author's email address and Twitter handle

anibal.olivera.m@gmail.com [reemplazar por email institucional — requisito del journal]

## Keywords

Constitution-making; norm tracking; text reuse; co-authorship networks; amendments; political elites; ideal points; Latin American politics

## Abstract

This dataset provides an article-level genealogy of the constitutional draft produced by Chile's Constitutional Convention (2021–2022), the elected body created after the 2019 social uprising to write a new constitution, whose proposal was ultimately rejected in the September 2022 referendum. The data trace each of the 498 articles of the draft approved by the plenary on 14 May 2022 back through the full lineage that produced it: the original norm proposals (1,892 "genesis" texts consolidated from constituent initiatives), the amendments (*indicaciones*) debated and voted in each of the seven thematic commissions, and the intermediate text versions, down to the final drafted article.

The core of the dataset is a set of tracking files, one per commission, containing 2,047 lineage records. Each record includes the article text, its unique identifier, its co-authors (harmonized against the official roster of 154 convention members), the initiative(s) it originated from, a history of amendment snapshots with dates, and a terminal status field that classifies its fate: eliminated in commission (1,191 records), rejected in the plenary (350), or surviving into the draft as an identical (293) or similar (185) version of a final article. A master crosswalk table links every final-draft article to its source lineage(s) with a three-level traceability status (identical, similar, not yet traced). The dataset also includes the pool of 996 constituent initiatives with their signatories, member-level biographical data web-scraped from the Chilean Library of Congress (147 profiles with gender, age, profession, district, and political affiliation), and dynamic ideal-point estimates for the 154 members computed from plenary roll-call votes.

The data were extracted from official Convention documents (PDF committee reports, systematized genesis texts, and the published draft) through Python pipelines combining large-language-model-assisted parsing with extensive human-in-the-loop reconstruction and one-by-one manual validation. The dataset supports research on constitution-making, legislative behavior, co-authorship and collaboration networks, textual survival and legislative success, and the interplay between ideology and drafting in elected constituent bodies.

# SPECIFICATIONS TABLE

| Field | Value |
|---|---|
| **Subject** | Social Sciences |
| **Specific subject area** | Article-level tracking of constitutional norm proposals, amendments, authorship, and textual survival in Chile's Constitutional Convention (2021–2022) |
| **Type of data** | Processed, Raw, Tables (JSON, CSV, Markdown) |
| **Data collection** | Structured extraction from official public records of the Constitutional Convention (systematized "genesis" texts, amendment and voting reports of the seven thematic commissions, and the 14 May 2022 consolidated draft) using Python pipelines with LLM-assisted parsing (Google Gemini API) under commission-specific extraction profiles, followed by human-in-the-loop reconstruction and one-by-one manual validation of every article lineage. Author names were harmonized against the official member roster. Member biographies were web-scraped from the Library of the National Congress of Chile (BCN). Dynamic ideal points were estimated in R with the emIRT package. |
| **Data source location** | Primary sources: Convención Constitucional de Chile (https://www.chileconvencion.cl), Santiago, Chile; Biblioteca del Congreso Nacional de Chile (https://www.bcn.cl), Valparaíso, Chile. Data compiled at: [AFILIACIÓN — completar], Chile. |
| **Data accessibility** | Repository name: Harvard Dataverse. Data identification number: [DOI PENDIENTE — depositar antes del envío, p.ej. https://doi.org/10.7910/DVN/XXXXXX]. Direct URL to data: [URL Dataverse]. Instructions for accessing these data: openly accessible, no registration required. Processing and validation code: https://github.com/aoliveram/constitutional-proposal-tracking |
| **Related research article** | None |

# VALUE OF THE DATA

- These data provide the first article-level genealogy of a complete constitutional draft: every article of the text approved by the plenary of Chile's Constitutional Convention on 14 May 2022 is linked back to the initiatives, authors, amendments, and votes that produced it, allowing researchers to measure whose proposed text survived into the draft and in what form.
- The data complement the existing public record of the Convention, which so far consists mainly of roll-call votes [3,4], by adding the textual and authorship dimensions of the drafting process; combining both sources enables joint analyses of ideology, collaboration, and drafting success within a single elected constituent body.
- Co-authorship lists attached to initiatives and amendments, together with harmonized member identifiers, allow the construction of dynamic collaboration networks among the 154 convention members, supporting social network analyses of cooperation, influence, and legislative success (e.g., temporal exponential random graph models or stochastic actor-oriented models) in a constituent assembly elected with gender parity, reserved indigenous seats, and a majority of non-party members.
- The lineage records preserve intermediate text versions and amendment snapshots, so the data can be used to develop and validate text-reuse and text-similarity methods for legislative corpora in Spanish [7], as well as to audit LLM-assisted extraction pipelines against fully human-validated ground truth.
- Member-level biographical attributes (gender, age, profession, education, district, political affiliation) and dynamic ideal-point estimates [8,9] make the data directly usable for research on representation and deliberation in constitution-making processes, a topic of active comparative debate [5,6].

# BACKGROUND

After the October 2019 social uprising, Chilean political parties agreed to open a constituent process, and in May 2021 voters elected a 155-member Constitutional Convention with gender parity, 17 seats reserved for indigenous peoples, and a large share of independents. The Convention worked between 4 July 2021 and 4 July 2022; its proposal was rejected in the mandatory referendum of 4 September 2022 (approximately 62% against) [5,6].

Quantitative research on the Convention has relied mostly on plenary roll-call votes [3,4], which capture how members voted but not what happened to the text they proposed. Norm proposals entered through constituent initiatives, were consolidated into "genesis" texts within seven thematic commissions, were amended through *indicaciones*, and reached the plenary, where they required a two-thirds supermajority to enter the draft. Reconstructing that textual pipeline requires linking hundreds of heterogeneous PDF reports scattered across commissions.

This dataset was compiled to make that pipeline tractable: it was motivated by a research program on cooperation networks and legislative success among convention members, and it follows the data-release model of a companion dataset on ideological positions in the Chilean Chamber of Deputies [1,2].

# DATA DESCRIPTION

The repository is organized in seven commission folders (`comision-1` to `comision-7`), each containing a `dataverse-final/` directory with four JSON files, plus repository-level files that link commissions together and describe the members. All JSON files are UTF-8 arrays of records; all text is in Spanish as published in the official documents. Table 1 lists the seven thematic commissions and the number of records per file type; the naming pattern of the four files in each commission folder is described below the table.

**Table 1. Record counts per commission and file type in `comision-{X}/dataverse-final/`**

| Commission (official name, abbreviated) | `TRACK_full` | `TRACK_articles` | `GENESIS_master` | `BORRADOR_final` |
|---|---|---|---|---|
| C1 — Political System, Government, Legislative Power and Electoral System | 230 | 131 | 96 | 100 |
| C2 — Constitutional Principles, Democracy, Nationality and Citizenship | 182 | 24 | 312 | 41 |
| C3 — Form of the State, Territorial Organization and Decentralization | 234 | 72 | 222 | 96 |
| C4 — Fundamental Rights | 175 | 58 | 167 | 58 |
| C5 — Environment, Rights of Nature, Natural Commons and Economic Model | 484 | 36 | 464 | 43 |
| C6 — Justice Systems, Autonomous Control Organs and Constitutional Reform | 491 | 117 | 440 | 119 |
| C7 — Knowledge Systems, Cultures, Science, Technology, Arts and Heritage | 251 | 40 | 191 | 41 |
| **Total** | **2,047** | **478** | **1,892** | **498** |

**`C{X}_TRACK_full.json`** is the core genealogical file of each commission: one record per tracked text lineage, including lineages that died along the way. Table 2 describes its fields. Records carry a unique identifier (`article_uid`) with the scheme `C{X}_GEN[…]_ART{N}` for genesis-derived articles (optionally with a chapter component `CH##`) and `C{X}_IND[…]_ART{N}` for amendment records. The `sources` field lists the identifiers of the constituent initiative(s) the text came from (e.g., `"672-2"`), which link to the initiative pool described below. The `history` field stores a list of amendment snapshots, each with its own timestamp, amendment action, content, and authors, so the successive wording of an article can be reconstructed step by step.

**Table 2. Main fields of `C{X}_TRACK_full.json` and `C{X}_TRACK_articles.json`** (presence out of 2,047 TRACK_full records)

| Field | Type | Description | Presence |
|---|---|---|---|
| `article_uid` | string | Unique lineage identifier (see naming scheme above) | 2,019 |
| `article` | string | Article label as printed in the source report (e.g., "Artículo 14") | 1,848 |
| `text` | string | Full article text (Spanish) | 2,008 |
| `authors` | list of strings | Co-authors, harmonized to "Surname, Name" against the official roster | 1,773 |
| `sources` | list of strings | Originating initiative ID(s), format `<number>-<version>` | 1,638 |
| `timestamp` | string | Date label of the session/report the record comes from (MM-DD) | 2,026 |
| `history` | list of dicts | Amendment snapshots: timestamp, action (ADD/SUBSTITUTE/DELETE), target scope, content, content removed, placement instructions, authors | 1,620 |
| `final_status` | string | Terminal fate of the lineage (see Table 3) | 2,020 |
| `icc_id`, `voting_result` | string/list | Committee vote identifier and outcome text, where recorded | 167 |
| `number`, `target_scope`, `action`, `content`, `content_to_remove`, `placement_instructions`, `step` | mixed | Amendment-specific fields (subset of ~224 amendment records) | 125–226 |

**`C{X}_TRACK_articles.json`** is the survivor subset of `TRACK_full`: the 478 lineages whose text reached the 14 May 2022 draft. `article_uid` and `final_status` are present in 100% of these records, and `final_status` only takes pointer values ("Idéntico a …" / "Similar a …") that name the final-draft article the lineage became.

**Table 3. `final_status` categories in `TRACK_full` (2,020 records with the field)**

| Value | Meaning | Count |
|---|---|---|
| `Eliminado` | Text eliminated during the commission stage | 1,191 |
| `ART-FALLIDO` | Article submitted to the plenary but failed to reach the two-thirds supermajority | 350 |
| `Idéntico a <N>.- Artículo <M>` | Survived; textually identical to final-draft article N | 293 |
| `Similar a <N>.- Artículo <M>` | Survived; similar (non-identical wording) to final-draft article N | 185 |

**`C{X}_GENESIS_master(_merged).json`** contains the pool of "genesis" texts of each commission: the consolidated base proposals (from the systematized texts, *textos sistematizados*) before amendments. Each record carries `text` (100% of 1,892 records), and most carry `article`, `sources`, and `authors`. **`C{X}_BORRADOR_final.json`** contains the plain final-draft articles attributed to each commission, with exactly two fields (`article`, `text`); the seven files sum to the 498 articles of the draft. The seven `C{X}_BORRADOR-CONSTITUCIONAL-14-05-22.md` files provide the same draft as published ("Consolidado de normas aprobadas para la propuesta constitucional por el Pleno"), partitioned by originating commission, in Markdown.

**`coincidencias_comisiones.csv`** (498 rows; also provided as `.xlsx`) is the master crosswalk: one row per final-draft article, in draft order, linking it to its source lineage(s). Table 4 describes its columns. 37 final articles merge text from more than one source lineage (up to three), which is why `TRACK_articles` holds 478 lineages for 498 final articles while some articles remain unmatched.

**Table 4. Columns of `coincidencias_comisiones.csv`**

| Column(s) | Description | Categorical values (count) |
|---|---|---|
| `final_draft_order`, `final_article_label` | Position and label of the article in the 14 May 2022 draft | — |
| `source_commission` | Commission of origin | C6 (119), C1 (100), C3 (96), C4 (58), C5 (43), C2 (41), C7 (41) |
| `n_sources_link`, `has_multiple_sources` | Number of source lineages feeding the article | 1 (461), 2 (36), 3 (1) |
| `traceability_status_primary` | Match quality of the primary source | `identical` (298), `similar` (146), `not_traced` (54) |
| `source_article_uid_primary` | `article_uid` of the primary source lineage | — |
| `match_notes_primary` | Free-text notes explaining non-identical matches | — |
| `…_secondary`, `…_tertiary` (uid, status, notes) | Same fields for additional sources, where they exist | secondary: `similar` (35), `identical` (2) |

**Member-level and initiative-level files.** `convention_members.json` is the canonical roster of the 154 convention members ("Surname, Name") used for author harmonization. `conventionals-bcn-webscrapping/conventional-profiles.json` provides 147 biographical profiles scraped from the Library of the National Congress (BCN), with eight variables per member: harmonized name, gender indicator, grouped political affiliation, district, lawyer indicator, age at installation, education level, and prior institutional experience (a raw-text version, `conventional-profiles-raw.json`, preserves the full biographies). `submitted_initiatives/` contains the pool of 996 constituent initiatives (*iniciativas convencionales constituyentes*) as extracted from the official platform, keyed by the original PDF file name, with the proposed norm text, author, matched author, thematic commission (869 initiatives carry a commission assignment), date, and the full list of signatories with match diagnostics. `emIRT-analysis/emIRT_summary_positions.csv` provides dynamic ideal-point estimates for the 154 members (mean, standard deviation, minimum, maximum, range, and left-to-right ranking), with the underlying R scripts and model objects included in the same folder. `unique_status_values.txt` documents the 124 raw status strings found before normalization, as a curation audit trail, and `reports/` contains the data-quality and reconstruction reports produced during curation.

**Figure 1. Fate of tracked text lineages by commission (to be generated).** Stacked bar or Sankey diagram from `TRACK_full`: for each commission, the share of lineages ending as `Eliminado`, `ART-FALLIDO`, `Idéntico a…`, and `Similar a…`.

**Figure 2. Traceability of the 498 final-draft articles (to be generated).** Per-commission counts of `identical`, `similar`, and `not_traced` primary matches from `coincidencias_comisiones.csv`.

# EXPERIMENTAL DESIGN, MATERIALS AND METHODS

**Sources.** All inputs are official public records: (i) the systematized genesis texts (*textos sistematizados*) and amendment (*indicaciones*) and voting reports issued by each of the seven thematic commissions of the Convention; (ii) the consolidated draft approved by the plenary on 14 May 2022 (*Consolidado de normas aprobadas para la propuesta constitucional por el Pleno*); (iii) the constituent initiatives published on the Convention's platform (https://www.chileconvencion.cl); and (iv) the biographical pages of convention members published by the Library of the National Congress of Chile (BCN).

**Extraction pipeline.** Documents were downloaded as PDFs, filtered to the relevant pages, and processed with a Python pipeline (repository: https://github.com/aoliveram/constitutional-proposal-tracking). Because commissions published reports in heterogeneous formats, extraction was configured through per-commission profiles: narrative documents parsed by language patterns, two-column tabular documents parsed by table structure, and ad-hoc logic for irregular formats. Text segmentation, article identification, and amendment parsing were assisted by a large language model (Google Gemini API) called from the numbered scripts (`01_…` to `06_…`), including a semantic matcher that proposes genesis-to-final-draft candidate matches.

**Human-in-the-loop reconstruction and validation.** All machine-extracted lineages were manually reconstructed and validated: amendment sequences were re-applied step by step to verify each intermediate text; every `final_status` value was checked one by one against the published draft; author lists were completed by hand where reports omitted them and harmonized to "Surname, Name" against the canonical roster of 154 members; identifier uniqueness was verified across all commissions (single `article_uid` per lineage, underscore-only format); and each final-draft article was classified as `identical`, `similar` (with explanatory notes), or `not_traced` in the master crosswalk. The audit trail of this process (raw status vocabulary, missing-author reports, validation reports) is released with the data.

**Ideal-point estimation.** Dynamic ideal points were estimated from plenary roll-call votes (sessions 1–109, coded yes = 1, no = −1, missing = 0) with the dynamic item-response model of Martin and Quinn [9] as implemented in the `dynIRT()` function of the R package emIRT [8], using variational EM, identification anchors on one right-wing and one left-wing member, temporal smoothing ω² = 0.025, and parametric-bootstrap standard errors (50 trials). The 154 members who served through the drafting stage are included. Raw plenary roll-call matrices are publicly available from the Convention's records and in an existing Harvard Dataverse deposit [3]; the present dataset ships the estimation scripts, model objects, and the summary positions table.

**Processing environment.** Python 3 (pdfplumber/PyPDF-based extraction, pandas) and R (v4.x; emIRT) [COMPLETAR versiones exactas y paquetes al congelar el release]. All processing code, including the commission-specific profiles and the validation scripts, is available in the GitHub repository and archived with the data deposit.

# LIMITATIONS

The seven commissions published their reports in heterogeneous and sometimes irregular formats; despite commission-specific pipelines and manual reconstruction, coverage is not perfectly uniform across commissions. In the master crosswalk, 54 of the 498 final-draft articles (10.8%) remain `not_traced` to a source lineage in the current version. Some tracking records lack author lists (a missing-authors report is included), and 127 of the 996 constituent initiatives lack a thematic commission assignment. The `final_status` field is semi-structured: survivor categories embed the final article label as free text. LLM-assisted extraction may introduce residual transcription errors, although every lineage endpoint was manually validated. The genealogy targets the plenary draft of 14 May 2022; the subsequent work of the Harmonization Commission that produced the 388-article final proposal of 4 July 2022 is not yet covered. Raw plenary roll-call matrices are not redistributed here (they are available from official records and an existing deposit [3]).

# ETHICS STATEMENT

The authors have read and follow the ethical requirements for publication in Data in Brief and confirm that the current work does not involve human subjects, animal experiments, or any data collected from social media platforms. All data derive from official public institutional records of the Constitutional Convention and the Library of the National Congress of Chile concerning elected public officials acting in their public capacity.

# CRediT AUTHOR STATEMENT

[COMPLETAR según orden de autores definitivo. Propuesta:]
**Aníbal Olivera Morales:** Conceptualization, Methodology, Software, Data curation, Validation, Writing – original draft, Supervision. **Vicente [APELLIDO]:** Data curation, Validation, Software, Writing – review & editing. **[¿Jorge Fábrega?]:** [Conceptualization, Writing – review & editing, Supervision].

# ACKNOWLEDGEMENTS

[COMPLETAR: financiamiento (¿ANID beca de doctorado / FONDECYT?). Si no hay:]
This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

# DECLARATION OF COMPETING INTERESTS

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

# REFERENCES

[1] J. Fábrega, Ideological positions in the Chilean Chamber of Deputies (2002–2026): A legislative roll-call dataset, Data in Brief 63 (2025) 112163. https://doi.org/10.1016/j.dib.2025.112163

[2] J. Fábrega, Ideological Estimates of the Chilean Chamber of Deputies, 2002–2026, Harvard Dataverse, V2, 2025. https://doi.org/10.7910/DVN/FOXOIT

[3] K. Bunker, P. Toro, S. Contreras, Roll Call Data of the Constitutional Convention of Chile, Harvard Dataverse, V3, 2023. https://doi.org/10.7910/DVN/JLTSRL

[4] H. Campos-Parra, P. Navia, Ideological polarization in roll call votes in constitutional conventions: The case of Chile in 2021–2, Parliamentary Affairs 78 (1) (2024) 203–225. https://doi.org/10.1093/pa/gsae009

[5] J. Rozas-Bugueño, Between hope and disaffection: The Chilean constitution-making process and the intermediation crisis, PS: Political Science & Politics 57 (2) (2024) 274–281. https://doi.org/10.1017/S1049096523001130

[6] R. Tapia, When ideology trumps deliberation: Evidence from Chile's 2022 constitutional proposal, PS: Political Science & Politics 59 (1) (2025) 102–106. https://doi.org/10.1017/S1049096525101601

[7] J. Wilkerson, D. Smith, N. Stramp, Tracing the flow of policy ideas in legislatures: A text reuse approach, American Journal of Political Science 59 (4) (2015) 943–956. https://doi.org/10.1111/ajps.12175

[8] K. Imai, J. Lo, J. Olmsted, Fast estimation of ideal points with massive data, American Political Science Review 110 (4) (2016) 631–656. https://doi.org/10.1017/S0003055416000385

[9] A.D. Martin, K.M. Quinn, Dynamic ideal point estimation via Markov chain Monte Carlo for the U.S. Supreme Court, 1953–1999, Political Analysis 10 (2) (2002) 134–153. https://doi.org/10.1093/pan/10.2.134

[10] A. Olivera Morales, V. [APELLIDO], et al., From initiative to constitutional draft: article-level genealogy data of Chile's Constitutional Convention (2021–2022), Harvard Dataverse, V1, 2026. [DOI PENDIENTE — citar el depósito propio, obligatorio]
