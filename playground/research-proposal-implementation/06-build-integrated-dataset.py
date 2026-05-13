"""
06-build-integrated-dataset.py
Merge all data sources into the final cross-sectional analysis dataset.

Each row = one convencional. Merges:
- Author success scores (from 05-nlp)
- Network metrics (from 01-ergm)
- Ideological metrics (from 02-emirt)
- Profile covariates (from BCN webscrapping)
- Derived variables: ego_heterophily, cross_coalition_ties
"""

import json
import os
import csv
from collections import defaultdict

base_dir = "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking"
data_dir = os.path.join(base_dir, "playground/research-proposal-implementation/data")


def load_csv_as_dict(filepath, key_col):
    """Load CSV into dict keyed by key_col."""
    rows = {}
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows[row[key_col]] = row
    return rows


# =============================================================================
# 1. Load all data sources
# =============================================================================

print("--- Step 1: Loading data sources ---")

# Author success scores
success = load_csv_as_dict(
    os.path.join(data_dir, "author_success_scores.csv"), "nombre_armonizado")
print(f"  Author success scores: {len(success)} convencionales")

# Network metrics
metrics = load_csv_as_dict(
    os.path.join(data_dir, "network_metrics.csv"), "nombre_armonizado")
print(f"  Network metrics: {len(metrics)} convencionales")

# Ideological metrics
ideology = load_csv_as_dict(
    os.path.join(data_dir, "emirt_summary_metrics.csv"), "nombre_armonizado")
print(f"  Ideological metrics: {len(ideology)} convencionales")

# Profiles
with open(os.path.join(base_dir, "conventionals-bcn-webscrapping/conventional-profiles.json"),
          "r", encoding="utf-8") as f:
    profiles_list = json.load(f)
profiles = {p["nombre_armonizado"]: p for p in profiles_list}
print(f"  Profiles: {len(profiles)} convencionales")

# Pooled network edges (for ego_heterophily computation)
edges = []
with open(os.path.join(data_dir, "pooled_cumulative_network.csv"), "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        edges.append((row["source"], row["target"], int(row["weight"])))
print(f"  Pooled edges: {len(edges)}")

# =============================================================================
# 2. Compute derived network variables
# =============================================================================

print("\n--- Step 2: Computing derived variables ---")

# Build adjacency list with weights and coalition info
neighbors = defaultdict(list)  # name -> [(neighbor, weight)]
for s, t, w in edges:
    neighbors[s].append((t, w))
    neighbors[t].append((s, w))

# Ego heterophily: proportion of ego's partners from different coalitions
def get_coalition(name):
    if name in profiles:
        return profiles[name].get("afiliacion_agrupada", "Desconocida")
    if name in metrics:
        return metrics[name].get("afiliacion_agrupada", "Desconocida")
    return "Desconocida"

ego_heterophily = {}
cross_coalition_ties = {}

for name in set(list(metrics.keys()) + list(success.keys())):
    own_coalition = get_coalition(name)
    nbrs = neighbors.get(name, [])
    if not nbrs:
        ego_heterophily[name] = 0.0
        cross_coalition_ties[name] = 0
        continue

    n_cross = 0
    total = 0
    for nbr_name, weight in nbrs:
        nbr_coalition = get_coalition(nbr_name)
        total += 1
        if nbr_coalition != own_coalition:
            n_cross += 1

    ego_heterophily[name] = n_cross / total if total > 0 else 0.0
    cross_coalition_ties[name] = n_cross

print(f"  Computed ego_heterophily for {len(ego_heterophily)} convencionales")

# =============================================================================
# 3. Merge into integrated dataset
# =============================================================================

print("\n--- Step 3: Merging datasets ---")

# Use the union of all names that appear in any dataset
all_names = sorted(
    set(success.keys()) | set(metrics.keys()) | set(ideology.keys())
)
print(f"  Union of all names: {len(all_names)}")

integrated = []
for name in all_names:
    row = {"nombre_armonizado": name}

    # Success scores (from NLP)
    if name in success:
        s = success[name]
        row["n_articles_authored"] = int(s["n_articles"])
        row["mean_tfidf_retention"] = float(s["mean_tfidf_retention"])
        row["median_tfidf_retention"] = float(s["median_tfidf_retention"])
        row["n_identical"] = int(s["n_identical"])
        row["n_similar"] = int(s["n_similar"])
        row["pct_identical"] = float(s["pct_identical"])
        emb = s.get("mean_embedding_retention")
        row["mean_embedding_retention"] = float(emb) if emb and emb != "None" else None
    else:
        row["n_articles_authored"] = 0
        row["mean_tfidf_retention"] = None
        row["median_tfidf_retention"] = None
        row["n_identical"] = 0
        row["n_similar"] = 0
        row["pct_identical"] = None
        row["mean_embedding_retention"] = None

    # Network metrics
    if name in metrics:
        m = metrics[name]
        row["degree"] = int(m["degree"])
        row["weighted_degree"] = float(m["weighted_degree"])
        row["betweenness"] = float(m["betweenness"])
        row["eigenvector"] = float(m["eigenvector"])
    else:
        row["degree"] = 0
        row["weighted_degree"] = 0.0
        row["betweenness"] = 0.0
        row["eigenvector"] = 0.0

    # Ideological metrics
    if name in ideology:
        idl = ideology[name]
        row["theta_mean"] = float(idl["theta_mean"])
        row["theta_sd"] = float(idl["theta_sd"])
        row["theta_range"] = float(idl["theta_range"])
        row["theta_shift"] = float(idl["theta_shift"])
        row["theta_first"] = float(idl["theta_first"])
        row["theta_last"] = float(idl["theta_last"])
    else:
        row["theta_mean"] = None
        row["theta_sd"] = None
        row["theta_range"] = None
        row["theta_shift"] = None
        row["theta_first"] = None
        row["theta_last"] = None

    # Profile covariates
    if name in profiles:
        p = profiles[name]
        row["es_mujer"] = p.get("es_mujer", None)
        row["es_abogado"] = p.get("es_abogado", None)
        row["edad_al_asumir"] = p.get("edad_al_asumir", None)
        row["experiencia_previa_institucional"] = p.get("experiencia_previa_institucional", None)
        row["afiliacion_agrupada"] = p.get("afiliacion_agrupada", "Desconocida")
        row["distrito"] = p.get("distrito", None)
        row["grado_academico_nivel"] = p.get("grado_academico_nivel", None)
    else:
        row["es_mujer"] = None
        row["es_abogado"] = None
        row["edad_al_asumir"] = None
        row["experiencia_previa_institucional"] = None
        row["afiliacion_agrupada"] = "Desconocida"
        row["distrito"] = None
        row["grado_academico_nivel"] = None

    # Derived variables
    row["ego_heterophily"] = ego_heterophily.get(name, 0.0)
    row["cross_coalition_ties"] = cross_coalition_ties.get(name, 0)

    integrated.append(row)

# =============================================================================
# 4. Save
# =============================================================================

print("\n--- Step 4: Saving ---")

# CSV
csv_path = os.path.join(data_dir, "integrated_dataset.csv")
fieldnames = list(integrated[0].keys())
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(integrated)
print(f"  Saved: {csv_path} ({len(integrated)} rows, {len(fieldnames)} columns)")

# JSON
json_path = os.path.join(data_dir, "integrated_dataset.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(integrated, f, ensure_ascii=False, indent=2)
print(f"  Saved: {json_path}")

# =============================================================================
# 5. Summary stats
# =============================================================================

print("\n--- Summary ---")
n_with_success = sum(1 for r in integrated if r["mean_tfidf_retention"] is not None)
n_with_ideology = sum(1 for r in integrated if r["theta_mean"] is not None)
n_with_network = sum(1 for r in integrated if r["degree"] > 0)
n_with_profile = sum(1 for r in integrated if r["es_mujer"] is not None)

print(f"  Total convencionales: {len(integrated)}")
print(f"  With success score:   {n_with_success}")
print(f"  With ideology:        {n_with_ideology}")
print(f"  With network metrics: {n_with_network}")
print(f"  With profile data:    {n_with_profile}")
print(f"  Complete cases (all 4): {sum(1 for r in integrated if r['mean_tfidf_retention'] is not None and r['theta_mean'] is not None and r['degree'] > 0 and r['es_mujer'] is not None)}")

# Correlation between success and network position
import numpy as np
success_vals = [(r["mean_tfidf_retention"], r["weighted_degree"], r["betweenness"], r["theta_mean"])
                for r in integrated
                if r["mean_tfidf_retention"] is not None and r["theta_mean"] is not None]
if success_vals:
    arr = np.array(success_vals)
    print(f"\n  Correlations (N={len(arr)}):")
    print(f"    success ~ weighted_degree: r = {np.corrcoef(arr[:,0], arr[:,1])[0,1]:.3f}")
    print(f"    success ~ betweenness:     r = {np.corrcoef(arr[:,0], arr[:,2])[0,1]:.3f}")
    print(f"    success ~ theta_mean:      r = {np.corrcoef(arr[:,0], arr[:,3])[0,1]:.3f}")

print("\n--- Done ---")
