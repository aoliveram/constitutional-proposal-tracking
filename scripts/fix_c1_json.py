from pathlib import Path
import json, re

src = Path(r"c:/Users/vicel/Proyectos/constitutional-proposal-tracking/comision-1/dataverse-final/C1_BORRADOR_final.json")
backup = src.with_name(src.stem + '_backup.json')
if not backup.exists():
    backup.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')

data = json.loads(src.read_text(encoding='utf-8'))
count_article = 0
count_text = 0

for e in data:
    if 'article' in e:
        orig = e['article']
        # Ensure a single space after the word 'Artículo' (case-insensitive)
        new = re.sub(r'(?i)Artículo\s*', 'Artículo ', orig)
        new = re.sub(r'\s+', ' ', new).strip()
        if new != orig:
            e['article'] = new
            count_article += 1
    if 'text' in e:
        origt = e['text']
        # Remove leading ".-" and any surrounding whitespace at start
        newt = re.sub(r'^\s*\.-\s*', '', origt)
        if newt != origt:
            e['text'] = newt
            count_text += 1

src.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Fixed articles: {count_article}, cleaned texts: {count_text}')
print(f'Backup at: {backup}')
