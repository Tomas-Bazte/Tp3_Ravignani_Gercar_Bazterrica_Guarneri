import pygame as pg
def Cargar_Mapa(Ruta: str) -> list:
    """Parametros:
                   Ruta -> es donde se encuntra el archivo de texto
        Retorna: 
                   Mapa -> es el texto abierto y convertido en matriz"""
    with open (Ruta, "r") as Archivo:
       Mapa = Archivo.read().splitlines()
       return Mapa
    
def Dibujar_Pared(pantalla, x, y, tamaño_casillero ): 
    pg.draw.rect(pantalla, (0, 0, 0), (x, y, tamaño_casillero, tamaño_casillero))
    pg.draw.rect(pantalla, (0, 0, 255), (x, y, tamaño_casillero, tamaño_casillero), 2)

def Dibujar_Mapa(pantalla, mapa : list, tamaño_casillero = 24) -> None:
    for fila in range(len(mapa)):
        for columna in range(len(mapa[fila])):
            Carater = mapa[fila][columna]
            x = columna * tamaño_casillero
            y = fila * tamaño_casillero
            if Carater == "X":
               Dibujar_Pared(pantalla, x, y, tamaño_casillero )
            elif Carater == ".":
                pg.draw.circle(pantalla, (222, 161, 133) ,(x + tamaño_casillero // 2, y + tamaño_casillero // 2), 3)
            elif Carater == "o":
                pg.draw.circle(pantalla, (222, 161, 133) ,(x + tamaño_casillero // 2, y + tamaño_casillero // 2), 7)
            elif Carater == "G":
                pg.draw.rect(pantalla, (0, 0, 0), (x, y, tamaño_casillero, tamaño_casillero))
            elif Carater == "-":
                 pg.draw.line(pantalla,(255, 150, 255), (x, y + TILE // 2), (x + TILE, y + TILE // 2), 4 )
import sys

pg.init()

TILE = 20

mapa = Cargar_Mapa("Mapa.txt")

ANCHO = len(mapa[0]) * TILE
ALTO = len(mapa) * TILE

pantalla = pg.display.set_mode((ANCHO, ALTO))

while True:

    for evento in pg.event.get():
        if evento.type == pg.QUIT:
            pg.quit()
            sys.exit()

    pantalla.fill((0, 0, 0))

    Dibujar_Mapa(pantalla, mapa, TILE)

    pg.display.flip()
