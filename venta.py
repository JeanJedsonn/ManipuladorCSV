
# Diccionario con una lista de ventas para el mismo juego
"""
registro: dict[str,str|None] = {
    "PS4P": str|None,
    "PS4S": str|None,
    "PS5P": str|None,
    "PS5S": str|None
}
"""
import statistics as stats
import re

class Registro:
    def __init__(self, ps4p: str|None, ps4s: str|None, ps5p: str|None, ps5s: str|None) -> None:
        self.ps4p: str|None = ps4p
        self.ps4s: str|None = ps4s
        self.ps5p: str|None = ps5p
        self.ps5s: str|None = ps5s

class Venta:
    def __init__(self) -> None:
        self.id: int = None                                 # El ID del juego en la BD
        self.url: str = None                                # La url del juego
        self.ps4: bool = False                              # Si el juego tiene alguna venta de PS4
        self.ps5: bool = False                              # Si el juego tiene alguna venta de PS5
        self.registros: list[Registro] = []                 # Lista de registros

    def set_id(self,id: int) -> None:
        self.id = id

    def set_url(self,url: str) -> None:
        self.url = url

    def get_url(self) -> str:
        return self.url

    def set_ps4(self,ps4: bool) -> None:
        self.ps4 = ps4

    def set_ps5(self,ps5: bool) -> None:
        self.ps5 = ps5

    def get_ps4(self) -> bool:
        return self.ps4

    def get_ps5(self) -> bool:
        return self.ps5

    """ * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - 
        METODOS COMPLEJOS
    """ 

    def push_registro(self,registro: dict[str, str|None]) -> None:
        self.registros.append(registro)

    def get_registro(self) -> list[dict[str, str|None]]:
        return self.registros

    def get_len(self) -> int:
        return len(self.registros)

    def get_vendidos(self) -> int:
        sol = 0
        for registro in self.registros:
            if registro.ps4p != "-" and registro.ps4p != "N/D" and registro.ps4p != "":
                sol += 1
            if registro.ps4s != "-" and registro.ps4s != "N/D" and registro.ps4s != "":
                sol += 1
            if registro.ps5p != "-" and registro.ps5p != "N/D" and registro.ps5p != "":
                sol += 1
            if registro.ps5s != "-" and registro.ps5s != "N/D" and registro.ps5s != "":
                sol += 1
        return sol

    def tipos_libres(self) -> dict[str, bool]:
        solucion = {
            "ps4p": False,
            "ps4s": False,
            "ps5p": False,
            "ps5s": False
        }
        atributos = ['ps4p', 'ps4s', 'ps5p', 'ps5s']
        for attr in atributos:
            # print([getattr(r, attr) for r in self.registros])

            if any(getattr(r, attr) is "" for r in self.registros):
                solucion[attr] = True
                
        return solucion

    def calcular_precio_mediano(self) -> dict[str, float]:
        solucion = {
            "ps4p": None,
            "ps4s": None,
            "ps5p": None,
            "ps5s": None
        }
        atributos = ['ps4p', 'ps4s', 'ps5p', 'ps5s']
        
        for attr in atributos:
            valores = []
            for registro in self.registros:
                captura = re.search(r"(\d+(?:[\.,]\d+)?)", getattr(registro, attr))
                if captura:
                    valores.append(float(captura.group(1).replace(',', '.')))
            if valores:
                solucion[attr] = stats.median(valores)
        return solucion