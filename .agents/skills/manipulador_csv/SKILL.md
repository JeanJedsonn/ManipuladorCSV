---
name: manipulador_csv
description: Reglas y contexto para trabajar con el script ManipuladorCSV que clasifica juegos vendidos según sus ofertas y catálogo.
---

# Manipulador CSV (Procesador de Catálogos)

Este proyecto es un script en Python (`main.py`) diseñado para procesar y clasificar juegos vendidos a partir de archivos CSV.

## Flujo de Datos

**Entradas** (deben estar en la carpeta `entrada/`):
- `DB.csv`: Base de datos principal de juegos. Debe contener las columnas de precio de oferta (ej. `Precio Oferta: USA`, `Precio Oferta: Turquia`, etc.), `Titulo`, `ID` y `URL` o `Imagen`.
- `Vendido.csv`: Lista de juegos vendidos. Los nombres de los juegos están en la columna `Juegos`. Incluye columnas `PS4P`, `PS4S`, `PS5P`, `PS5S`.
- `Catalogo.csv`: Catálogo actual de juegos. Debe contener la columna `Titulo`.

**Salidas** (se generan en el directorio raíz):
- `ConOfertaEnCatalogo.csv`: Juegos vendidos que tienen oferta activa y están en el catálogo.
- `ConOfertaSinCatalogo.csv`: Juegos vendidos que tienen oferta activa pero NO están en el catálogo.
- `SinOferta.csv`: Juegos vendidos sin oferta activa o que no se encontraron en la BD.
- `Descartada.csv`: Filas donde todas las casillas `PS4P`, `PS4S`, `PS5P`, `PS5S` tienen valor válido (se descartan del resto).

## Lógica Principal
- **checarOferta(row)**: Revisa si el juego tiene alguna oferta en las regiones (USA, Turquia, India, Panama, Brasil). Si el valor no está vacío, no es '-' y no es 'N/A', se considera que tiene oferta activa.
- **Búsqueda de Títulos**: El script intenta una coincidencia exacta por título en `DB.csv` y, si falla, una coincidencia parcial. Un mismo registro de `Vendido.csv` puede tener varios juegos separados por salto de línea (`\n`).

## Instrucciones para Modificaciones
- Si se añaden nuevas regiones o tiendas, actualizar la lista `offer_cols` en la función `checarOferta`.
- Asegurarse de que los nombres de los archivos de salida se mantengan consistentes usando las constantes al inicio del archivo.
- Al manipular archivos CSV, seguir utilizando codificación `utf-8` con `errors='replace'` para soportar caracteres especiales.
