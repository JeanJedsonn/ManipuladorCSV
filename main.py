import sys

# from baseDeDatos import Juego
from typing import Optional,List, Any
from baseDeDatos import cargarDB
from baseDeDatos import DB_Juegos,Juego
from venta import Venta, Registro
from utilidades import consolaDev
import os
import csv
# import re

# Configuración de rutas de archivos
DB_PATH = 'entrada/DB.csv'
VENDIDO_PATH = 'entrada/Vendido.csv'
CATALOGO_PATH = 'entrada/Catalogo.csv'

# Nombres de archivos de salida como se indica en el readme y la solicitud
CON_OFERTA_EN_CATALOGO_PATHS = ['salida/ConOfertaEnCatalogo.csv']
CON_OFERTA_SIN_CATALOGO_PATHS = ['salida/ConOfertaSinCatalogo.csv']
SIN_OFERTA_PATHS = ['salida/SinOferta.csv']
DESCARTADA_PATHS = ['salida/Descartada.csv']
NO_ENCONTRADOS_PATHS = ['salida/NoEncontrados.csv']
CATALOGO_PROPUESTO_PATHS = ['salida/CatalogoPropuesto.csv']


def cargaerCatalogo() -> set:
    print(f"[*] Cargando catálogo desde '{CATALOGO_PATH}'...")

    catalogo_titulos = set()
    if os.path.exists(CATALOGO_PATH):
        try:
            with open(CATALOGO_PATH, mode='r', encoding='utf-8', errors='replace') as f:
                lector = csv.DictReader(f, delimiter=";")
                for fila in lector:
                    t = fila.get('Juegos')
                    if t:
                        catalogo_titulos.add(t.strip())
            print(f"[+] Catálogo cargado correctamente ({len(catalogo_titulos)} títulos únicos).")
        except Exception as e:
            print(f"[!] Error al leer '{CATALOGO_PATH}': {e}")
            return set()
    else:
        print(f"[!] Error: El archivo '{CATALOGO_PATH}' no existe.")
        return set()
    return catalogo_titulos

def procesarVendido(BaseDeDatos: DB_Juegos, catalogo_titulos: set) -> dict[str, list[dict[str,str|int]]]:
    print(f"\n[*] Procesando juegos vendidos desde '{VENDIDO_PATH}'...")
    if not os.path.exists(VENDIDO_PATH):
        print(f"[!] Error: El archivo '{VENDIDO_PATH}' no existe.")
        return {}

    descartada_list:                list[dict[str,str|int]] = []                # Descartado: Las 4 columnas tienen valor, no es vendible
    sin_oferta_list:                list[dict[str,str|int]] = []                # Sin Oferta: Tiene alguna columna libre, pero no esta en oferta
    con_oferta_en_catalogo_list:    list[dict[str,str|int]] = []                # Con Oferta: Tiene alguna columna con precio de oferta y esta en catalogo
    con_oferta_sin_catalogo_list:   list[dict[str,str|int]] = []                # Con Oferta: Tiene alguna columna con precio de oferta pero no esta en catalogo
    no_encontrados:                 list[dict[str,str|int]] = []                # No encontrados: No se encontro coincidencia en la base de datos
    lista_total:                    list[dict[str,str|int]] = []                # Total: Todas las ventas para su revision
    ventas:                         dict[str, Venta]        = {}                # diccionario de ventas para su revision
    
    try:
        with open(VENDIDO_PATH, mode='r', encoding='utf-8', errors='replace') as f:
            lector = csv.DictReader(f, delimiter=";")

            print("[*] Procesando los juegos vendidos...")
            for fila in lector:
                # El archivo vendido tiene el título en la columna 'Juegos'

                juego: str | None = fila.get('Juegos')

                # si no tiene titulo lo saltamos
                if not juego:
                    continue

                # Extraemos las casillas requeridas
                ps4p: str | None = fila.get('PS4P')
                ps4s: str | None = fila.get('PS4S')
                ps5p: str | None = fila.get('PS5P')
                ps5s: str | None = fila.get('PS5S')

                # Una fila se descarta si las 4 columnas a la vez tienen un valor válido (no vacío ni NULL/ND/?)
                descartar_fila: bool = all(
                    fila.get(col) is not None and
                    fila.get(col) != ''
                    for col in ['PS4P', 'PS4S', 'PS5P', 'PS5S']
                )

                # Puede haber registros con múltiples juegos separados por salto de línea (\n).
                titulos = [s.strip() for s in juego.split('\n') if s.strip()]

                # buscamos cada juego del titulo en la base de datos
                for titulo in titulos:
                    id_juego = BaseDeDatos.get_id(titulo)
                    if id_juego is not None:
                        url = BaseDeDatos.get_url(id_juego)
                    else:
                        url = ""

                    # Creamos el registro de salida incluyendo ID y URL
                    registro: dict[str,str| Any] = {
                        'ID': id_juego,
                        'Titulo': titulo,
                        'PS4P': ps4p,
                        'PS4S': ps4s,
                        'PS5P': ps5p,
                        'PS5S': ps5s,
                        # url protegido por si no se encuentra el juego
                        'URL': url
                    }

                    # Clasificar en la lista respectiva

                    # 1. Las 4 columnas tienen valor
                    if descartar_fila:
                        # print("descartada")
                        descartada_list.append(registro)

                    # 2. El juego no se encuentra en la base de datos
                    elif id_juego is None:
                        # print("no encontrado")
                        no_encontrados.append(registro)

                    # 3. El juego tiene oferta ?
                    else:
                        if BaseDeDatos.tieneOferta(id_juego):
                            # Esta en catalogo
                            if juego in catalogo_titulos:
                                con_oferta_en_catalogo_list.append(registro)
                            # No esta en catalogo
                            else:
                                con_oferta_sin_catalogo_list.append(registro)
                        else:
                            # No tiene oferta
                            sin_oferta_list.append(registro)

                        # Total: Todas las ventas para su revision
                        
                        if id_juego not in ventas.keys():
                            ventas[id_juego] = Venta()          # Crea un elemento Venta
                            ventas[id_juego].set_id(id_juego)   # Asigna el id del juego
                            ventas[id_juego].set_url(url)       # Asigna la url del juego
                            ventas[id_juego].set_ps4(BaseDeDatos.get_juego(id_juego).get_ps4())       # Asigna la venta de PS4
                            ventas[id_juego].set_ps5(BaseDeDatos.get_juego(id_juego).get_ps5())       # Asigna la venta de PS5

                        registro = Registro(ps4p, ps4s, ps5p, ps5s) # Crea un registro
                        ventas[id_juego].push_registro(registro)    # Añade el registro a la venta


        print("[+] Procesamiento completado:")
        print(f"    - Con Oferta en Catálogo: {len(con_oferta_en_catalogo_list)} ventas.")
        print(f"    - Con Oferta sin Catálogo: {len(con_oferta_sin_catalogo_list)} ventas.")
        print(f"    - Sin Oferta: {len(sin_oferta_list)} ventas.")
        print(f"    - Descartadas (4 valores activos): {len(descartada_list)} ventas.")
        print(f"    - No Encontrados: {len(no_encontrados)} ventas.")
        ventas_totales: int = 0
        for venta in ventas.values():
            ventas_totales += venta.get_vendidos()
        print(f"    - Total de ventas procesadas: {ventas_totales} ventas.")
    except Exception as e:
        print(f"[!] Error al procesar '{VENDIDO_PATH}': {e}, linea 187")
        return {}

    return ({
        'con_oferta_en_catalogo': con_oferta_en_catalogo_list,
        'con_oferta_sin_catalogo': con_oferta_sin_catalogo_list,
        'sin_oferta': sin_oferta_list,
        'descartada': descartada_list,
        'no_encontrados': no_encontrados,
        'lista_total': ventas
    })

def main(valor: bool =False):
    # 1. Cargar base de datos
    BaseDeDatos: DB_Juegos = cargarDB(DB_PATH)

    # 1.5. Cargar catálogo (Catalogo.csv)
    catalogo_titulos: set = cargaerCatalogo()

    # 2. Cargar y clasificar los juegos vendidos (Vendido.csv)
    listas_juegos: dict[str, list[dict[str,str|int]]] = procesarVendido(BaseDeDatos,catalogo_titulos)

    # 3. Guardar las listas generadas en los archivos correspondientes
    fieldnames:list[str] = ['ID', 'Titulo', 'PS4P', 'PS4S', 'PS5P', 'PS5S', 'URL']

    print("\n[*] Guardando archivos de salida...")

    # Escribir archivos para "Con Oferta en Catálogo"
    for path in CON_OFERTA_EN_CATALOGO_PATHS:
        try:
            with open(path, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(listas_juegos['con_oferta_en_catalogo'])
            print(f"    [+] Archivo guardado: '{path}'")
        except Exception as e:
            print(f"    [!] Error al guardar '{path}': {e}")

    # Escribir archivos para "Con Oferta sin Catálogo"
    for path in CON_OFERTA_SIN_CATALOGO_PATHS:
        try:
            with open(path, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(listas_juegos['con_oferta_sin_catalogo'])
            print(f"    [+] Archivo guardado: '{path}'")
        except Exception as e:
            print(f"    [!] Error al guardar '{path}': {e}")

    # Escribir archivos para "Sin Oferta"
    for path in SIN_OFERTA_PATHS:
        try:
            with open(path, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(listas_juegos['sin_oferta'])
            print(f"    [+] Archivo guardado: '{path}'")
        except Exception as e:
            print(f"    [!] Error al guardar '{path}': {e}")

    # Escribir archivos para "Descartadas"
    for path in DESCARTADA_PATHS:
        try:
            with open(path, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(listas_juegos['descartada'])
            print(f"    [+] Archivo guardado: '{path}'")
        except Exception as e:
            print(f"    [!] Error al guardar '{path}': {e}")

    # Mostrar advertencias si hubo juegos no encontrados en DB.csv
    """
    if no_encontrados:
        print(f"\n[i] Advertencia: {len(no_encontrados)} juegos no se encontraron en '{DB_PATH}' y se enviaron a SinOferta:")
        for titulo in no_encontrados:
            print(f"    {titulo}")
    """
    # Escribir archivos para "No Encontrados"
    for path in NO_ENCONTRADOS_PATHS:
        try:
            with open(path, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(listas_juegos['no_encontrados'])
            print(f"    [+] Archivo guardado: '{path}'")
        except Exception as e:
            print(f"    [!] Error al guardar '{path}': {e}")

    # Escribir archivos para "Catalogo Propuesto"
    for path in CATALOGO_PROPUESTO_PATHS:
        try:
            with open(path, mode='w', encoding='utf-8', newline='') as f:
                camposCatalogo: list[str] = ['ID', 'Titulo', 'PS4', 'PS5', 'Tipo', 'Consola', 'URL', 'Venta']


                writer = csv.DictWriter(f, fieldnames=camposCatalogo)
                writer.writeheader()

                for id_juego, registro in listas_juegos['lista_total'].items():
                    tipos = registro.tipos_libres()               # Tipos de juegos que se pueden vender
                    precios = registro.calcular_precio_mediano()  # Precio mediano de los juegos vendidos
                    
                    registro_catalogo = {
                        'ID': id_juego,
                        'Titulo': BaseDeDatos.get_juego(id_juego).get_titulo(),
                        'PS4': "show" if registro.get_ps4() else "hide",                                  # Tiene version de PS4
                        'PS5': "show" if registro.get_ps5() else "hide",                                  # Tiene version de PS5
                        'Tipo': "",                                                 # Tipo de venta
                        'Consola':"",                                               # Consola del juego
                        'URL': registro.get_url(),                                                  # Url del juego
                        'Venta': ""                                                 # precio recomendado
                    }

                    if tipos["ps4p"]:
                        registro_catalogo['Tipo'] = "Primaria"
                        registro_catalogo['Consola'] = "PS4"
                        registro_catalogo['Venta'] = precios["ps4p"]
                        writer.writerow(registro_catalogo)

                    if tipos["ps5p"]:
                        registro_catalogo['Tipo'] = "Primaria"
                        registro_catalogo['Consola'] = "PS5"
                        registro_catalogo['Venta'] = precios["ps5p"]
                        writer.writerow(registro_catalogo)

                    if tipos["ps5s"]:
                        registro_catalogo['Tipo'] = "Secundaria"
                        registro_catalogo['Consola'] = "PS5"
                        registro_catalogo['Venta'] = precios["ps5s"]
                        writer.writerow(registro_catalogo)

                    if tipos["ps4s"]:
                        registro_catalogo['Tipo'] = "Secundaria"
                        registro_catalogo['Consola'] = "PS4"
                        registro_catalogo['Venta'] = precios["ps4s"]
                        writer.writerow(registro_catalogo)

            print(f"    [+] Archivo guardado: '{path}'")
        except Exception as e:
            print(f"    [!] Error al guardar '{path}': {e}")

    print("\n" + "=" * 60)
    print("  PROCESO FINALIZADO CON ÉXITO")
    print("=" * 60)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(bool(sys.argv[1]))
    else:
        main()
