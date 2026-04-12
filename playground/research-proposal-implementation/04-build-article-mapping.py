"""
04-build-article-mapping.py
Build unified mapping from commission articles to final draft articles.

Only includes entries from C1, C3, C5 whose final_status starts with
"Idéntico" or "Similar". Extracts text pairs (genesis text vs final text)
and author lists for NLP comparison in the next step.
"""

import json
import os
import re
import csv

base_dir = "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking"
data_dir = os.path.join(base_dir, "playground/research-proposal-implementation/data")

COMMISSION_FILES = {
    "C1": os.path.join(base_dir, "comision-1/draft-after-indications-manual/C1_texto-sistematizado_enriched_manual.json"),
    "C3": os.path.join(base_dir, "comision-3/draft-after-indications-manual/C3_historial_manual.json"),
    "C5": os.path.join(base_dir, "comision-5/draft-after-indications-manual/C5_historial_manual.json"),
}


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_final_status(status):
    """
    Parse final_status field to extract format_label and final_article_id.
    Returns (format_label, final_article_id) or (None, None) if not mapped.

    Examples:
        "idéntico a 296.- Artículo 1" -> ("identical", "296")
        "Similar a 143.- Artículo 2" -> ("similar", "143")
        "Idéntico a 1.- Artículo 2°.-" -> ("identical", "1")
        "idéntio a 304.- Artículo 20" -> ("identical", "304")  # typo variant
        "Eliminado" -> (None, None)
    """
    if not status:
        return None, None

    status_lower = status.lower().strip()

    # Match "idéntico/similar a NNN.- ..."
    # Handle typos: "idéntio", "identico", etc.
    match = re.match(
        r"(id[eé]nt?i[co]o?|similar)\s+a\s+(\d+)\s*\.-",
        status_lower
    )
    if match:
        label_raw = match.group(1)
        article_num = match.group(2)

        if "similar" in label_raw:
            return "similar", article_num
        else:
            return "identical", article_num

    return None, None


def get_article_text(item):
    """Extract the most relevant text from a commission article entry."""
    # For entries with history, use the last content_snapshot (final state)
    if "history" in item and item["history"]:
        last_history = item["history"][-1]
        if "content_snapshot" in last_history and last_history["content_snapshot"]:
            return last_history["content_snapshot"].strip()

    # Fallback to top-level text
    if "text" in item and item["text"]:
        return item["text"].strip()

    # Fallback to content field
    if "content" in item and item["content"]:
        return item["content"].strip()

    return ""


def clean_authors(authors_list):
    """Extract and clean author names."""
    if not authors_list:
        return []
    out = []
    for a in authors_list:
        if isinstance(a, list):
            out.extend([str(x).strip() for x in a if x])
        elif a:
            out.append(str(a).strip())
    return sorted(set(x for x in out if len(x) > 3 and "S/I" not in x))


# =============================================================================
# 1. Load final draft text
# =============================================================================

print("--- Step 1: Loading final draft text ---")
final_draft = load_json(os.path.join(base_dir, "proposals/draft_final_text.json"))
# Build lookup by article_id
final_text_by_id = {}
for art in final_draft:
    aid = art["article_id"]
    final_text_by_id[aid] = art["text"]
print(f"  Final draft articles: {len(final_text_by_id)}")

# =============================================================================
# 2. Parse commission files and extract mapped articles
# =============================================================================

print("\n--- Step 2: Parsing commission files ---")

mapping_entries = []
stats = {"identical": 0, "similar": 0, "eliminated": 0, "not_found": 0, "no_status": 0}

for comm_name, filepath in COMMISSION_FILES.items():
    data = load_json(filepath)
    comm_mapped = 0
    comm_skipped = 0

    for item in data:
        final_status = item.get("final_status", "")
        format_label, final_article_id = parse_final_status(final_status)

        if format_label is None:
            # Categorize for stats
            if not final_status:
                stats["no_status"] += 1
            elif "eliminado" in final_status.lower():
                stats["eliminated"] += 1
            elif "no se encuentra" in final_status.lower():
                stats["not_found"] += 1
            comm_skipped += 1
            continue

        stats[format_label] += 1

        # Get commission article text
        genesis_text = get_article_text(item)

        # Get final draft text
        final_text = final_text_by_id.get(final_article_id, "")
        if not final_text:
            print(f"  WARNING: Final article {final_article_id} not found in draft "
                  f"(from {comm_name} {item.get('article_uid', '?')})")
            continue

        # Get authors
        authors = clean_authors(item.get("authors", []))

        # Get article_uid
        article_uid = item.get("article_uid", "")

        mapping_entries.append({
            "commission": comm_name,
            "article_uid": article_uid,
            "final_article_id": final_article_id,
            "format_label": format_label,
            "genesis_text": genesis_text,
            "final_text": final_text,
            "authors": authors,
            "n_authors": len(authors),
            "genesis_text_length": len(genesis_text),
            "final_text_length": len(final_text),
        })
        comm_mapped += 1

    print(f"  {comm_name}: {comm_mapped} mapped, {comm_skipped} skipped "
          f"(from {len(data)} total entries)")

# =============================================================================
# 3. Summary and save
# =============================================================================

print(f"\n--- Step 3: Summary ---")
print(f"  Total mapped articles: {len(mapping_entries)}")
print(f"  Identical: {stats['identical']}")
print(f"  Similar: {stats['similar']}")
print(f"  Excluded - Eliminated: {stats['eliminated']}")
print(f"  Excluded - Not found: {stats['not_found']}")
print(f"  Excluded - No status: {stats['no_status']}")

# Unique authors across all mapped articles
all_authors = set()
for entry in mapping_entries:
    all_authors.update(entry["authors"])
print(f"  Unique authors in mapped articles: {len(all_authors)}")

# Commission breakdown
for comm in ["C1", "C3", "C5"]:
    comm_entries = [e for e in mapping_entries if e["commission"] == comm]
    n_id = sum(1 for e in comm_entries if e["format_label"] == "identical")
    n_sim = sum(1 for e in comm_entries if e["format_label"] == "similar")
    print(f"    {comm}: {len(comm_entries)} total ({n_id} identical, {n_sim} similar)")

# Save as JSON
output_path = os.path.join(data_dir, "article_mapping_unified.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(mapping_entries, f, ensure_ascii=False, indent=2)
print(f"\n  Saved: {output_path}")

# Also save as CSV (with truncated text for readability)
csv_path = os.path.join(data_dir, "article_mapping_unified.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "commission", "article_uid", "final_article_id", "format_label",
        "n_authors", "authors", "genesis_text_length", "final_text_length"
    ])
    for entry in mapping_entries:
        writer.writerow([
            entry["commission"],
            entry["article_uid"],
            entry["final_article_id"],
            entry["format_label"],
            entry["n_authors"],
            "|".join(entry["authors"]),
            entry["genesis_text_length"],
            entry["final_text_length"],
        ])
print(f"  Saved: {csv_path}")

print("\n--- Done ---")
