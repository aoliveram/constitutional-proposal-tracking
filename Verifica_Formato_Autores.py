import json
import sys
from pathlib import Path

def find_authors_recursive(data, authors_list, path="root"):
    """
    Busca recursivamente la clave 'authors' en diccionarios y listas,
    almacenando los autores encontrados junto con su ruta para facilitar su ubicación.
    """
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "authors" and isinstance(v, list):
                for idx, author in enumerate(v):
                    if isinstance(author, str):
                        authors_list.append((author, f"{path} -> authors[{idx}]"))
                    else:
                        # Por si hay algún autor que no sea un string (ej. null o un objeto)
                        authors_list.append((str(author), f"{path} -> authors[{idx}] (No es texto)"))
            else:
                find_authors_recursive(v, authors_list, f"{path} -> {k}")
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            find_authors_recursive(item, authors_list, f"{path}[{idx}]")

def check_author_format(filepath):
    print(f"\nRevisando el archivo: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        authors_found = []
        find_authors_recursive(data, authors_found)
        
        malformed_authors = []
        for author, path in authors_found:
            # Si el autor no es un string (esto lo capturamos arriba), ya está mal.
            if "(No es texto)" in path:
                malformed_authors.append((author, path, "El valor no es texto"))
                continue

            # Verificamos que tenga exactamente una coma para separar "Apellido, Nombre"
            parts = author.split(',')
            
            if len(parts) != 2:
                malformed_authors.append((author, path, "No tiene el formato 'Apellido, Nombre' (falta o sobra coma)"))
            else:
                apellido, nombre = parts[0].strip(), parts[1].strip()
                if not apellido or not nombre:
                    malformed_authors.append((author, path, "Falta el apellido o el nombre alrededor de la coma"))

        if malformed_authors:
            print(f"  ¡Se encontraron {len(malformed_authors)} autores con formato sospechoso/incorrecto!")
            # Mostrar solo los primeros 20 para no saturar la consola, si hay muchos
            for author, path, reason in malformed_authors[:20]:
                print(f"  - '{author}' en {path} | Motivo: {reason}")
            
            if len(malformed_authors) > 20:
                print(f"  ... y {len(malformed_authors) - 20} más.")
        else:
            print("  Todos los autores revisados tienen el formato correcto ('Apellido, Nombre').")

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
        files = list(Path('.').glob('**/*.json'))
        if not files:
            print("No se especificaron archivos.")
            return

    for file in files:
        check_author_format(file)

if __name__ == "__main__":
    main()
