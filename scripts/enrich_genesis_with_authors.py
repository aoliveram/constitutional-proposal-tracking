import os
import json
import re
import glob

# Configuration: Target only the requested commissions
TARGET_COMMISSIONS = [1, 3, 5, 6, 7]
SUBMITTED_INITIATIVES_DIR = "submitted_initiatives"

def normalize_id(id_string):
    """
    Normalizes IDs to just the number part.
    Example: "116-1" -> "116"
             "ICC N° 514-3" -> "514"
    """
    s = str(id_string).strip()
    # Remove common prefixes
    s = re.sub(r'ICC\s*N°\s*', '', s, flags=re.IGNORECASE)
    # Extract the first sequence of digits
    match = re.match(r'^(\d+)', s)
    if match:
        return match.group(1)
    return s

def load_authors_map():
    """
    Loads all authors from submitted_initiatives JSONs into a map.
    The map is indexed by the base number of the initiative.
    """
    authors_map = {}
    # Use the pattern for the files in the submitted_initiatives directory
    pattern = os.path.join(SUBMITTED_INITIATIVES_DIR, "api_extracted_*_corrected_4.json")
    files = glob.glob(pattern)
    
    print(f"Loading authors from {len(files)} files found in '{SUBMITTED_INITIATIVES_DIR}'...")
    
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Structure: { "filename.pdf": { "firmantes_matched": [...] }, ... }
                for key, val in data.items():
                    # Extract the base number ID from the key (e.g., "99" from "99-3-c-...")
                    match = re.match(r'^(\d+)', key)
                    if match:
                        norm_id = match.group(1)
                        # We specifically use "firmantes_matched" as requested
                        authors = val.get('firmantes_matched', [])
                        if authors:
                            if norm_id in authors_map:
                                # Merge and de-duplicate if multiple files mention the same ID
                                authors_map[norm_id] = list(set(authors_map[norm_id] + authors))
                            else:
                                authors_map[norm_id] = authors
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                
    return authors_map

def enrich_files():
    authors_map = load_authors_map()
    print(f"Loaded mapping for {len(authors_map)} unique initiative IDs.")
    
    for com_id in TARGET_COMMISSIONS:
        base_dir = os.path.join(f"comision-{com_id}", "genesis-extracted")
        if not os.path.exists(base_dir):
            print(f"Directory {base_dir} not found. Skipping Commission {com_id}.")
            continue
            
        # Target only the base GENESIS files as requested
        pattern = os.path.join(base_dir, f"C{com_id}_GENESIS_*.json")
        for filepath in glob.glob(pattern):
            # Exclude files already marked as enriched, merged or previews
            if any(x in filepath for x in ["enriched", "merged", "PREVIEW"]):
                continue
                
            print(f"Processing: {filepath}")
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except Exception as e:
                    print(f"  Error loading JSON {filepath}: {e}")
                    continue
            
            modified = False
            for entry in data:
                # Only add authors if the entry doesn't have them or they are empty
                if not entry.get("authors"):
                    sources = entry.get("sources", [])
                    if isinstance(sources, str):
                        sources = [sources]
                    
                    found_authors = set()
                    for src in sources:
                        norm_src = normalize_id(src)
                        if norm_src in authors_map:
                            found_authors.update(authors_map[norm_src])
                    
                    if found_authors:
                        entry["authors"] = sorted(list(found_authors))
                        modified = True
            
            if modified:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"  --> Updated {os.path.basename(filepath)} with authorship details.")
            else:
                print(f"  --> No missing author data could be matched for {os.path.basename(filepath)}.")

if __name__ == "__main__":
    enrich_files()
