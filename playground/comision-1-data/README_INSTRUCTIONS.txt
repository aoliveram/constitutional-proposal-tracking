Data Analysis Instructions - Commission 1 (Political System)
============================================================

FOLDER CONTENTS:
- data/: Subfolder containing all the raw JSON files (both Genesis texts and parsed Indications) as well as flattened CSV versions.
- 01_exploratory_example.R: The master R script. This script provides an end-to-end example of how to load the fully enriched manual data, perform exploratory aggregate analysis (number of articles, counting and plotting the distribution of modifications), and execute a deep-dive case study tracking the exact history of a single article.

NOTE ON THE DATA:
The core file (`data/C1_texto-sistematizado_enriched_manual.json`) contains the most complete timeline mapped by the "human in the loop" methodology, linking original texts, authors, and subsequent indications into a single structured format.
