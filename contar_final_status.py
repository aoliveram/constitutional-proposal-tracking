Python 3.13.0 (tags/v3.13.0:60403a5, Oct  7 2024, 09:38:07) [MSC v.1941 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
import json
import os
import unicodedata
from collections import Counter
import pandas as pd


CARPETA_JSON = "json_originales"


def normalizar_texto(texto):
    """
    Convierte el texto a minúsculas y elimina tildes.
    Ejemplo: 'Idéntico' -> 'identico'
    """
    if not isinstance(texto, str):
        return ""

    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caracter for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )
    return texto


def clasificar_final_status(valor):
    """
    Clasifica final_status según el inicio del texto.
    """
    texto = normalizar_texto(valor)

    if texto.startswith("identico"):
        return "Idéntico"
    elif texto.startswith("similar"):
        return "Similar"
    elif texto.startswith("eliminado"):
        return "Eliminado"
    elif texto.startswith("art-fallido"):
        return "ART-FALLIDO"
    elif texto.startswith("no se encuentra"):
        return "No se encuentra en el borrador final"
    elif texto == "":
        return "Sin final_status"
    else:
        return "Otro"


def obtener_articulos(datos):
    """
    En tu estructura, los artículos son los objetos de la lista raíz
    que tienen la clave 'article_uid'.

    Los objetos con 'titleuid' son títulos, por tanto no se cuentan
    como artículos.
    """
    if not isinstance(datos, list):
        raise ValueError("El JSON no tiene una lista como estructura raíz.")

    articulos = [
        objeto for objeto in datos
        if isinstance(objeto, dict) and "article_uid" in objeto
    ]

    return articulos


resultados = []
otros_detectados = []

for nombre_archivo in os.listdir(CARPETA_JSON):
    if nombre_archivo.endswith(".json"):
        ruta = os.path.join(CARPETA_JSON, nombre_archivo)

        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        articulos = obtener_articulos(datos)

        conteo = Counter()

        for articulo in articulos:
            if "final_status" in articulo:
                categoria = clasificar_final_status(articulo["final_status"])
            else:
                categoria = "Sin final_status"

            conteo[categoria] += 1

            if categoria == "Otro":
                otros_detectados.append({
                    "archivo": nombre_archivo,
                    "article_uid": articulo.get("article_uid", ""),
...                     "article": articulo.get("article", ""),
...                     "final_status": articulo.get("final_status", "")
...                 })
... 
...         resultados.append({
...             "archivo": nombre_archivo,
...             "total_articulos": len(articulos),
...             "idéntico": conteo.get("Idéntico", 0),
...             "similar": conteo.get("Similar", 0),
...             "eliminado": conteo.get("Eliminado", 0),
...             "no_se_encuentra": conteo.get("No se encuentra en el borrador final", 0),
...             "art_fallido": conteo.get("ART-FALLIDO", 0),
...             "sin_final_status": conteo.get("Sin final_status", 0),
...             "otro": conteo.get("Otro", 0)
...         })
... 
... 
... df = pd.DataFrame(resultados)
... 
... print("\nResumen por archivo:")
... print(df)
... 
... df.to_csv(
...     "conteo_final_status_por_json.csv",
...     index=False,
...     encoding="utf-8-sig"
... )
... 
... if otros_detectados:
...     df_otros = pd.DataFrame(otros_detectados)
...     df_otros.to_csv(
...         "final_status_otros_detectados.csv",
...         index=False,
...         encoding="utf-8-sig"
...     )
...     print("\nSe detectaron valores clasificados como 'Otro'.")
...     print("Revisa el archivo final_status_otros_detectados.csv")
... 
