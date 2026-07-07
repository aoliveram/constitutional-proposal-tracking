# Dataverse README / Codebook Draft

Working draft for the Harvard Dataverse deposit of the article-level genealogy dataset of Chile's Constitutional Convention. This note documents conventions shared by:

- `comision-{1..7}/dataverse-final/C{X}_TRACK_full.json`
- `comision-{1..7}/dataverse-final/C{X}_TRACK_articles.json`

All files covered here are UTF-8 JSON arrays. Textual content is in Spanish, following the source documents.

## Files Covered

`C{X}_TRACK_full.json` contains article-lineage records reconstructed for commission `C{X}`. It includes lineages that survived into the 14 May 2022 constitutional draft and lineages that did not survive because they were eliminated or failed during the drafting process.

`C{X}_TRACK_articles.json` contains the subset of article-lineage records from the same commission whose `final_status` points to an article in the 14 May 2022 constitutional draft. In these files, `final_status` takes only survivor values beginning with `Idéntico a` or `Similar a`.

## `article_uid`

`article_uid` is a stable string identifier for a reconstructed article-level lineage. It is designed for traceability across files, not as a fully standardized analytical classification. Analysts should use the exact string for joins and should derive analytical variables from explicit fields or validated parsing rules, not from ad hoc assumptions about the identifier alone.

General form:

```text
C{commission}_{origin_token}_{optional_document_locator}_{article_token}
```

The identifier uses underscores as its main separator. Some article tokens preserve punctuation, suffixes, ranges, or non-ASCII characters when those marks reflect the source document.

### Components

| Component | Meaning | Examples |
|---|---|---|
| `C{commission}` | The thematic commission that produced or processed the record. | `C1`, `C2`, ..., `C7` |
| `origin_token` | The documentary source of the record. | `GEN`, `GEN1`, `GEN2`, `GEN3`, `IND04_01_2`, `IND05_08`, `X` |
| `optional_document_locator` | Chapter, title, or special section marker when the source document provided one. This component is omitted when the source did not provide a stable chapter/title structure. | `CH01`, `CH1`, `CH*`, `CHTX_TIT1`, `DT` |
| `article_token` | Article label preserved from the source or from the reconstruction process. | `ART01`, `ART1A`, `ART43BIS`, `ART20TER`, `ARTN`, `ARTN90`, `ART72_73`, `ARTX`, `ARTXX` |

### Origin Tokens

`GEN`, `GEN1`, `GEN2`, and `GEN3` identify records derived from Genesis/base texts. Numeric suffixes distinguish source batches, merged versions, or document-specific reconstruction stages. They should not be interpreted as a harmonized chronological scale across commissions without checking the source file.

`IND{MM}_{DD}` and `IND{MM}_{DD}_{block}` identify records derived from amendment or voting reports (`indicaciones`). The date-like segment records the report/session label used during reconstruction. If a precise date is required, use the record's `timestamp` and the original source document rather than parsing `article_uid` alone.

`X` marks records retained through manual reconstruction where the source does not fit the standard `GEN` or `IND` pattern, or where provenance could not be encoded with the regular tokens. These records should be kept in the dataset but treated as special cases in downstream parsing.

### Article Tokens and Irregular Labels

The `ART` component preserves the source article label as closely as practical. This includes:

- alphabetic suffixes: `ART1A`, `ART40B`
- constitutional suffixes: `ART55BIS`, `ART43BIS`, `ART20TER`, `ART52QUATER`
- decimal or split labels: `ART01.1`, `ART1.9`
- ranges or merged references: `ART72_73`, `ART28_29`
- new-article labels: `ARTN` for records labeled as "Artículo Nuevo", and `ARTN{number}` when the new-article label was associated with a specific article number in the source or reconstruction
- unresolved placeholders: `ARTX`, `ARTXX`, `ARTXXX2`
- non-ASCII labels when present in the source: for example `C2_GEN_ART9Ñ`

Case and accents are part of the raw identifier. For joins, preserve the exact value. For analysis, create a separate normalized variable if case-folding or ASCII conversion is needed.

### Examples

| Example | Interpretation |
|---|---|
| `C1_GEN_CH01_ART01` | Commission 1, Genesis-derived record, chapter 1, article 1. |
| `C2_GEN_ART9Ñ` | Commission 2, Genesis-derived record, article label 9Ñ; the source label contains `Ñ`. |
| `C3_GEN2_CH01_ART43BIS` | Commission 3, Genesis batch/version 2, chapter 1, article 43 bis. |
| `C4_IND03_24_ARTN` | Commission 4, indication/voting record dated/labeled 03-24, new article. |
| `C5_GEN2_CH1_ART236` | Commission 5, Genesis batch/version 2, chapter 1, article 236. |
| `C6_X_ART3` | Commission 6, special/manual provenance marker, article 3. |
| `C7_GEN_CH01_ART01.1` | Commission 7, Genesis-derived record, chapter 1, article 1.1. |

## `timestamp`

`timestamp` records the session/report label under which a record (or an amendment snapshot inside `history[]`) was extracted. It is a documentary label taken from the source report, not a full calendar date.

### Format

| Pattern | Meaning | Count (top-level, all `TRACK_full`) |
|---|---|---|
| `MM-DD` | Month and day of the source report/session. The year is implicit: all observed values fall between January and May, within the 2022 commission reporting period. | 1,634 |
| `MM-DD-{block}` | Same as `MM-DD`, plus a block ordinal distinguishing multiple reports or voting blocks issued on the same day (e.g., `04-01-2` is the second block of 1 April 2022). This `{block}` component is the same one used by the `IND{MM}_{DD}_{block}` origin token of `article_uid`. | 319 |
| `NA` | The source report did not provide a usable session date label. All 55 such records belong to C6 (17) and C7 (38). | 55 |

The same convention applies to `timestamp` values inside `history[]` snapshots (observed months: February–May, implicit year 2022).

### Cautions

- Treat `timestamp` as an ordinal session label within 2022, not as an exact legal date. For precise dating, consult the source PDF report.
- Do not parse the `-{block}` suffix as a day or month component.
- For chronological sorting, parse as (month, day, block) with block defaulting to 0; `NA` values cannot be ordered and should be handled explicitly.
- In C2, nested `history[].step` labels name reconstruction stages of that commission's custom pipeline (e.g., `Genesis (02-16)`, `Report 1 (03-02)`, `Consolidation 04-08`); the date inside the label follows the same `MM-DD` convention. In all other commissions, `step` takes the value `Indicacion` (stored without accent by convention).

## `final_status`

`final_status` is a curatorial endpoint field. It summarizes how a reconstructed article-lineage record relates to the constitutional draft approved by the Convention plenary on 14 May 2022, after considering both the article text and the reconstructed amendment history.

`final_status` is stored as a string in the top-level article record. It is not a nested `history` field. The raw value should be preserved because survivor statuses embed a pointer to the final-draft article.

### Literal Values and Meaning

| Raw pattern | Recommended derived class | Meaning |
|---|---|---|
| `Idéntico a <N>.- <final_article_label>` | `identical_to_final_article` | The lineage survives into the 14 May 2022 draft as a textually identical final-draft article. `<N>` is the order of the final-draft article in the crosswalk, and `<final_article_label>` is the article label printed or retained in the final draft. |
| `Similar a <N>.- <final_article_label>` | `similar_to_final_article` | The lineage survives into the 14 May 2022 draft, but the final wording is not identical. The record should be linked to the crosswalk and, when needed, to match notes explaining the textual difference. |
| `Eliminado` | `eliminated_before_final_draft` | The lineage did not survive into the 14 May 2022 draft. It was removed during the reconstructed drafting trajectory. This does not imply that no related topic survived elsewhere. |
| `ART-FALLIDO` | `failed_article` | The record represents an article proposal that failed as an article in the reconstruction process. This is a procedural endpoint, not a qualitative evaluation of the content. |

Recommended parser for survivor values:

```text
^(Idéntico|Similar) a ([0-9]+)\.- (.+)$
```

The parser returns:

- survival type: `Idéntico` or `Similar`
- final-draft order: numeric value after `a`
- final-draft article label: the string after `.-` (usually `Artículo ...`, but some source labels may be shorter)

Do not apply this parser to `Eliminado` or `ART-FALLIDO`, since those values do not point to a final-draft article.

## Relation Between `final_status`, `history`, and the Crosswalk

`history` stores the intermediate amendment snapshots used to reconstruct the trajectory of a lineage. `final_status` summarizes the endpoint of that trajectory.

`coincidencias_comisiones.csv` is a separate final-draft-to-source crosswalk. Its `traceability_status_*` fields classify the quality of the link from a final-draft article back to one or more source lineages (`identical`, `similar`, or `not_traced`). This is related to, but not identical with, `final_status`:

- `final_status` is attached to a source lineage and asks: what happened to this lineage?
- `traceability_status_*` is attached to a final-draft article and asks: how was this final article linked back to its source lineage(s)?

For survivor records, the two should be substantively consistent. For analysis, however, they should remain distinct variables because they answer opposite linking questions.

## Methodological Cautions

- Treat `article_uid` as an identifier first. Its components are useful for traceability, but the source documents were heterogeneous across commissions.
- Do not infer institutional meaning from missing locator components. Absence of `CH` or `TIT` usually reflects the structure of the source document, not absence of a chapter or title in a legal sense.
- Do not collapse `Eliminado` and `ART-FALLIDO` unless the research question explicitly only requires a binary survived/not-survived outcome.
- `Similar a ...` is a curated survival link with non-identical wording. It should not be treated as weaker evidence of survival without reading the match notes or comparing texts.
- `ART-FALLIDO` is a procedural data category. It should not be described as political failure unless the voting or procedural evidence supports that interpretation.
- Any release that changes `article_uid` values must update all downstream references, including `history.article_uid` if present, `coincidencias_comisiones.csv`, and any scripts or derived tables that join on these identifiers.
