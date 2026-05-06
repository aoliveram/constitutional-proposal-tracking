import json

file_path = r'C:\Users\vicel\Proyectos\constitutional-proposal-tracking\comision-4\draft-after-indications-manual\C4_historial_manual.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for i in range(53, 359):
        new_article = {
            "article_uid": f"C4_GEN_ART{i}",
            "timestamp": "03-07-1",
            "article": f"Artículo {i}",
            "text": " ",
            "sources": [
                ""
            ]
        }
        data.append(new_article)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully appended to the JSON file.")
except Exception as e:
    print(f"Error: {e}")
