import pygame as pg
import sys
from entidades import PacMan
import HUD
from Mapa import *

pg.init()
pg.mixer.init()
pg.font.init()

TILE_SIZE = 18

MAPA_ANCHO = 28 * TILE_SIZE
MAPA_ALTO = 31 * TILE_SIZE

HUD_ARRIBA = 75
HUD_ABAJO = 45

ANCHO = MAPA_ANCHO
ALTO = HUD_ARRIBA + MAPA_ALTO + HUD_ABAJO

Inicio = pg.mixer.Sound("sonidos_pacman/start.wav")
Cinematica = pg.mixer.Sound("sonidos_pacman/intermission.wav")
Inicio.play()

pantalla = pg.display.set_mode((ANCHO, ALTO))
pg.display.set_caption("Test PacMan + Mapa + HUD")

mapa_surface = pg.Surface((MAPA_ANCHO, MAPA_ALTO))

reloj = pg.time.Clock()
fuente = pg.font.SysFont("Courier", 30, bold=True)

mapa = Cargar_Mapa("mapa.txt")
grupo_paredes, grupo_puntos, Pos_Pm , Puertas = Dibujar_Mapa(
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
    
    if not grupo_puntos :
        #Aca va la funcion que reinicia el mapa una vez que no quedan puntos.
        Resetea = ""
        continue

    if pacman.estado == "muriendo":
        if pacman.actualizar_muerte():
            pacman.reiniciar_posicion(
                Pos_Pm[0] + TILE_SIZE // 2,
                Pos_Pm[1] + TILE_SIZE // 2
            )

    else:
        pacman.Choque(dt, TILE_SIZE, grupo_paredes,Puertas)
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
    Puertas.draw(mapa_surface)

    pantalla.blit(mapa_surface, (0, HUD_ARRIBA))

    HUD.dibujar_hud(
        pantalla,
        pacman,
        high_score,
        fuente
    )

    pg.display.flip()

pg.quit()