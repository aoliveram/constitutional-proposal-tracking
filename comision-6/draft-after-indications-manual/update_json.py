import json
import re
import traceback
import unicodedata

file_path = r'C:\Users\vicel\Proyectos\constitutional-proposal-tracking\comision-2\draft-after-indications-manual\C2_historial_manual.json'

def normalize_text(s):
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\u00a0", " ")
    return s.strip()

def clean_identifier(identifier):
    identifier = identifier.strip().upper()
    identifier = re.sub(r'\s+', '', identifier)
    identifier = identifier.replace('.', '_')
    return identifier

def parse_article_uid(title):
    title = normalize_text(title)

    # Acepta:
    # Artículo 63
    # ARTÍCULO XX1
    # Art. 1
    # Art 1.2
    # Art 2.1
    article_match = re.match(
        r'^\s*(?:ART[ÍIÌÏ]CULO|ART[IÍ]CULO|ART\.?|Art[íi]culo|art[íi]culo|art\.?)\s+([A-Z0-9]+(?:\.[A-Z0-9]+)*)',
        title,
        flags=re.IGNORECASE
    )
    if article_match:
        identifier = clean_identifier(article_match.group(1))
        return f"C2_GEN_ART{identifier}"

    # Acepta transitorias
    trans_match = re.match(
        r'^\s*(.*?)\s*\((?:Transitoria)\)\s*$',
        title,
        flags=re.IGNORECASE
    )
    if trans_match:
        identifier = clean_identifier(trans_match.group(1))
        return f"C2_GEN_ART_TRANS_{identifier}"

    return None

def process():
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            title = item.get('article')
            if title:
                uid = parse_article_uid(title)
                if uid:
                    item['article_uid'] = uid
                else:
                    print(f"Warning: could not parse article_uid from {repr(title)}")

            item['timestamp'] = "02-16"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("Done successfully.")

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    process()