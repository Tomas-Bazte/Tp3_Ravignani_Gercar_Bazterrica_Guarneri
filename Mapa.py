import pygame as pg
def Cargar_Mapa(Ruta: str) -> list:
    """Parametros:
                   Ruta -> es donde se encuntra el archivo de texto
        Retorna: 
                   Mapa -> es el texto abierto y convertido en matriz"""
    with open (Ruta, "r") as Archivo:
       Mapa = Archivo.read().splitlines()
       return Mapa
def Dibujar_Mapa(pantalla, mapa : list, tamaño_casillero : int):
    for fila in range(len(mapa)):
        for columna in range(len(mapa[fila])):
            Carater = mapa[fila][columna]
            x = columna * tamaño_casillero
            y = fila * tamaño_casillero
            if Carater == "X":
                pg.draw.rect(pantalla,(25, 25, 166), x, y, tamaño_casillero, tamaño_casillero)
            elif Carater == ".":
                pg.draw.circl(pantalla, (222, 161, 133) ,(x + tamaño_casillero // 2, y + tamaño_casillero // 2), 3)
            elif Carater == "o":
                pg.draw.circl(pantalla, (222, 161, 133) ,(x + tamaño_casillero // 2, y + tamaño_casillero // 2), 7)

