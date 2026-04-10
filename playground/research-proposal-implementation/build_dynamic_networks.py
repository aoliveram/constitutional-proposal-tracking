import json
import os
import itertools
from collections import defaultdict

# Official Bins for Commission 1
C1_BINS = ["03-17", "04-01", "04-18", "04-30"] 
# Official Bins for Commission 3
C3_BINS = ["02-14", "03-01", "03-14", "03-24", "04-06", "04-19", "04-26"]

base_dir = "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking"
output_dir = os.path.join(base_dir, "playground/research-proposal-implementation")

files = {
    "C1": os.path.join(base_dir, "playground/comision-1-data/data/C1_texto-sistematizado_enriched_manual.json"),
    "C3": os.path.join(base_dir, "comision-3/draft-after-indications-manual/C3_historial_manual.json")
}

def load_data(filepath):
    if not os.path.exists(filepath):
        # Fallback for search
        if "C1" in filepath:
            filepath = os.path.join(base_dir, "comision-1/draft-after-indications-manual/C1_texto-sistematizado_enriched_manual.json")
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_authors(authors_list):
    out = []
    if not authors_list: return out
    for a in authors_list:
        if isinstance(a, list):
            out.extend([str(x).strip() for x in a if x])
        elif a:
            out.append(str(a).strip())
    return sorted(list(set([x for x in out if len(x)>3 and "S/I" not in x])))

def get_bin(ts, bins):
    if not ts: return None
    # Clean timestamp for prefix matching (e.g. 03-01-1 -> 03-01)
    # Check if any bin is a prefix or matches the date segment
    for b in bins:
        if b in ts:
            return b
    return None

def build_networks(data, bins, name):
    # G_cumulative stores current weight of edges
    G_cumulative = defaultdict(int) 
    
    # Wave objects. T0 is Genesis.
    waves = {}
    
    # Step 0: Genesis
    for item in data:
        authors = clean_authors(item.get("authors", []))
        if authors:
            pairs = itertools.combinations(authors, 2)
            for p in pairs:
                G_cumulative[p] += 1
    
    waves["T0_Genesis"] = dict(G_cumulative)
    
    # Step 1...N: Group indications by official bins
    # Initialize bin collections
    bin_data = {b: [] for b in bins}
    
    for item in data:
        history = item.get("history", [])
        for h in history:
            ts = h.get("timestamp", "")
            target_bin = get_bin(ts, bins)
            if target_bin:
                authors = clean_authors(h.get("authors", []))
                if authors:
                    bin_data[target_bin].append(authors)
                    
    # Now build waves sequentially
    step_num = 1
    for b in bins:
        events = bin_data[b]
        for authors in events:
            pairs = itertools.combinations(authors, 2)
            for p in pairs:
                G_cumulative[p] += 1
        waves[f"T{step_num}_{b}"] = dict(G_cumulative)
        step_num += 1
        
    return waves

for c_name, filepath in files.items():
    print(f"Processing {c_name}...")
    data = load_data(filepath)
    if data:
        official_bins = C1_BINS if c_name == "C1" else C3_BINS
        waves = build_networks(data, official_bins, c_name)
        
        # Save results
        out_file = os.path.join(output_dir, f"{c_name}_dynamic_networks_official.json")
        serializable = {}
        for t_label, edges in waves.items():
            serializable[t_label] = [{"source": k[0], "target": k[1], "weight": w} for k, w in edges.items()]
        
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, ensure_ascii=False, indent=4)
        print(f"Saved {c_name} with {len(waves)} steps.")
