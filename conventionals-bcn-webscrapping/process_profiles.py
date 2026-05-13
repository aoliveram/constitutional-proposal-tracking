import json
import os
from datetime import datetime

raw_path = "conventional-profiles-raw.json"
out_path = "conventional-profiles.json"

if not os.path.exists(raw_path):
    print(f"Error: {raw_path} not found.")
    exit(1)

with open(raw_path, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

processed_data = []

def calc_age(birth_str, ref_date_str="2021-07-04"):
    try:
        birth = datetime.strptime(birth_str, "%Y-%m-%d")
        ref = datetime.strptime(ref_date_str, "%Y-%m-%d")
        age = ref.year - birth.year - ((ref.month, ref.day) < (birth.month, birth.day))
        return age
    except:
        return None

for c in raw_data:
    # 1. Nombre Armonizado
    nombre = c.get("nombre_original_json", "")
    
    # 2. Afiliacion agrupada
    afiliacion = c.get("afiliacion_politica", "")
    if not afiliacion:
        trayectoria = str(c.get("trayectoria_politica_y_publica", ""))
        if "Independiente" in trayectoria:
            afiliacion = "Independiente"
        elif "Partido Comunista" in trayectoria:
            afiliacion = "Partido Comunista de Chile"
        else:
            afiliacion = "Desconocida"
            
    # 3. Distrito
    distrito = c.get("distrito", "Desconocido")
    if not distrito:
        distrito = "Desconocido"
        
    # 4. Es_abogado
    es_abogado = 0
    prof = str(c.get("profesion", "")).lower()
    if "abogad" in prof:
        es_abogado = 1
        
    # 5. Edad al asumir
    edad = calc_age(c.get("fecha_nacimiento", ""))
    
    # 6. Grado Académico (Ordinal)
    grado = str(c.get("grado_academico", "")).lower()
    grado_num = 0
    if "doctor" in grado or "phd" in grado:
        grado_num = 2
    elif "mag" in grado or "master" in grado:
        grado_num = 1
        
    # 7. Experiencia previa
    exp = 0
    tray_lower = str(c.get("trayectoria_politica_y_publica", "")).lower()
    keywords = ["diputad", "senador", "alcalde", "alcaldesa", "concejal", "seremi", "intendente", "ministerio", "ministro", "ministra", "gobernador", "subsecretari", "embajador"]
    if any(k in tray_lower for k in keywords):
        exp = 1
        
    # 8. Es_mujer
    es_mujer = 0
    bio_text = str(c.get("familia_y_juventud", "")).lower() + " " + str(c.get("intro_wiki", "")).lower()
    first_name = nombre.split(", ")[1].split(" ")[0].lower() if ", " in nombre else nombre.split(" ")[0].lower()
    if " hija " in bio_text or "nacida" in bio_text or "casada" in bio_text or first_name.endswith("a"):
        es_mujer = 1

    processed_data.append({
        "nombre_armonizado": nombre,
        "es_mujer": es_mujer,
        "afiliacion_agrupada": afiliacion,
        "distrito": distrito,
        "es_abogado": es_abogado,
        "edad_al_asumir": edad,
        "grado_academico_nivel": grado_num,
        "experiencia_previa_institucional": exp
    })

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(processed_data, f, ensure_ascii=False, indent=4)

print(f"Successfully generated {out_path} with {len(processed_data)} profiles.")
