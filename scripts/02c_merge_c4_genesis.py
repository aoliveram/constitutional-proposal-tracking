import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COM4_DIR = os.path.join(BASE_DIR, "comision-4", "genesis-extracted")

main_file = os.path.join(COM4_DIR, "C4_GENESIS_votacion-general_enriched.json")
b3_file = os.path.join(COM4_DIR, "C4_GENESIS_votacion-general-bloque3.json")

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

print("Merging Block 3 ICCs into the main Genesis-0 pool...")

main_data = load_json(main_file)
b3_data = load_json(b3_file)

if not b3_data:
    print("No Block 3 data found to merge.")
else:
    # Add new ones that might not be exactly duplicated
    initial_len = len(main_data)
    
    # We could check for duplicates by icc_id and text, but it's an append.
    # Usually they are distinct blocks.
    main_data.extend(b3_data)
    
    with open(main_file, 'w', encoding='utf-8') as f:
        json.dump(main_data, f, ensure_ascii=False, indent=2)
        
    print(f"Merged successfully. Genesis grew from {initial_len} to {len(main_data)} initiatives.")
    
    # Optional cleanup
    os.remove(b3_file)
    print("Cleaned up temporary Block 3 file.")
