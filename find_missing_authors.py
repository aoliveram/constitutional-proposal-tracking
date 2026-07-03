import os
import json
import argparse
import csv

def has_content(val):
    """Verifica si un valor tiene contenido real (no está vacío, ni nulo)."""
    if val is None:
        return False
    if isinstance(val, str) and val.strip() == "":
        return False
    if isinstance(val, list) and len(val) == 0:
        return False
    if isinstance(val, dict) and len(val) == 0:
        return False
    return True

def check_missing_authors(filepath):
    """Revisa un archivo JSON buscando objetos con fuente/número pero sin autores."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error al leer {filepath}: {e}")
        return []

    # Si no es una lista en la raíz, lo envolvemos para poder iterarlo
    if not isinstance(data, list):
        data = [data]

    issues = []

    def check_object(obj, context=""):
        if not isinstance(obj, dict):
            return

        # Vemos si tiene al menos uno de los identificadores de fuente
        has_source = has_content(obj.get('source')) or has_content(obj.get('sources')) or has_content(obj.get('number'))
        
        # Vemos si tiene autores definidos
        has_authors = has_content(obj.get('authors'))

        if has_source and not has_authors:
            # Determinamos cuál fue el origen que encontramos para mostrarlo
            if has_content(obj.get('number')):
                source_val = f"number: {obj.get('number')}"
            elif has_content(obj.get('sources')):
                source_val = f"sources: {obj.get('sources')}"
            else:
                source_val = f"source: {obj.get('source')}"

            # Identificador del artículo o indicación
            uid = obj.get('article_uid', obj.get('article', 'Desconocido'))
            
            issues.append({
                'context': context,
                'uid': uid,
                'source_val': source_val
            })

        # Buscamos anidadamente en "history" si existe
        if 'history' in obj and isinstance(obj['history'], list):
            for i, hist_obj in enumerate(obj['history']):
                parent_uid = obj.get('article_uid', obj.get('article', 'Desconocido'))
                check_object(hist_obj, f"history[{i}] de {parent_uid}")

    for item in data:
        check_object(item, "Raíz")
        
    return issues

def main():
    parser = argparse.ArgumentParser(description="Buscar objetos con source/sources/number pero sin authors.")
    parser.add_argument("--path", type=str, nargs='+', default=["."], help="Ruta de los directorios o archivos JSON.")
    parser.add_argument("--out", type=str, default="reporte_autores_faltantes.csv", help="Archivo CSV de salida.")
    args = parser.parse_args()

    csv_file_path = os.path.abspath(args.out)
    all_issues = []

    for path in args.path:
        base_path = os.path.abspath(path)
        if os.path.isfile(base_path) and base_path.endswith('.json'):
            print(f"Revisando archivo único: {base_path}")
            issues = check_missing_authors(base_path)
            for issue in issues:
                issue['file'] = base_path
            all_issues.extend(issues)
        elif os.path.isdir(base_path):
            print(f"Buscando en directorio: {base_path}")
            for root, dirs, files in os.walk(base_path):
                if '.git' in root or '.venv' in root or 'node_modules' in root:
                    continue
                for file in files:
                    if file.endswith('.json'):
                        filepath = os.path.join(root, file)
                        issues = check_missing_authors(filepath)
                        for issue in issues:
                            issue['file'] = filepath
                        all_issues.extend(issues)
        else:
            print(f"La ruta proporcionada no es un archivo .json ni un directorio válido: {base_path}")

    # Guardar en CSV
    if all_issues:
        with open(csv_file_path, 'w', encoding='utf-8', newline='') as csvfile:
            fieldnames = ['file', 'context', 'uid', 'source_val']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for issue in all_issues:
                writer.writerow(issue)
        print(f"\nSe encontraron {len(all_issues)} problemas en total.")
        print(f"Reporte generado con éxito en: {csv_file_path}")
    else:
        print("\nNo se encontraron problemas.")

if __name__ == "__main__":
    main()
