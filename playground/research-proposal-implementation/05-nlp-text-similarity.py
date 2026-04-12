"""
05-nlp-text-similarity.py
Compute lexical retention rates via text similarity.

Primary: TF-IDF cosine similarity
Robustness: Sentence-BERT embeddings (multilingual)

Validation: articles labeled "identical" should score near 1.0
Attribution: aggregate per-convencional success scores.
"""

import json
import os
import csv
import re
import unicodedata
from collections import defaultdict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

base_dir = "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking"
data_dir = os.path.join(base_dir, "playground/research-proposal-implementation/data")


def normalize_text(text):
    """Normalize Spanish text for comparison: lowercase, remove punctuation, collapse whitespace."""
    text = text.lower()
    # Normalize unicode (keep accented characters for Spanish)
    text = unicodedata.normalize("NFC", text)
    # Remove article numbering patterns like "Artículo 1.", "Artículo x1.-"
    text = re.sub(r"art[ií]culo\s+[\dx]+[\w]*\.?\s*-?\s*", "", text)
    # Remove ordinal markers
    text = re.sub(r"°", "", text)
    # Remove punctuation except hyphens within words
    text = re.sub(r"[^\w\sáéíóúüñ-]", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


# =============================================================================
# 1. Load article mapping
# =============================================================================

print("--- Step 1: Loading article mapping ---")
with open(os.path.join(data_dir, "article_mapping_unified.json"), "r", encoding="utf-8") as f:
    mapping = json.load(f)
print(f"  Articles to compare: {len(mapping)}")

# Extract texts
genesis_texts = []
final_texts = []
for entry in mapping:
    genesis_texts.append(normalize_text(entry["genesis_text"]))
    final_texts.append(normalize_text(entry["final_text"]))

# =============================================================================
# 2. TF-IDF Cosine Similarity
# =============================================================================

print("\n--- Step 2: TF-IDF Cosine Similarity ---")

# Fit TF-IDF on all texts together (shared vocabulary)
all_texts = genesis_texts + final_texts
vectorizer = TfidfVectorizer(
    analyzer="word",
    ngram_range=(1, 2),       # unigrams + bigrams
    sublinear_tf=True,
    max_features=20000,
    min_df=2,
)
tfidf_matrix = vectorizer.fit_transform(all_texts)

n = len(mapping)
genesis_tfidf = tfidf_matrix[:n]
final_tfidf = tfidf_matrix[n:]

# Compute pairwise cosine similarity (each genesis vs its matched final)
tfidf_scores = []
for i in range(n):
    sim = cosine_similarity(genesis_tfidf[i], final_tfidf[i])[0, 0]
    tfidf_scores.append(sim)

tfidf_scores = np.array(tfidf_scores)

# Validation: check identical articles
identical_mask = np.array([e["format_label"] == "identical" for e in mapping])
similar_mask = np.array([e["format_label"] == "similar" for e in mapping])

print(f"  TF-IDF scores (all):       mean={tfidf_scores.mean():.3f}, "
      f"median={np.median(tfidf_scores):.3f}, "
      f"min={tfidf_scores.min():.3f}, max={tfidf_scores.max():.3f}")
print(f"  TF-IDF scores (identical): mean={tfidf_scores[identical_mask].mean():.3f}, "
      f"median={np.median(tfidf_scores[identical_mask]):.3f}")
print(f"  TF-IDF scores (similar):   mean={tfidf_scores[similar_mask].mean():.3f}, "
      f"median={np.median(tfidf_scores[similar_mask]):.3f}")

# =============================================================================
# 3. Sentence-BERT Embeddings (robustness)
# =============================================================================

print("\n--- Step 3: Sentence-BERT Embeddings ---")

try:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    # Encode all texts
    print("  Encoding genesis texts...")
    genesis_emb = model.encode(genesis_texts, show_progress_bar=False, batch_size=32)
    print("  Encoding final texts...")
    final_emb = model.encode(final_texts, show_progress_bar=False, batch_size=32)

    # Compute cosine similarity
    embedding_scores = []
    for i in range(n):
        g = genesis_emb[i].reshape(1, -1)
        f = final_emb[i].reshape(1, -1)
        sim = cosine_similarity(g, f)[0, 0]
        embedding_scores.append(sim)

    embedding_scores = np.array(embedding_scores)

    print(f"  Embedding scores (all):       mean={embedding_scores.mean():.3f}, "
          f"median={np.median(embedding_scores):.3f}")
    print(f"  Embedding scores (identical): mean={embedding_scores[identical_mask].mean():.3f}, "
          f"median={np.median(embedding_scores[identical_mask]):.3f}")
    print(f"  Embedding scores (similar):   mean={embedding_scores[similar_mask].mean():.3f}, "
          f"median={np.median(embedding_scores[similar_mask]):.3f}")

    has_embeddings = True

except Exception as e:
    print(f"  Sentence-BERT failed: {e}")
    print("  Continuing with TF-IDF only")
    embedding_scores = np.full(n, np.nan)
    has_embeddings = False

# =============================================================================
# 4. Save per-article similarity scores
# =============================================================================

print("\n--- Step 4: Saving per-article scores ---")

article_scores_path = os.path.join(data_dir, "article_similarity_scores.csv")
with open(article_scores_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "commission", "article_uid", "final_article_id", "format_label",
        "tfidf_cosine", "embedding_cosine",
        "genesis_text_length", "final_text_length", "n_authors"
    ])
    for i, entry in enumerate(mapping):
        writer.writerow([
            entry["commission"],
            entry["article_uid"],
            entry["final_article_id"],
            entry["format_label"],
            f"{tfidf_scores[i]:.6f}",
            f"{embedding_scores[i]:.6f}" if not np.isnan(embedding_scores[i]) else "",
            entry["genesis_text_length"],
            entry["final_text_length"],
            entry["n_authors"],
        ])
print(f"  Saved: {article_scores_path} ({n} articles)")

# =============================================================================
# 5. Aggregate per-convencional success scores
# =============================================================================

print("\n--- Step 5: Computing per-convencional success scores ---")

author_articles = defaultdict(list)
for i, entry in enumerate(mapping):
    for author in entry["authors"]:
        author_articles[author].append(i)

author_scores = []
for author in sorted(author_articles.keys()):
    indices = author_articles[author]
    n_arts = len(indices)
    tfidf_vals = tfidf_scores[indices]
    n_identical = sum(1 for idx in indices if mapping[idx]["format_label"] == "identical")
    n_similar = sum(1 for idx in indices if mapping[idx]["format_label"] == "similar")

    row = {
        "nombre_armonizado": author,
        "n_articles": n_arts,
        "mean_tfidf_retention": float(tfidf_vals.mean()),
        "median_tfidf_retention": float(np.median(tfidf_vals)),
        "min_tfidf_retention": float(tfidf_vals.min()),
        "max_tfidf_retention": float(tfidf_vals.max()),
        "n_identical": n_identical,
        "n_similar": n_similar,
        "pct_identical": n_identical / n_arts if n_arts > 0 else 0,
    }

    if has_embeddings:
        emb_vals = embedding_scores[indices]
        row["mean_embedding_retention"] = float(emb_vals.mean())
        row["median_embedding_retention"] = float(np.median(emb_vals))
    else:
        row["mean_embedding_retention"] = None
        row["median_embedding_retention"] = None

    author_scores.append(row)

# Save
success_path = os.path.join(data_dir, "author_success_scores.csv")
fieldnames = list(author_scores[0].keys())
with open(success_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(author_scores)

print(f"  Saved: {success_path} ({len(author_scores)} convencionales)")
print(f"  Mean TF-IDF retention across authors: {np.mean([s['mean_tfidf_retention'] for s in author_scores]):.3f}")

# Top 10 most successful
print("\n  Top 10 by mean TF-IDF retention:")
sorted_authors = sorted(author_scores, key=lambda x: x["mean_tfidf_retention"], reverse=True)
for s in sorted_authors[:10]:
    print(f"    {s['nombre_armonizado']:30s} | articles={s['n_articles']:3d} | "
          f"tfidf={s['mean_tfidf_retention']:.3f} | "
          f"identical={s['n_identical']}/{s['n_articles']}")

# Bottom 10
print("\n  Bottom 10 by mean TF-IDF retention:")
for s in sorted_authors[-10:]:
    print(f"    {s['nombre_armonizado']:30s} | articles={s['n_articles']:3d} | "
          f"tfidf={s['mean_tfidf_retention']:.3f} | "
          f"identical={s['n_identical']}/{s['n_articles']}")

print("\n--- Done ---")
