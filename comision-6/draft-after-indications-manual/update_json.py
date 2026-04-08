import json
import re
import traceback

file_path = r'C:\Users\vicel\Proyectos\constitutional-proposal-tracking\comision-6\genesis-extracted\C6_GENESIS_texto-sistematizado-03-17.json'

def process():
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            if 'article' in item:
                title = item['article']
                
                # Match "Artículo 1.-", "Artículo 1 A.-", "Artículo 19. "
                match = re.search(r'Art[íi\ufffd]culo\s+(\d+(?:\s*[A-Z])?)', title)
                if match:
                    identifier = match.group(1).replace(' ', '').upper()
                    item['article_uid'] = f"C6_GEN3_ART{identifier}"
                elif '(Transitoria)' in title:
                    # Match "Primera (Transitoria)", "Primera A (Transitoria)"
                    trans_match = re.search(r'(.*?)\s*\(Transitoria\)', title)
                    if trans_match:
                        identifier = trans_match.group(1).replace(' ', '').upper()
                        # "PRIMERA" or "PRIMERAA"
                        item['article_uid'] = f"C6_GEN1_ART_TRANS_{identifier}"
                    else:
                        print(f"Warning: could not parse transitoria from {title}")
                else:
                    print(f"Warning: could not parse article_uid from {title}")
            
            # Always add/update timestamp
            item['timestamp'] = "03-17"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print("Done successfully.")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    process()
