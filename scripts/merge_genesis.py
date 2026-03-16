import json
import os

base_dir = "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking/comision-1/genesis-extracted"

file1 = os.path.join(base_dir, "C1_GENESIS_texto-sistematizado-1-03-17.json")
file2 = os.path.join(base_dir, "C1_GENESIS_texto-sistematizado-2-04-06.json")
output_file = os.path.join(base_dir, "C1_GENESIS_merged_1_and_2.json")

print(f"Loading {file1}...")
with open(file1, 'r', encoding='utf-8') as f:
    data1 = json.load(f)

print(f"Loading {file2}...")
with open(file2, 'r', encoding='utf-8') as f:
    data2 = json.load(f)

# Concatenate arrays
merged_data = data1 + data2

print(f"Writing {len(merged_data)} items to {output_file}...")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=2)

print("Done.")
