import json
import os
import itertools
from collections import defaultdict

# Script for generating Dynamic Networks (Co-authorship Waves)
# Inputs: C1 and C3 manual JSON files

base_dir = "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking"

files = {
    "C1": os.path.join(base_dir, "playground/comision-1-data/data/C1_texto-sistematizado_enriched_manual.json"),
    "C3": os.path.join(base_dir, "comision-3/draft-after-indications-manual/C3_historial_manual.json")
}

output_dir = os.path.join(base_dir, "playground/research-proposal-implementation")

def load_data(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_authors(authors_list):
    # Flatten and clean the authors list
    out = []
    if not authors_list: return out
    for a in authors_list:
        if isinstance(a, list):
            out.extend([x.strip() for x in a if isinstance(x, str)])
        elif isinstance(a, str):
            out.append(a.strip())
    # Remove empty or non informative
    return [x for x in out if len(x)>3 and "S/I" not in x]

def build_networks_for_comision(data, name):
    # Network state tracking
    # edge weights map: tuple(a, b) -> cumulative weight
    G_cumulative = defaultdict(int) 
    
    # Time step 0: Genesis 
    for item in data:
        genesis_authors = clean_authors(item.get("authors", []))
        if genesis_authors:
            # Generate all pairs
            pairs = itertools.combinations(sorted(genesis_authors), 2)
            for p in pairs:
                G_cumulative[p] += 1
                
    waves = {}
    # Record T=0 (Genesis)
    waves["T0_Genesis"] = dict(G_cumulative)
    
    # Time step > 0: Based on indications history
    history_events = defaultdict(list)
    for item in data:
        history = item.get("history", [])
        if not history: continue
        for h in history:
            ts = h.get("timestamp", "Unspecified")
            authors = clean_authors(h.get("authors", []))
            if authors:
                history_events[ts].append(authors)
                
    # Sort timestamps chronologically (mm-dd format typical)
    sorted_ts = sorted(list(history_events.keys()))
    
    step = 1
    for ts in sorted_ts:
        for authors in history_events[ts]:
            pairs = itertools.combinations(sorted(authors), 2)
            for p in pairs:
                G_cumulative[p] += 1 # Adds strictly 1 point per indication coauthorship
        waves[f"T{step}_{ts}"] = dict(G_cumulative)
        step += 1
        
    return waves

for c_name, filepath in files.items():
    print(f"Processing {c_name} => {filepath}")
    data = load_data(filepath)
    if not data:
        # Fallback check for C1
        if c_name == "C1":
            filepath = os.path.join(base_dir, "comision-1/draft-after-indications-manual/C1_texto-sistematizado_enriched_manual.json")
            data = load_data(filepath)
    if data:
        waves = build_networks_for_comision(data, c_name)
        
        # Save output
        out_file = os.path.join(output_dir, f"{c_name}_dynamic_networks.json")
        
        serializable_waves = {}
        for t_label, edges in waves.items():
            serializable_waves[t_label] = [{"source": k[0], "target": k[1], "weight": w} for k, w in edges.items()]
            
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_waves, f, ensure_ascii=False, indent=4)
        print(f"Saved {c_name} network with {len(waves)} temporal waves -> {out_file}")

print("Done building dynamic networks.")
