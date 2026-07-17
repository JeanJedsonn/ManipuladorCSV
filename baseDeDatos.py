import os
import csv
from typing import Dict, Optional

# Objeto con la forma de un juego
class Juego:
    def __init__(self, id: int, titulo: str, url: str = "", oferta: dict[str,str] = {}, original: dict[str,str] = {}) -> None:
        self.id:         int = id
        self.titulo:     str = titulo
        self.url:        str = url
        self.oferta:     dict[str,str] = oferta
        self.original:   dict[str,str] = original

    def get_id(self) -> int:
        return self.id

    def get_titulo(self) -> str:
        return self.titulo

    def get_url(self) -> str:
        return self.url

    def get_oferta(self,) -> Optional[dict]:
        return self.oferta

    def get_original(self) -> Optional[dict]:
        return self.original

    def tieneOferta(self) -> bool:
        sol: bool = False
        for oferta in self.oferta.values():
            if oferta != "-" and oferta != "" and oferta != "N/D":
                sol = True
                break
        return sol

# Clase que almacena la base de datos
class DB_Juegos:
    def __init__(self) -> None:
        self.diccionario_juegos: Dict[int, Juego] = {}                                # ID -> Juego
        self.indice_titulos:     Dict[str, int]   = {}                                # Titulo -> ID

    # agrega un juego a la base de datos
    def set_juego(self, id: int, titulo: str, url: str = "", oferta: dict[str,str] = {}, original: dict[str,str] = {}) -> None:
        self.diccionario_juegos[id] = Juego(id, titulo, url, oferta, original)
        self.indice_titulos[titulo.lower().strip()] = id

    def get_juego(self,id: int) -> Optional[Juego]:
        return self.diccionario_juegos[id]

    # devuelve el id de un titulo, si no existe devuelve None
    def get_id(self, titulo: str) -> Optional[int]:
        return self.indice_titulos.get(titulo.lower().strip())

    # devuelve el titulo de un id, si no existe devuelve None
    def get_titulo(self,id: int) -> Optional[str]:
        return self.diccionario_juegos[id].get_titulo()

    # devuelve la url de un id, si no existe devuelve None
    def get_url(self,id: int) -> Optional[str]:
        return self.diccionario_juegos[id].get_url()

    # devuelve el precio de oferta de un id, si no existe devuelve None
    def get_oferta(self,id: int) -> Optional[dict]:
        return self.diccionario_juegos[id].get_oferta()

    # devuelve el precio original de un id, si no existe devuelve None
    def get_original(self,id: int) -> Optional[dict]:
        return self.diccionario_juegos[id].get_original()

    def tieneOferta(self,id: int) -> bool:
        return self.diccionario_juegos[id].tieneOferta()


def cargarDB(DB_PATH) -> DB_Juegos:
    BaseDeDatos = DB_Juegos()

    print("=" * 60)
    print("  PROCESADOR DE CATÁLOGOS - GENERADOR DE LISTAS DE OFERTAS")
    print("=" * 60)

    # 1. Cargar la base de datos de juegos (DB.csv)
    print(f"[*] Cargando base de datos desde '{DB_PATH}'...")
    if not os.path.exists(DB_PATH):
        print(f"[!] Error: El archivo '{DB_PATH}' no existe.")
        return DB_Juegos()

    try:
        with open(DB_PATH, mode='r', encoding='utf-8', errors='replace') as f:

            # leer todos los titulos de DB.csv
            lector = csv.DictReader(f, delimiter=";")
            print(lector.fieldnames)
            for fila in lector:
                titulo = fila.get('Titulo')

                # preparamos el diccionario de oferta
                original = {
                    'USA': fila.get('Precio Original: USA'),
                    'TUR': fila.get('Precio Original: Turquia'),
                    'IND': fila.get('Precio Original: India'),
                    'PAN': fila.get('Precio Original: Panama'),
                    'BRA': fila.get('Precio Original: Brasil')
                }

                # preparamos el diccionario original
                oferta = {
                    'USA': fila.get('Precio Oferta: USA'),
                    'TUR': fila.get('Precio Oferta: Turquia'),
                    'IND': fila.get('Precio Oferta: India'),
                    'PAN': fila.get('Precio Oferta: Panama'),
                    'BRA': fila.get('Precio Oferta: Brasil')
                }

                if titulo:
                    # guardamos el titulo
                    BaseDeDatos.set_juego(fila.get('ID'), titulo, fila.get('Imagen'), oferta, original)

        # Imprimir todos los titulos cargados
        print(f"[+] Base de datos cargada correctamente ({len(BaseDeDatos.diccionario_juegos)} títulos únicos mapeados).")
        return BaseDeDatos

    except Exception as e:
        print(f"[!] Error al leer '{DB_PATH}': {e}")
        return DB_Juegos()
