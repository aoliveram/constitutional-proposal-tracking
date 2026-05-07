import json
import sys

def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        new_data = []
        for item in data:
            new_item = {}
            # Los cuatro campos solicitados al principio
            new_item["timestamp"] = item.get("timestamp", "04-08-2")
            
            target = item.get("target_article", "")
            if target:
                new_item["article"] = f"Artículo {target}"
            else:
                new_item["article"] = "Artículo "
                
            new_item["step"] = item.get("step", "Indicación")
            new_item["content_snapshot"] = item.get("content_snapshot", "")

            # Copiar el resto de las propiedades
            for k, v in item.items():
                if k not in ["timestamp", "article", "step", "content_snapshot"]:
                    new_item[k] = v
            
            new_data.append(new_item)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)

        print(f"Successfully updated {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

if __name__ == '__main__':
    # Permite pasar el archivo por línea de comandos, si no usa el predeterminado
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        target_file = r'C:\Users\vicel\Proyectos\constitutional-proposal-tracking\comision-4\indicaciones-universal-extracted\C4_VOTACION_informe-3-04-08-indicaciones.json'
    process_file(target_file)
