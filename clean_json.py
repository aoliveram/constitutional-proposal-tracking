import json
import sys
import os

def clean_dict(d, stats):
    keys_to_delete = []
    
    # Check current level
    if "target_article" in d:
        keys_to_delete.append("target_article")
        stats['changes_made'] += 1
        
    if "authors_matched" in d:
        d["authors"] = d.pop("authors_matched")
        stats['changes_made'] += 1

    # Apply deletions
    for k in keys_to_delete:
        del d[k]
        
    # Traverse children
    for k, v in d.items():
        if isinstance(v, dict):
            clean_dict(v, stats)
        elif isinstance(v, list):
            clean_list(v, stats)

def clean_list(l, stats):
    for item in l:
        if isinstance(item, dict):
            clean_dict(item, stats)
        elif isinstance(item, list):
            clean_list(item, stats)

def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        stats = {'changes_made': 0}

        if isinstance(data, dict):
            clean_dict(data, stats)
        elif isinstance(data, list):
            clean_list(data, stats)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"\n[+] ¡Éxito! Se realizaron {stats['changes_made']} modificaciones.")
        print(f"    Archivo guardado: {os.path.basename(file_path)}\n")
    except Exception as e:
        print(f"\n[-] Error procesando {os.path.basename(file_path)}: {e}\n")

if __name__ == "__main__":
    print("-" * 50)
    print(" Herramienta de Limpieza de JSON ".center(50))
    print("-" * 50)
    
    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            if os.path.exists(path):
                process_file(path)
            else:
                print(f"[-] El archivo no existe: {path}")
    else:
        path = input("Arrastra aquí tu archivo JSON o pega su ruta y presiona Enter:\n> ").strip()
        
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        elif path.startswith("'") and path.endswith("'"):
            path = path[1:-1]
            
        if os.path.exists(path):
            process_file(path)
        else:
            print(f"\n[-] El archivo especificado no se encontró: {path}")
