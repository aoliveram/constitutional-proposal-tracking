import json
import os
import argparse

def select_json_keys(input_file, output_file):
    """
    Lee un archivo JSON y crea uno nuevo manteniendo únicamente
    las claves especificadas para cada objeto.
    """
    print(f"Leyendo archivo: {input_file}")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error al leer el archivo JSON: {e}")
        return
        
    if not isinstance(data, list):
        print("Error: El archivo JSON debe contener una lista de objetos en su nivel raíz.")
        return

    # Claves que queremos conservar
    keys_to_keep = {"article_uid", "article", "text", "sources", "authors","icc_id","voting_result"}
    
    filtered_data = []
    
    for item in data:
        if isinstance(item, dict):
            # Crea un nuevo diccionario solo con las claves que existen en item y están en keys_to_keep
            # Al no incluir "history", se excluyen automáticamente todos sus objetos anidados
            new_item = {key: item[key] for key in keys_to_keep if key in item}
            
            # Filtro adicional: omitir los que tengan un article_uid que comience con "C[X]_IND"
            if new_item.get("article_uid", "").startswith("C4_IND"):
                continue
                
            filtered_data.append(new_item)
            
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")
        return
        
    print(f"Proceso completado exitosamente.")
    print(f" - Total de objetos procesados : {len(filtered_data)}")
    print(f" - Archivo guardado en       : {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filtra las claves de un archivo JSON, conservando solo las indicadas.")
    parser.add_argument(
        "--input", 
        default=r"C:\Users\vicel\Proyectos\constitutional-proposal-tracking\comision-4\dataverse-final\C4_TRACK_full.json",
        help="Ruta al archivo JSON de entrada."
    )
    
    args = parser.parse_args()
    input_file = args.input
    
    # Construimos la ruta de salida en el mismo directorio del input
    base_dir = os.path.dirname(input_file)
    output_file = os.path.join(base_dir, "C4_GENESIS_master_merged.json")
    
    if not os.path.exists(input_file):
        print(f"Error: El archivo '{input_file}' no existe.")
    else:
        select_json_keys(input_file, output_file)
