import pygame as pg
from entidades import TILE_SIZE

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
        pg.draw.rect(self.image,(0,0,255),(0,0,tamaño,tamaño),1)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)


class puntitos (pg.sprite.Sprite):
    def __init__ (self,x,y,Super=False,tile_size=18):
        super().__init__()
        self.es_power_pellet = Super
        radio = (int(tile_size//4) if Super else int(tile_size//8))
        tamaño = radio*2
        self.image = pg.Surface((tamaño,tamaño),pg.SRCALPHA)
        pg.draw.circle(self.image,(255,255,255),(radio,radio),radio)
        self.rect = self.image.get_rect()
        self.rect.center = (int(x+(tile_size//2)),int(y+(tile_size//2)))
    
    def flash_power_pellet(self):
        if self.es_power_pellet:
            tiempo = pg.time.get_ticks()
            if (tiempo // 200) % 2 == 0:
                self.image.set_alpha(255)
            else:
                self.image.set_alpha(0)

class tuneles (pg.sprite.Sprite):
    def __init__(self):
        super().__init__()

class Puerta_H (pg.sprite.Sprite):
    def __init__(self,x,y,tamaño):
        super().__init__()
        self.image = pg.Surface((tamaño,tamaño),pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        pg.draw.line(self.image,(255,255,255),(0,0),(tamaño,0),5)


def Dibujar_Mapa(pantalla, mapa : list, tamaño_casillero = 18) -> None:
    grupo_Paredes = pg.sprite.Group()
    grupo_puntos = pg.sprite.Group()
    Puerta = pg.sprite.Group()
    Spawns = []
    for fila in range(len(mapa)):
        for columna in range(len(mapa[fila])):
            Caracter = mapa[fila][columna]
            x = columna * tamaño_casillero
            y = fila * tamaño_casillero
            if Caracter == "X":
               Nueva_pared= pared(x, y, tamaño_casillero-0.000001)
               grupo_Paredes.add(Nueva_pared)
            elif Caracter == ".":
                Nuevo_punto = puntitos(x,y,False,tamaño_casillero)
                grupo_puntos.add(Nuevo_punto)
            elif Caracter == "o":
                Nuevo_punto = puntitos(x,y,True,tamaño_casillero)
                grupo_puntos.add(Nuevo_punto)
            elif Caracter == "P":
                Pos_Pm = (x,y)
            elif Caracter == "-":
                Nueva_puerta = Puerta_H (x , y ,tamaño_casillero )
                Puerta.add(Nueva_puerta)
            elif Caracter == "G":
                Spawns.append((x,y))

                
    return grupo_Paredes, grupo_puntos, Pos_Pm , Puerta
