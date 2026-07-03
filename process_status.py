import json
import collections
import os

file_path = r"C:\Users\vicel\Proyectos\constitutional-proposal-tracking\comision-7\dataverse-final\C7_TRACK_full.json"

def main():
    # Cargar el JSON
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    status_counts = collections.Counter()
    anomalies = []
    missing_count = 0

    # Procesar cada elemento
    for i, item in enumerate(data):
        # Identificamos si es un artículo (tiene 'article' o 'article_uid')
        es_articulo = "article_uid" in item or "article" in item
        
        # Solo a los artículos sin final_status se les añade ART-FALLIDO
        if es_articulo and "final_status" not in item:
            item["final_status"] = "ART-FALLIDO"
            missing_count += 1
        
        # Si tiene final_status (o recién se le añadió) lo contabilizamos
        if "final_status" in item:
            status = item["final_status"]
            status_counts[status] += 1
            
            # Verificar si es una anomalía
            # Consideramos que lo normal es que empiece con estas palabras (respetando mayúsculas)
            if not (status.startswith("Similar a") or 
                    status.startswith("Idéntico a") or 
                    status.startswith("Eliminado") or 
                    status == "ART-FALLIDO"):
                
                identifier = item.get("article_uid", item.get("titleuid", f"Índice {i}"))
                anomalies.append({"id": identifier, "status": status})

    # Guardar el JSON actualizado sobre el mismo archivo
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # Imprimir resultados por consola
    print("=" * 50)
    print("REPORTE DE PROCESAMIENTO DE FINAL_STATUS")
    print("=" * 50)
    print(f"Artículos a los que se les añadió 'ART-FALLIDO': {missing_count}\n")
    
    print("--- CONTEO GENERAL POR CATEGORÍA ---")
    category_counts = {
        "Similar a...": 0, 
        "Idéntico a...": 0, 
        "Eliminado": 0, 
        "ART-FALLIDO": 0, 
        "Anomalías": 0
    }
    
    for status, count in status_counts.items():
        if status.startswith("Similar a"):
            category_counts["Similar a..."] += count
        elif status.startswith("Idéntico a"):
            category_counts["Idéntico a..."] += count
        elif status.startswith("Eliminado"):
            category_counts["Eliminado"] += count
        elif status == "ART-FALLIDO":
            category_counts["ART-FALLIDO"] += count
        else:
            category_counts["Anomalías"] += count

    for cat, count in category_counts.items():
        print(f"{cat}: {count}")

    print("\n--- DETALLE DE ANOMALÍAS ENCONTRADAS ---")
    if anomalies:
        for anomaly in anomalies:
            print(f"- ID: {anomaly['id']} | Status: '{anomaly['status']}'")
    else:
        print("No se encontraron anomalías.")

    print("\n--- CONTEO EXACTO DE TODOS LOS FINAL_STATUS ---")
    for status, count in status_counts.most_common():
        print(f"{count}x : {status}")

if __name__ == '__main__':
    main()
