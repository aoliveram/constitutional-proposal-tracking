from pathlib import Path
import json, re

base = Path(r"c:/Users/vicel/Proyectos/constitutional-proposal-tracking")
updated_files = []

for i in range(1,8):
    targ = base / f"comision-{i}" / "dataverse-final" / f"C{i}_BORRADOR_final.json"
    if not targ.exists():
        continue
    backup = targ.with_name(targ.stem + '_backup2.json')
    if not backup.exists():
        backup.write_text(targ.read_text(encoding='utf-8'), encoding='utf-8')
    data = json.loads(targ.read_text(encoding='utf-8'))
    changed = 0
    for e in data:
        if 'text' in e and e['text']:
            orig = e['text']
            # remove one or more leading dots and surrounding whitespace/newlines
            new = re.sub(r'^\s*\.{1,}\s*', '', orig)
            # also remove a leading '·' bullet if present
            new = re.sub(r'^\s*·\s*', '', new)
            if new != orig:
                e['text'] = new
                changed += 1
    if changed:
        targ.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    updated_files.append((str(targ), changed, str(backup)))

for f, c, b in updated_files:
    print(f"Updated {f}: cleaned {c} entries; backup: {b}")
