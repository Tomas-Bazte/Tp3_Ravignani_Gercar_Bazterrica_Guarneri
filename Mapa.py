import pygame as pg
import sys
from entidades import PacMan
import HUD

pg.init()
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
    def __init__ (self,x,y,Super=False):
        super().__init__()
        self.es_power_pellet = Super
        radio = (7 if Super else 3)
        tamaño = radio*2
        self.image = pg.Surface((tamaño,tamaño),pg.SRCALPHA)
        pg.draw.circle(self.image,(255,255,255),(radio,radio),radio)
        self.rect = self.image.get_rect()
        self.rect.center = (x+12,y+12)
    
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
            elif Caracter == "P":
                Pos_Pm = (x,y)

                
    return grupo_Paredes, grupo_puntos, Pos_Pm

pg.init()
pg.mixer.init()
pg.font.init()

TILE_SIZE = 24

MAPA_ANCHO = 28 * TILE_SIZE
MAPA_ALTO = 31 * TILE_SIZE

HUD_ARRIBA = 75
HUD_ABAJO = 45

ANCHO = MAPA_ANCHO
ALTO = HUD_ARRIBA + MAPA_ALTO + HUD_ABAJO

pantalla = pg.display.set_mode((ANCHO, ALTO))
pg.display.set_caption("Test PacMan + Mapa + HUD")

mapa_surface = pg.Surface((MAPA_ANCHO, MAPA_ALTO))

reloj = pg.time.Clock()
fuente = pg.font.SysFont("Courier", 30, bold=True)

mapa = Cargar_Mapa("mapa.txt")
grupo_paredes, grupo_puntos, Pos_Pm = Dibujar_Mapa(
    mapa_surface,
    mapa,
    TILE_SIZE
)

pacman = PacMan(
    Pos_Pm[0] + TILE_SIZE // 2,
    Pos_Pm[1] + TILE_SIZE // 2
)

pacman.cargar_frames_muerte()

high_score = HUD.cargar_high_score()

jugando = True

while jugando:
    dt = reloj.tick(60) / 1000

    for evento in pg.event.get():
        if evento.type == pg.QUIT:
            jugando = False

        if evento.type == pg.KEYDOWN:
            if evento.key == pg.K_m and pacman.estado != "muriendo":
                pacman.iniciar_muerte()
            elif pacman.estado != "muriendo":
                pacman.cambiar_direccion(evento.key)

    if pacman.estado == "muriendo":
        if pacman.actualizar_muerte():
            pacman.reiniciar_posicion(
                Pos_Pm[0] + TILE_SIZE // 2,
                Pos_Pm[1] + TILE_SIZE // 2
            )

    else:
        pacman.Choque(dt, TILE_SIZE, grupo_paredes)
        pacman.manejar_tunel(MAPA_ANCHO)
        pacman.actualizar_animacion()
        pacman.actualizar_super()

        hitbox_pm = pacman.obtener_hitbox()

        for punto in grupo_puntos.copy():
            if hitbox_pm.colliderect(punto.rect):
                if punto.es_power_pellet:
                    pacman.comer_power_pellet()
                else:
                    pacman.comer_punto()

                punto.kill()

    for punto in grupo_puntos:
        punto.flash_power_pellet()

    high_score = HUD.actualizar_high_score(
        pacman,
        high_score
    )

    pantalla.fill((0, 0, 0))
    mapa_surface.fill((0, 0, 0))

    grupo_paredes.draw(mapa_surface)
    grupo_puntos.draw(mapa_surface)
    pacman.dibujar(mapa_surface)

    pantalla.blit(mapa_surface, (0, HUD_ARRIBA))

    HUD.dibujar_hud(
        pantalla,
        pacman,
        high_score,
        fuente
    )

    pg.display.flip()

pg.quit()