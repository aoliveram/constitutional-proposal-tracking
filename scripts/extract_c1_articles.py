from pathlib import Path
import json
import re

source = Path(r"c:/Users/vicel/Proyectos/constitutional-proposal-tracking/comision-1/C1_BORRADOR-CONSTITUCIONAL-14-05-22.md")
target = Path(r"c:/Users/vicel/Proyectos/constitutional-proposal-tracking/comision-1/dataverse-final/C1_BORRADOR_final.json")

text = source.read_text(encoding="utf-8")
lines = text.splitlines()
article_re = re.compile(r"^\s*(\d+\.-\s*Artículo\s+)([^\.\-]+)", re.IGNORECASE)

entries = []
current = None

for line in lines:
    m = article_re.match(line)
    if m:
        if current is not None:
            paragraphs = []
            buffer = []
            for l in current["text_lines"]:
                if l.strip() == "":
                    if buffer:
                        paragraphs.append(" ".join(buffer))
                        buffer = []
                else:
                    buffer.append(l.strip())
            if buffer:
                paragraphs.append(" ".join(buffer))
            current["text"] = "\n\n".join(paragraphs).strip()
            del current["text_lines"]
            entries.append(current)

        prefix = m.group(1).strip()
        article_num = m.group(2).strip()
        article_num = re.sub(r"[°º]+", "", article_num).strip()
        article_field = f"{prefix}{article_num}"
        current = {"article": article_field, "text_lines": []}
        rest = line[m.end():].strip()
        if rest:
            current["text_lines"].append(rest)
        continue

    if current is not None:
        current["text_lines"].append(line)

if current is not None:
    paragraphs = []
    buffer = []
    for l in current["text_lines"]:
        if l.strip() == "":
            if buffer:
                paragraphs.append(" ".join(buffer))
                buffer = []
        else:
            buffer.append(l.strip())
    if buffer:
        paragraphs.append(" ".join(buffer))
    current["text"] = "\n\n".join(paragraphs).strip()
    del current["text_lines"]
    entries.append(current)

entries = [e for e in entries if e.get("article") and e.get("text")]

target.parent.mkdir(parents=True, exist_ok=True)
with target.open("w", encoding="utf-8") as f:
    json.dump(entries, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(entries)} articles to {target}")
