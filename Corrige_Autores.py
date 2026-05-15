import json
import sys
import shutil

def get_valid_authors_mapping(data, mapping):
    """Recorre y extrae todos los autores válidos para crear un diccionario de mapeo."""
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "authors" and isinstance(v, list):
                for author in v:
                    if isinstance(author, str) and author.count(',') == 1:
                        # Extraemos "Apellido, Nombre" y lo convertimos a "Nombre Apellido"
                        parts = author.split(',')
                        apellido = parts[0].strip()
                        nombre = parts[1].strip()
                        llave = f"{nombre} {apellido}"
                        mapping[llave] = author
            else:
                get_valid_authors_mapping(v, mapping)
    elif isinstance(data, list):
        for item in data:
            get_valid_authors_mapping(item, mapping)

def fix_authors_recursive(data, mapping, changes_made):
    """Recorre y corrige los autores mal formateados basándose en el mapeo o heurísticas."""
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "authors" and isinstance(v, list):
                for i in range(len(v)):
                    author = v[i]
                    if isinstance(author, str) and author.count(',') != 1:
                        # Limpiamos espacios
                        author_clean = author.strip()
                        
                        # 1. Intentamos usar el mapeo de nombres válidos
                        if author_clean in mapping:
                            v[i] = mapping[author_clean]
                            changes_made.append((author_clean, v[i]))
                        else:
                            # 2. Heurística: asumimos que la última palabra es el apellido
                            words = author_clean.split()
                            if len(words) >= 2:
                                apellido = words[-1]
                                nombre = " ".join(words[:-1])
                                v[i] = f"{apellido}, {nombre}"
                                changes_made.append((author_clean, v[i]))
            else:
                fix_authors_recursive(v, mapping, changes_made)
    elif isinstance(data, list):
        for item in data:
            fix_authors_recursive(item, mapping, changes_made)

def fix_file(filepath):
    print(f"\nProcesando archivo: {filepath}")
    
    # Hacemos un respaldo del archivo por seguridad
    backup_path = filepath + ".backup"
    shutil.copy2(filepath, backup_path)
    print(f"  Se creó un respaldo en: {backup_path}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    mapping = {}
    get_valid_authors_mapping(data, mapping)
    
    changes_made = []
    fix_authors_recursive(data, mapping, changes_made)
    
    if changes_made:
        print(f"  Se corrigieron {len(changes_made)} autores.")
        # Mostramos algunos ejemplos de las correcciones
        unique_changes = list(set(changes_made))
        print("  Ejemplos de correcciones realizadas:")
        for old, new in unique_changes[:15]:
            print(f"    - '{old}' -> '{new}'")
        
        if len(unique_changes) > 15:
            print(f"    ... y {len(unique_changes) - 15} correcciones únicas más.")
            
        # Guardamos los cambios
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("  ¡Archivo actualizado exitosamente!")
    else:
        print("  No se encontraron autores que requirieran corrección.")

def main():
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        fix_file(filepath)
    else:
        print("Por favor, especifica el archivo a corregir.")

if __name__ == "__main__":
    main()
