import pygame as pg
import sys
def Cargar_Mapa(Ruta: str) -> list:
    """Parametros:
                   Ruta -> es donde se encuntra el archivo de texto
        Retorna: 
                   Mapa -> es el texto abierto y convertido en matriz"""
    with open (Ruta, "r") as Archivo:
       Mapa = Archivo.read().splitlines()
       return Mapa

class pared (pg.sprite.Sprite):
    def __init__(self,x,y,tamaño):
        super().__init__()
        self.image = pg.Surface((tamaño,tamaño))
        self.image.fill((0,0,0))
        pg.draw.rect(self.image,(0,0,255),(0,0,tamaño,tamaño),2)
        self.hitbox = self.image.get_rect()


class puntitos (pg.sprite.Sprite):
    def __init__ (self,x,y,Super=False):
        super().__init__()
        radio = (7 if Super else 3)
        tamaño = radio*2
        self.image = pg.Surface((tamaño,tamaño),pg.SRCALPHA)
        pg.draw.circle(self.image(222,161,133),(radio,radio),radio)
        self.hitbox = self.image.get_rect()
        self.rect.center = (x+12,y+12)


def Dibujar_Mapa(pantalla, mapa : list, tamaño_casillero = 24) -> None:
    grupo_Paredes = pg.sprite.Group()
    grupo_puntos = pg.sprite.Group()
    for fila in range(len(mapa)):
        for columna in range(len(mapa[fila])):
            Caracter = mapa[fila][columna]
            x = columna * tamaño_casillero
            y = fila * tamaño_casillero
            if Caracter == "X":
               Nueva_pared= pared(x, y, tamaño_casillero)
               grupo_Paredes.add(Nueva_pared)
            elif Caracter == ".":
                Nuevo_punto = puntitos(x,y,False)
                grupo_puntos.add(Nuevo_punto)
            elif Caracter == "o":
                Nuevo_punto = puntitos(x,y,True)
                grupo_puntos.add(Nuevo_punto)

                
    return grupo_Paredes, grupo_puntos

pg.init()

TILE = 24

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
