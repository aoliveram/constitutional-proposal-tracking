import json
import re
import os

def clean_status(status):
    if not status: return status
    status = status.strip()
    if not status: return status
    
    # 1. Capitalizar primero
    status = status[0].upper() + status[1:]
    
    # 2. Normalizar conectores: "similar al" -> "Similar a"
    status = re.sub(r'^[Ss]imilar al\s+', 'Similar a ', status)
    
    # 3. Formato estricto para artículos referenciados: 
    # [Tipo] a [ID].- Artículo [Número]
    pattern = r'^([Ii]d.ntico|[Ss]imilar)\s+a\s+([0-9]+)(\.-)?\s+(Art.culo\s+[^\s\.]+)[\s\.]*$'
    match = re.match(pattern, status, re.IGNORECASE)
    if match:
        orig = match.group(1).lower()
        typ = "Idéntico" if "id" in orig else "Similar"
        id_num = match.group(2)
        art_name = match.group(4)
        return f"{typ} a {id_num}.- {art_name}"
    
    # Casos simples
    if status.lower() == "eliminado": return "Eliminado"
    if status.lower() in ["idéntico", "identico"]: return "Idéntico"
    
    return status

# Buscar y procesar todos los archivos
cwd = os.getcwd()
target_files = [
    os.path.join(cwd, "playground/comision-1-data/data/C1_texto-sistematizado_enriched_manual.json"),
    os.path.join(cwd, "comision-1/draft-after-indications-manual/C1_texto-sistematizado_enriched_manual.json")
]

for file_path in target_files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for item in data:
            if 'final_status' in item:
                item['final_status'] = clean_status(item['final_status'])
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Limpiado: {file_path}")

# 2. Crear Filtro (solo para comision-1-data/data/...)
source_file = os.path.join(cwd, "playground/comision-1-data/data/C1_texto-sistematizado_enriched_manual.json")
if os.path.exists(source_file):
    with open(source_file, 'r', encoding='utf-8') as f:
        full_data = json.load(f)

    # Filtrar por estados que indican permanencia
    filtered = [
        item for item in full_data 
        if 'final_status' in item and 
        (item['final_status'].startswith("Idéntico") or item['final_status'].startswith("Similar"))
    ]

    output_file = os.path.join(cwd, "playground/comision-1-data/data/C1_borrador_final_filtered.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, indent=4, ensure_ascii=False)

    print(f"Filtrado completado. Total artículos en borrador final: {len(filtered)}")
else:
    print(f"Source file not found for filtering: {source_file}")
