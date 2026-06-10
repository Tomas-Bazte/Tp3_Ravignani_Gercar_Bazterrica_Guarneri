import pygame as pg
from entidades import TILE_SIZE


MAPA_ANCHO = 28 * TILE_SIZE
MAPA_ALTO = 31 * TILE_SIZE


HUD_ARRIBA = 75
HUD_ABAJO = 45

ANCHO = MAPA_ANCHO
ALTO = HUD_ARRIBA + MAPA_ALTO + HUD_ABAJO

def Cargar_Mapa(Ruta: str) -> list:
    """Parametros:
                   Ruta -> es donde se encuntra el archivo de texto
        Retorna: 
                   Mapa -> es el texto abierto y convertido en matriz"""
    with open (Ruta, "r") as Archivo:
       Mapa = Archivo.read().splitlines()
       return Mapa

def menu_inicio(pantalla):

    fuente_titulo = pg.font.SysFont("Courier", 70, bold=True)
    fuente_menu = pg.font.SysFont("Courier", 35, bold=True)
    menu = True
    while menu:

        for evento in pg.event.get():

            if evento.type == pg.QUIT:
                pg.quit()
                exit()

            if evento.type == pg.KEYDOWN:
                if evento.key == pg.K_SPACE:
                    menu = False

                if evento.key == pg.K_ESCAPE:
                    pg.quit()
                    exit()


        pantalla.fill((0,0,0))


        titulo = fuente_titulo.render(
            "PAC-MAN",
            True,
            (255,255,0)
        )

        jugar = fuente_menu.render(
            "ESPACIO - JUGAR",
            True,
            (255,255,255)
        )

        salir = fuente_menu.render(
            "ESC - SALIR",
            True,
            (255,255,255)
        )


        pantalla.blit(
            titulo,
            titulo.get_rect(center=(ANCHO//2, ALTO//3))
        )

        pantalla.blit(
            jugar,
            jugar.get_rect(center=(ANCHO//2, ALTO//2))
        )

        pantalla.blit(
            salir,
            salir.get_rect(center=(ANCHO//2, ALTO//2 + 60))
        )


        pg.display.flip()


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

def cambiar_color(self, color): # Funcion que sirve para cambiar el color del mapa de azul a blanco cuanto termine el nivel.
    self.image.fill((0, 0, 0))
    pg.draw.rect(self.image,color,self.image.get_rect(),1)