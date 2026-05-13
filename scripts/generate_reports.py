import os
import subprocess

commissions = [1, 3, 5, 6, 7]
base_dir = "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking"

for c in commissions:
    txt_file = os.path.join(base_dir, f"comision-{c}", f"comision-{c}-final", f"C{c}_resumen_borrador.txt")
    if not os.path.exists(txt_file):
        continue
        
    with open(txt_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    lines = content.split('\n')
    metrics = {}
    for line in lines:
        if "|" in line and "Total" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) == 2 and parts[1].isdigit():
                metrics[parts[0]] = int(parts[1])
                
    total_unicos = metrics.get("Total de Artículos Únicos en el Borrador Final", 0)
    identicos = metrics.get("Total de Propuestas 'Idéntico'", 0)
    similares = metrics.get("Total de Propuestas 'Similar'", 0)
    no_encontrados = metrics.get("Total de Propuestas 'No encontrado'", 0)
    eliminados = metrics.get("Total de Propuestas 'Eliminado'", 0)
    
    total_propuestas = identicos + similares + no_encontrados + eliminados
    sobrevivientes = identicos + similares
    survival_rate = round((sobrevivientes / total_propuestas) * 100, 1) if total_propuestas > 0 else 0
    
    # Remover el titulo grande del txt para evitar duplicados en el reporte
    content_clean = "\n".join(lines[2:])
    
    md_content = f"""---
title: "Reporte de Trazabilidad: Comisión {c}"
author: Análisis Automático
date: \\today
geometry: margin=2cm
---

# Introducción

Este documento presenta un análisis cuantitativo de la trazabilidad de las iniciativas en la **Comisión {c}**. El objetivo de este reporte es entender el nivel de supervivencia de las propuestas originales después del proceso de indicaciones, mostrando qué proporción logró formar parte del borrador final.

# Resumen Analítico

En esta comisión, se analizaron un total de **{total_propuestas} propuestas** vinculadas al borrador. El destino de estas propuestas se desglosa de la siguiente manera:

- **{sobrevivientes} propuestas** ({survival_rate}%) lograron sobrevivir hasta el borrador final, contribuyendo a la redacción de **{total_unicos} artículos únicos**.
- De las que sobrevivieron, **{identicos}** se mantuvieron idénticas o con cambios mínimos, mientras que **{similares}** fueron catalogadas como similares, implicando fusiones o modificaciones sustanciales.
- **{eliminados} propuestas** fueron eliminadas explícitamente durante el proceso.
- **{no_encontrados} propuestas** no se encuentran en el borrador final (sin destino o rastro evidente).

Este grado de síntesis refleja cómo el debate y las votaciones condensaron {sobrevivientes} iniciativas en solo {total_unicos} artículos constitucionales finales.

# Tablas de Datos

A continuación se presentan las métricas extraídas directamente del flujo de trabajo, seguidas de la matriz de trazabilidad que conecta cada artículo final con sus propuestas originales (identificadas por su ID de `source`).

{content_clean}

"""
    md_file = os.path.join(base_dir, f"comision-{c}", f"comision-{c}-final", f"C{c}_reporte_completo.md")
    pdf_file = os.path.join(base_dir, f"comision-{c}", f"comision-{c}-final", f"C{c}_reporte_completo.pdf")
    
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"Compilando PDF para Comisión {c}...")
    try:
        subprocess.run(["/opt/homebrew/bin/pandoc", md_file, "-o", pdf_file, "--pdf-engine=/Library/TeX/texbin/pdflatex"], check=True)
        print(f"Generado {pdf_file}")
    except Exception as e:
        print(f"Error compilando {md_file}: {e}")

print("Generación finalizada.")
