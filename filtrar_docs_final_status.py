import json
import argparse
import os

def filter_json_file(input_file, output_file=None):
    """
    Lee un archivo JSON, filtra los objetos según los criterios dados y guarda el resultado.

    Criterios para mantener un objeto:
    1. Debe tener la clave "final_status".
    2. El valor debe comenzar con:
       - "Idéntico a "
       - "Similar a "
    """

    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_cleaned{ext}"

    print(f"Leyendo archivo: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error al leer el archivo JSON: {e}")
            return

    if not isinstance(data, list):
        print("Error: El archivo JSON debe contener una lista de objetos.")
        return

    original_count = len(data)

    # Filtrar objetos
    filtered_data = [
        item for item in data
        if (
            isinstance(item, dict)
            and "final_status" in item
            and (
                item["final_status"].startswith("Idéntico a ")
                or item["final_status"].startswith("Similar a ")
            )
        )
    ]

    filtered_count = len(filtered_data)
    removed_count = original_count - filtered_count

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=4)

    print("Proceso completado exitosamente.")
    print(f" - Objetos originales : {original_count}")
    print(f" - Objetos eliminados : {removed_count}")
    print(f" - Objetos mantenidos : {filtered_count}")
    print(f"Archivo guardado en  : {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Filtra objetos JSON manteniendo sólo aquellos cuyo 'final_status' comienza con 'Idéntico a' o 'Similar a'."
    )

    parser.add_argument(
        "input_file",
        help="Ruta al archivo JSON de entrada."
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Ruta al archivo JSON de salida.",
        default=None
    )

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: El archivo '{args.input_file}' no existe.")
    else:
        filter_json_file(args.input_file, args.output)