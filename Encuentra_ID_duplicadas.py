import json
import sys
import collections
from pathlib import Path

def find_duplicate_uids(filepath):
    print(f"\nRevisando el archivo: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not isinstance(data, list):
            print("  El archivo JSON no contiene una lista de objetos en la raíz.")
            return

        uids = []
        for index, item in enumerate(data):
            if isinstance(item, dict):
                uid = item.get("article_uid")
                if uid:
                    uids.append(uid)
                else:
                    print(f"  Advertencia: El objeto en el índice {index} no tiene 'article_uid'")
            else:
                print(f"  Advertencia: El elemento en el índice {index} no es un objeto/diccionario.")

        uid_counts = collections.Counter(uids)
        duplicates = {uid: count for uid, count in uid_counts.items() if count > 1}

        if duplicates:
            print(f"  ¡Se encontraron {len(duplicates)} IDs repetidas!")
            for uid, count in duplicates.items():
                print(f"  - '{uid}' aparece {count} veces.")
        else:
            print("  No se encontraron IDs repetidas.")

    except FileNotFoundError:
        print("  Error: No se encontró el archivo.")
    except json.JSONDecodeError:
        print("  Error: El archivo no es un JSON válido.")
    except Exception as e:
        print(f"  Error inesperado: {e}")

def main():
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        # Por defecto revisa los archivos en la carpeta actual
        files = list(Path('.').glob('*.json'))
        if not files:
            print("No se especificaron archivos y no se encontraron archivos JSON en el directorio actual.")
            return

    for file in files:
        find_duplicate_uids(file)

if __name__ == "__main__":
    main()
