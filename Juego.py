import pygame as pg
import HUD

from entidades import PacMan
from Mapa import Cargar_Mapa, Dibujar_Mapa
from Frutas import Frutas
from entidades import TILE_SIZE

pg.init()
pg.mixer.init()
pg.font.init()

MAPA_ANCHO = 28 * TILE_SIZE
MAPA_ALTO = 31 * TILE_SIZE

HUD_ARRIBA = 75
HUD_ABAJO = 45

ANCHO = MAPA_ANCHO
ALTO = HUD_ARRIBA + MAPA_ALTO + HUD_ABAJO

GAME_OVER = False
Texto = 0
Duracion_GO= 3000

Inicio = pg.mixer.Sound("sonidos_pacman/start.wav")
Cinematica = pg.mixer.Sound("sonidos_pacman/intermission.wav")
Inicio.play()

pantalla = pg.display.set_mode((ANCHO, ALTO))
pg.display.set_caption("Test PacMan + Mapa + HUD + Frutas")

mapa_surface = pg.Surface((MAPA_ANCHO, MAPA_ALTO))

reloj = pg.time.Clock()
fuente = pg.font.SysFont("Courier", 30, bold=True)

mapa = Cargar_Mapa("mapa.txt")

grupo_paredes, grupo_puntos, Pos_Pm, Puertas = Dibujar_Mapa(
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

# ---------------- FRUTAS ----------------

grupo_frutas = pg.sprite.Group()

nivel = 1
contador_puntos_comidos = 0
frutas_aparecidas = 0

POS_FRUTA = (
    MAPA_ANCHO // 2,
    17 * TILE_SIZE + TILE_SIZE // 2
)
jugando = True

while jugando:
    dt = reloj.tick(60) / 1000

    for evento in pg.event.get():
        if evento.type == pg.QUIT:
            jugando = False

        if evento.type == pg.KEYDOWN:
            if evento.key == pg.K_m and pacman.estado != "muriendo":
                pacman.iniciar_muerte()

            elif evento.key == pg.K_f:
                fruta = Frutas(
                    POS_FRUTA[0],
                    POS_FRUTA[1],
                    nivel,
                    TILE_SIZE
                )
                grupo_frutas.add(fruta)

            elif pacman.estado != "muriendo":
                pacman.cambiar_direccion(evento.key)

    if not grupo_puntos:
        grupo_paredes, grupo_puntos, Pos_Pm, Puertas = Dibujar_Mapa(
            mapa_surface,
            mapa,
            TILE_SIZE
        )

        nivel += 1
        contador_puntos_comidos = 0
        frutas_aparecidas = 0
        grupo_frutas.empty()

    if pacman.estado == "muriendo":
        if pacman.actualizar_muerte():
            pacman.reiniciar_posicion(
                Pos_Pm[0] + TILE_SIZE // 2,
                Pos_Pm[1] + TILE_SIZE // 2
            )

    else:
        pacman.Choque(dt, TILE_SIZE, grupo_paredes, Puertas)
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

                contador_puntos_comidos += 1

                if contador_puntos_comidos in [70, 170] and frutas_aparecidas < 2:
                    if len(grupo_frutas) == 0:
                        fruta = Frutas(
                            POS_FRUTA[0],
                            POS_FRUTA[1],
                            nivel,
                            TILE_SIZE
                        )

                        grupo_frutas.add(fruta)
                        frutas_aparecidas += 1

                punto.kill()

        for fruta in grupo_frutas.copy():
            fruta.comer_frutas(pacman)
            fruta.actualizar()

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
    grupo_frutas.draw(mapa_surface)

    pacman.dibujar(mapa_surface)

    Puertas.draw(mapa_surface)

    pantalla.blit(mapa_surface, (0, HUD_ARRIBA))

    HUD.dibujar_hud(
        pantalla,
        pacman,
        high_score,
        fuente
    )

    if pacman.vidas < 0:
        Tiempo = pg.time.get_ticks()
        pantalla.fill((0,0,0))
        Fuente = pg.font.SysFont("Courier", 80, bold=True)
        Texto = Fuente.render("GAME OVER", True, (255, 255, 255))
        rect_Texto = Texto.get_rect(center=(ANCHO//2, ALTO//2))
        pantalla.blit(Texto, rect_Texto)
        if pg.time.get_ticks() - Tiempo >= Duracion_GO:
            jugando = False

    pg.display.flip()

pg.quit()