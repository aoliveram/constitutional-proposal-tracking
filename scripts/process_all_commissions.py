import os
import json
import re

commissions = [1, 3, 5, 6, 7]
base_dir = "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking"

def clean_status(status):
    if not status:
        return ""
    status = status.strip()
    status_lower = status.lower()
    
    # Manejar "No encontrado"
    if "no se encuentra" in status_lower or "no encontrado" in status_lower:
        return "No encontrado"
        
    # Manejar "Eliminado"
    if "eliminado" in status_lower:
        return "Eliminado"
        
    # Manejar Idéntico a / Similar a (preservando el resto intacto)
    match = re.match(r'^([ií]d.ntico|similar)\s+(?:al?\s+)?(.+)$', status, re.IGNORECASE)
    if match:
        prefix = match.group(1).lower()
        target = match.group(2).strip()
        
        # Limpiar espacios dobles
        target = re.sub(r'\s+', ' ', target)
        # Limpiar punto final si existe aislado (ej: "Artículo 3°.-" -> no lo tocaremos por seguridad a menos que termine en ".-" al final del todo, lo dejamos intacto para preservar cosas como "D.")
        target = re.sub(r'[\.\s]+$', '', target)
        
        if "id" in prefix:
            return f"Idéntico a {target}"
        else:
            return f"Similar a {target}"
            
    # Casos donde dice "Idéntico" o "Similar" sin número (solitarios)
    if status_lower in ["idéntico", "identico"]:
        return "Idéntico"
    if status_lower == "similar":
        return "Similar"
        
    # Fallback genérico capitalizado
    return status[0].upper() + status[1:] if status else ""

def get_target(status):
    if status.startswith("Idéntico a "):
        return status.replace("Idéntico a ", "").strip()
    if status.startswith("Similar a "):
        return status.replace("Similar a ", "").strip()
    return None

for c in commissions:
    folder = f"comision-{c}"
    input_file = os.path.join(base_dir, folder, "draft-after-indications-manual", f"C{c}_historial_manual.json")
    
    # Manejo de ruta especial para C1 si no está en la estándar
    if c == 1 and not os.path.exists(input_file):
        alt_path = os.path.join(base_dir, "playground", "comision-1-data", "data", "C1_historial_manual.json")
        if os.path.exists(alt_path):
            input_file = alt_path
            
    if not os.path.exists(input_file):
        print(f"Archivo no encontrado para Comisión {c}: {input_file}")
        continue
        
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # 1. Armonización
    for item in data:
        if "final_status" in item and item["final_status"]:
            item["final_status"] = clean_status(item["final_status"])
            
    # Guardar los cambios armonizados
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    # 2. Filtrado y conteo
    filtered_data = []
    stats = {"Idéntico": 0, "Similar": 0, "No encontrado": 0, "Eliminado": 0}
    matrix = {}
    no_target_list = []
    
    for item in data:
        status = item.get("final_status", "")
        # Extraer sources. Si no hay, fall back al article_uid
        sources = item.get("sources", [])
        if not sources:
            sources = [item.get("article_uid", "N/A")]
            
        if status.startswith("Idéntico"):
            stats["Idéntico"] += 1
            filtered_data.append(item)
            target = get_target(status)
            if target:
                if target not in matrix:
                    matrix[target] = {"Idéntico": [], "Similar": [], "No encontrado": []}
                matrix[target]["Idéntico"].extend(sources)
            else:
                no_target_list.extend([(src, "Idéntico") for src in sources])
                
        elif status.startswith("Similar"):
            stats["Similar"] += 1
            filtered_data.append(item)
            target = get_target(status)
            if target:
                if target not in matrix:
                    matrix[target] = {"Idéntico": [], "Similar": [], "No encontrado": []}
                matrix[target]["Similar"].extend(sources)
            else:
                 no_target_list.extend([(src, "Similar") for src in sources])
                
        elif status == "No encontrado":
            stats["No encontrado"] += 1
            filtered_data.append(item)
            no_target_list.extend([(src, "No encontrado") for src in sources])
            
        elif status == "Eliminado":
            stats["Eliminado"] += 1
            
    # 3. Crear directorios comision-#/comision-#-final
    out_dir = os.path.join(base_dir, folder, f"comision-{c}-final")
    os.makedirs(out_dir, exist_ok=True)
    
    # 4. Guardar JSON filtrado
    out_json = os.path.join(out_dir, f"C{c}_borrador_final_filtered.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, indent=4, ensure_ascii=False)
        
    # 5. Generar Reporte Textual con Tablas Markdown
    out_txt = os.path.join(out_dir, f"C{c}_resumen_borrador.txt")
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(f"# RESUMEN BORRADOR FINAL - COMISIÓN {c}\n\n")
        
        f.write("## TABLA 1: RESUMEN GENERAL\n\n")
        f.write("| Métrica | Cantidad |\n")
        f.write("| :--- | :--- |\n")
        f.write(f"| Total de Artículos Únicos en el Borrador Final | {len(matrix)} |\n")
        f.write(f"| Total de Propuestas 'Idéntico' | {stats['Idéntico']} |\n")
        f.write(f"| Total de Propuestas 'Similar' | {stats['Similar']} |\n")
        f.write(f"| Total de Propuestas 'No encontrado' | {stats['No encontrado']} |\n")
        f.write(f"| Total de Propuestas 'Eliminado' | {stats['Eliminado']} |\n\n\n")
        
        f.write("## TABLA 2: MATRIZ DE TRAZABILIDAD (SOURCES POR ARTICULO FINAL)\n\n")
        f.write("| Artículo Final Destino | Idéntico (Sources) | Similar (Sources) | No encontrado (Sources) |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        
        for target in sorted(matrix.keys()):
            id_sources = ", ".join(matrix[target]["Idéntico"]) if matrix[target]["Idéntico"] else "-"
            sim_sources = ", ".join(matrix[target]["Similar"]) if matrix[target]["Similar"] else "-"
            no_sources = "-"
            f.write(f"| **{target}** | {id_sources} | {sim_sources} | {no_sources} |\n")
            
        if no_target_list:
            id_sources_list = [s[0] for s in no_target_list if s[1] == "Idéntico"]
            sim_sources_list = [s[0] for s in no_target_list if s[1] == "Similar"]
            no_found_list = [s[0] for s in no_target_list if s[1] == "No encontrado"]
            
            id_sources = ", ".join(id_sources_list) if id_sources_list else "-"
            sim_sources = ", ".join(sim_sources_list) if sim_sources_list else "-"
            no_sources = ", ".join(no_found_list) if no_found_list else "-"
            
            f.write(f"| **[Sin Artículo Destino]** | {id_sources} | {sim_sources} | {no_sources} |\n")
            
    print(f"✅ Procesada Comisión {c}")

print("¡Ejecución completa!")
