
import json
import os
import glob
import re

def merge_commission_genesis(com_id):
    base_dir = f"/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking/comision-{com_id}/genesis-extracted"
    
    # 1. Look for all raw GENESIS JSONs (ignore merged or enriched versions for the base merge)
    # The pattern is C{id}_GENESIS_*.json but excluding merged/enriched
    pattern = os.path.join(base_dir, f"C{com_id}_GENESIS_*.json")
    all_files = glob.glob(pattern)
    
    # Filter out already merged or enriched files and specific preview files
    files_to_merge = [f for f in all_files if "merged" not in f and "enriched" not in f and "PREVIEW" not in f]
    
    # Sort files by sequence number (-1-) or by the date found in the filename (MM-DD)
    def sort_key(filepath):
        filename = os.path.basename(filepath)
        # Check for sequence digit -NUMBER-
        match_seq = re.search(r'-(\d+)-', filename)
        if match_seq:
            return (0, int(match_seq.group(1)), filename)
        
        # Check for date-like MM-DD or MM-DD-YY
        match_date = re.search(r'(\d{2}-\d{2})', filename)
        if match_date:
            return (1, match_date.group(1), filename)
            
        return (2, filename)

    files_to_merge.sort(key=sort_key)
    
    if not files_to_merge:
        print(f"Comisión {com_id}: No files found to merge.")
        return

    print(f"Comisión {com_id}: Merging {len(files_to_merge)} files:")
    for f in files_to_merge:
        print(f"  - {os.path.basename(f)}")

    # 2. Extract and concatenate
    master_data = []
    for f in files_to_merge:
        with open(f, 'r', encoding='utf-8') as src:
            data = json.load(src)
            # Some extractions might be dicts or lists depending on the script version
            if isinstance(data, list):
                master_data.extend(data)
            else:
                print(f"Warning: {f} is not a list. Skipping content.")

    # 3. Save Master
    output_file = os.path.join(base_dir, f"C{com_id}_GENESIS_master_merged.json")
    with open(output_file, 'w', encoding='utf-8') as out:
        json.dump(master_data, out, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(master_data)} items to {os.path.basename(output_file)}")

def main():
    # Process all commissions
    for i in range(1, 8):
        merge_commission_genesis(i)

if __name__ == "__main__":
    main()
