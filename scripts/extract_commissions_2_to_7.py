from pathlib import Path
import json, re

# List of input files (as provided)
inputs = [
    r"c:/Users/vicel/Proyectos/constitutional-proposal-tracking/comision-2/C2_COMPLEX_BORRADOR-CONSTITUCIONAL-14-05-22.md",
    r"c:/Users/vicel/Proyectos/constitutional-proposal-tracking/comision-3/C3_BORRADOR-CONSTITUCIONAL-14-05-22.md",
    r"c:/Users/vicel/Proyectos/constitutional-proposal-tracking/comision-4/C4_BORRADOR-CONSTITUCIONAL-14-05-22.md",
    r"c:/Users/vicel/Proyectos/constitutional-proposal-tracking/comision-5/C5_BORRADOR-CONSTITUCIONAL-14-05-22.md",
    r"c:/Users/vicel/Proyectos/constitutional-proposal-tracking/comision-6/C6_BORRADOR-CONSTITUCIONAL-14-05-22.md",
    r"c:/Users/vicel/Proyectos/constitutional-proposal-tracking/comision-7/C7_BORRADOR-CONSTITUCIONAL-14-05-22.md",
]

article_re = re.compile(r"^\s*(\d+\.-\s*Artículo\s+)([^\.\-]+)", re.IGNORECASE)

for inp in inputs:
    src = Path(inp)
    if not src.exists():
        print(f"SKIP: source not found: {src}")
        continue
    # determine commission folder and target path
    com_dir = src.parent
    # output filename pattern: C{n}_BORRADOR_final.json
    m = re.search(r"comision-(\d+)", str(com_dir), re.IGNORECASE)
    if m:
        com_num = m.group(1)
    else:
        # fallback to filename prefix (C2, C3...)
        com_num = src.name.split('_')[0].lstrip('Cc')
    target_dir = com_dir / 'dataverse-final'
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"C{com_num}_BORRADOR_final.json"
    backup = target.with_name(target.stem + '_backup.json')

    text = src.read_text(encoding='utf-8')
    lines = text.splitlines()
    entries = []
    current = None

    for line in lines:
        m2 = article_re.match(line)
        if m2:
            if current is not None:
                # finalize
                paragraphs = []
                buffer = []
                for l in current['text_lines']:
                    if l.strip() == '':
                        if buffer:
                            paragraphs.append(' '.join(buffer))
                            buffer = []
                    else:
                        buffer.append(l.strip())
                if buffer:
                    paragraphs.append(' '.join(buffer))
                txt = '\n\n'.join(paragraphs).strip()
                # clean leading '.-'
                txt = re.sub(r'^\s*\.-\s*', '', txt)
                current['text'] = txt
                del current['text_lines']
                entries.append(current)
            prefix = m2.group(1).strip()
            article_id = m2.group(2).strip()
            article_id = re.sub(r'[°º]+', '', article_id).strip()
            # ensure space after 'Artículo'
            prefix = re.sub(r'(?i)Artículo\s*', 'Artículo ', prefix)
            article_field = f"{prefix}{article_id}"
            current = {'article': article_field, 'text_lines': []}
            rest = line[m2.end():].strip()
            if rest:
                current['text_lines'].append(rest)
            continue
        if current is not None:
            current['text_lines'].append(line)

    if current is not None:
        paragraphs = []
        buffer = []
        for l in current['text_lines']:
            if l.strip() == '':
                if buffer:
                    paragraphs.append(' '.join(buffer))
                    buffer = []
            else:
                buffer.append(l.strip())
        if buffer:
            paragraphs.append(' '.join(buffer))
        txt = '\n\n'.join(paragraphs).strip()
        txt = re.sub(r'^\s*\.-\s*', '', txt)
        current['text'] = txt
        del current['text_lines']
        entries.append(current)

    entries = [e for e in entries if e.get('article') and e.get('text')]

    # backup existing
    if target.exists() and not backup.exists():
        backup.write_text(target.read_text(encoding='utf-8'), encoding='utf-8')

    target.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {len(entries)} articles to {target}')
