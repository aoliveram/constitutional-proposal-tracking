"""
00-build_dynamic_networks.py
Build co-authorship networks from genesis entries across all 5 commissions.

Model 1 uses ALL commissions (C1, C3, C5, C6, C7) for the pooled network.
Per-commission temporal networks (with history-based waves) are built for C1, C3, C5 only
(used in Model 2).

Only top-level `authors` fields are used for genesis network construction.
History entries add edges in subsequent temporal waves (C1, C3, C5 only).
"""

import json
import os
import csv
import itertools
from collections import defaultdict

base_dir = "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking"
impl_dir = os.path.join(base_dir, "playground/research-proposal-implementation")
output_dir = os.path.join(impl_dir, "network-visualization")
data_dir = os.path.join(impl_dir, "data")

# --- Commission file paths ---
COMMISSION_FILES = {
    "C1": os.path.join(base_dir, "comision-1/draft-after-indications-manual/C1_texto-sistematizado_enriched_manual.json"),
    "C3": os.path.join(base_dir, "comision-3/draft-after-indications-manual/C3_historial_manual.json"),
    "C5": os.path.join(base_dir, "comision-5/draft-after-indications-manual/C5_historial_manual.json"),
    "C6": os.path.join(base_dir, "comision-6/draft-after-indications-manual/C6_historial_manual.json"),
    "C7": os.path.join(base_dir, "comision-7/draft-after-indications-manual/C7_GENESIS_texto-sistematizado-02-17_enriched_manual.json"),
}

# Temporal bins for per-commission dynamic networks (C1, C3, C5 only)
COMMISSION_BINS = {
    "C1": ["03-17", "04-01", "04-18", "04-30"],
    "C3": ["02-14", "03-01", "03-14", "03-24", "04-06", "04-19", "04-26"],
    "C5": ["03-01", "03-16", "03-17", "04-09", "05-04"],
}


def load_data(filepath):
    if not os.path.exists(filepath):
        print(f"  File not found: {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_authors(authors_list):
    """Extract and clean author names from a list (may contain nested lists)."""
    out = []
    if not authors_list:
        return out
    for a in authors_list:
        if isinstance(a, list):
            out.extend([str(x).strip() for x in a if x])
        elif a:
            out.append(str(a).strip())
    return sorted(set(x for x in out if len(x) > 3 and "S/I" not in x))


def get_bin(timestamp, bins):
    """Match a timestamp string to the appropriate bin via prefix matching."""
    if not timestamp:
        return None
    for b in bins:
        if timestamp.startswith(b):
            return b
    return None


def build_genesis_edges(data):
    """Build co-authorship edges from top-level authors (genesis entries only)."""
    edges = defaultdict(int)
    for item in data:
        authors = clean_authors(item.get("authors", []))
        if len(authors) >= 2:
            for pair in itertools.combinations(authors, 2):
                edges[pair] += 1
    return edges


def build_temporal_networks(data, bins):
    """Build per-commission temporal networks: T0 = genesis, T1..N = history waves."""
    G_cumulative = defaultdict(int)

    # T0: Genesis (top-level authors)
    for item in data:
        authors = clean_authors(item.get("authors", []))
        if len(authors) >= 2:
            for pair in itertools.combinations(authors, 2):
                G_cumulative[pair] += 1

    waves = {"T0_Genesis": dict(G_cumulative)}

    # Collect history entries per bin
    bin_data = {b: [] for b in bins}
    for item in data:
        for h in item.get("history", []):
            ts = h.get("timestamp", "")
            target_bin = get_bin(ts, bins)
            if target_bin:
                authors = clean_authors(h.get("authors", []))
                if len(authors) >= 2:
                    bin_data[target_bin].append(authors)

    # Build waves sequentially (cumulative)
    for step_num, b in enumerate(bins, start=1):
        for authors in bin_data[b]:
            for pair in itertools.combinations(authors, 2):
                G_cumulative[pair] += 1
        waves[f"T{step_num}_{b}"] = dict(G_cumulative)

    return waves


def save_dynamic_network_json(waves, filepath):
    """Save temporal network waves to JSON."""
    serializable = {}
    for t_label, edges in waves.items():
        serializable[t_label] = [
            {"source": k[0], "target": k[1], "weight": w}
            for k, w in edges.items()
        ]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=4)


def save_pooled_network_csv(edges, filepath):
    """Save pooled network as CSV edge list."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target", "weight"])
        for (src, tgt), weight in sorted(edges.items()):
            writer.writerow([src, tgt, weight])


# =============================================================================
# Main execution
# =============================================================================

if __name__ == "__main__":
    pooled_edges = defaultdict(int)
    commission_stats = {}

    # --- Step 1: Build per-commission temporal networks (C1, C3, C5) ---
    for c_name in ["C1", "C3", "C5"]:
        filepath = COMMISSION_FILES[c_name]
        print(f"Processing {c_name} (temporal network)...")
        data = load_data(filepath)
        if not data:
            continue

        bins = COMMISSION_BINS[c_name]
        waves = build_temporal_networks(data, bins)

        out_file = os.path.join(output_dir, f"{c_name}_dynamic_networks.json")
        save_dynamic_network_json(waves, out_file)

        # Use the final cumulative wave for the pooled network
        final_wave_key = list(waves.keys())[-1]
        for (src, tgt), w in waves[final_wave_key].items():
            pooled_edges[(src, tgt)] += w

        n_nodes = len(set(
            n for edge_list in waves.values()
            for e in edge_list
            for n in (e if isinstance(e, tuple) else (None,))
        ))
        genesis_edges = waves["T0_Genesis"]
        commission_stats[c_name] = {
            "total_items": len(data),
            "waves": len(waves),
            "genesis_edges": len(genesis_edges),
            "final_edges": len(waves[final_wave_key]),
        }
        print(f"  Saved {c_name} with {len(waves)} waves, {len(genesis_edges)} genesis edges, {len(waves[final_wave_key])} final edges")

    # --- Step 2: Build genesis-only networks for C6, C7 (no temporal waves) ---
    for c_name in ["C6", "C7"]:
        filepath = COMMISSION_FILES[c_name]
        print(f"Processing {c_name} (genesis only)...")
        data = load_data(filepath)
        if not data:
            continue

        genesis_edges = build_genesis_edges(data)
        for pair, w in genesis_edges.items():
            pooled_edges[pair] += w

        commission_stats[c_name] = {
            "total_items": len(data),
            "waves": 1,
            "genesis_edges": len(genesis_edges),
            "final_edges": len(genesis_edges),
        }
        print(f"  {c_name}: {len(genesis_edges)} genesis edges from {len(data)} items")

    # --- Step 3: Save pooled cumulative network ---
    pooled_path = os.path.join(data_dir, "pooled_cumulative_network.csv")
    save_pooled_network_csv(pooled_edges, pooled_path)

    # Compute pooled stats
    all_nodes = set()
    for (src, tgt) in pooled_edges:
        all_nodes.add(src)
        all_nodes.add(tgt)

    print(f"\n{'='*60}")
    print(f"POOLED CUMULATIVE NETWORK")
    print(f"  Nodes: {len(all_nodes)}")
    print(f"  Edges: {len(pooled_edges)}")
    print(f"  Total weight: {sum(pooled_edges.values())}")
    print(f"  Saved to: {pooled_path}")

    print(f"\nPer-commission breakdown:")
    for c_name, stats in commission_stats.items():
        print(f"  {c_name}: {stats['total_items']} items, {stats['genesis_edges']} genesis edges, {stats['final_edges']} final edges, {stats['waves']} waves")
