import json
import os
import argparse

def fix_article_uids(filepath):
    """
    Reads a JSON file, replaces '-' with '_' in 'article_uid' values,
    and writes the changes back to the file if any modifications were made.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        changed = False
        
        # Check if the JSON is a list of objects
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'article_uid' in item:
                    old_uid = item['article_uid']
                    if isinstance(old_uid, str) and '-' in old_uid:
                        item['article_uid'] = old_uid.replace('-', '_')
                        changed = True
        # Check if the JSON is a single object
        elif isinstance(data, dict):
            if 'article_uid' in data:
                old_uid = data['article_uid']
                if isinstance(old_uid, str) and '-' in old_uid:
                    data['article_uid'] = old_uid.replace('-', '_')
                    changed = True
                    
        if changed:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Modificado: {filepath}")
            
    except json.JSONDecodeError:
        print(f"Error al leer JSON (puede estar corrupto o vacío): {filepath}")
    except Exception as e:
        print(f"Error al procesar {filepath}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Reemplazar guiones por guiones bajos en article_uid de archivos JSON.")
    parser.add_argument(
        '--path', 
        type=str, 
        default=".", 
        help="Ruta del directorio donde buscar los archivos JSON."
    )
    args = parser.parse_args()

    base_path = os.path.abspath(args.path)
    
    if os.path.isfile(base_path) and base_path.endswith('.json'):
        print(f"Procesando archivo único: {base_path}")
        fix_article_uids(base_path)
    elif os.path.isdir(base_path):
        print(f"Buscando archivos JSON en el directorio: {base_path}")
        for root, dirs, files in os.walk(base_path):
            # Ignorar directorios que normalmente no queremos tocar
            if '.git' in root or '.venv' in root or 'node_modules' in root:
                continue
            
            for file in files:
                if file.endswith('.json'):
                    filepath = os.path.join(root, file)
                    fix_article_uids(filepath)
    else:
        print(f"La ruta proporcionada no es un archivo .json ni un directorio válido: {base_path}")

if __name__ == "__main__":
    main()
