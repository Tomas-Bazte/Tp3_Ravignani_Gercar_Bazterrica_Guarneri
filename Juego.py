import pygame as pg
import HUD

from entidades import PacMan
from Mapa import Cargar_Mapa, Dibujar_Mapa, menu_inicio
from Frutas import Frutas
from Intermissions import Intermission

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

pantalla = pg.display.set_mode((ANCHO, ALTO))
pg.display.set_caption("Test Pac-Man")

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

grupo_frutas = pg.sprite.Group()

intermission = Intermission()
nivel_intermission_actual = 3

nivel = 1
contador_puntos_comidos = 0
frutas_aparecidas = 0

POS_FRUTA = (
    MAPA_ANCHO // 2,
    17 * TILE_SIZE + TILE_SIZE // 2
)

estado_juego = "jugando"
tiempo_inicio_estado = 0

duracion_pausa_nivel = 1000
duracion_flash_mapa = 3000

Tiempo = 0
Duracion_GO = 3000
contando = False

inicio = pg.mixer.Sound("sonidos_pacman/start.wav")
inicio.play()


def cambiar_color_paredes(grupo_paredes, color):
    for pared in grupo_paredes:
        pared.image.fill((0, 0, 0))
        pg.draw.rect(
            pared.image,
            color,
            pared.image.get_rect(),
            1
        )


def iniciar_intermission_por_nivel(nivel_a_probar):
    intermission.cargar_frames_intermission_1(nivel_a_probar)
    intermission.iniciar_intermission()


jugando = True
menu_inicio(pantalla)

while jugando:
    dt = reloj.tick(60) / 1000

    for evento in pg.event.get():
        if evento.type == pg.QUIT:
            jugando = False

        if evento.type == pg.KEYDOWN:

            if evento.key == pg.K_i:
                nivel_intermission_actual = 3
                iniciar_intermission_por_nivel(nivel_intermission_actual)
                estado_juego = "intermission"

            elif evento.key == pg.K_o:
                nivel_intermission_actual = 6
                iniciar_intermission_por_nivel(nivel_intermission_actual)
                estado_juego = "intermission"

            elif evento.key == pg.K_p:
                nivel_intermission_actual = 10
                iniciar_intermission_por_nivel(nivel_intermission_actual)
                estado_juego = "intermission"

            elif estado_juego == "jugando":

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

    # ---------------------
    # UPDATE
    # ---------------------

    if estado_juego == "jugando":

        if len(grupo_puntos) == 0:
            estado_juego = "pausa_nivel"
            tiempo_inicio_estado = pg.time.get_ticks()

            pacman.direccion = "quieto"
            pacman.prox = "quieto"
            pacman.nivel_completado = True
            pacman.frame_animacion = 0

        elif pacman.estado == "muriendo":

            if pacman.actualizar_muerte():
                pacman.reiniciar_posicion(
                    Pos_Pm[0] + TILE_SIZE // 2,
                    Pos_Pm[1] + TILE_SIZE // 2
                )

        else:
            pacman.Choque(
                dt,
                TILE_SIZE,
                grupo_paredes,
                Puertas
            )

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

            if pacman.vidas < 0:
                estado_juego = "game_over"

    elif estado_juego == "pausa_nivel":

        if pg.time.get_ticks() - tiempo_inicio_estado >= duracion_pausa_nivel:
            estado_juego = "flash_mapa"
            tiempo_inicio_estado = pg.time.get_ticks()

    elif estado_juego == "flash_mapa":

        tiempo_actual = pg.time.get_ticks()

        if (tiempo_actual // 250) % 2 == 0:
            cambiar_color_paredes(grupo_paredes, (0, 0, 255))
        else:
            cambiar_color_paredes(grupo_paredes, (255, 255, 255))

        if tiempo_actual - tiempo_inicio_estado >= duracion_flash_mapa:
            nivel += 1
            contador_puntos_comidos = 0
            frutas_aparecidas = 0
            grupo_frutas.empty()

            grupo_paredes, grupo_puntos, Pos_Pm, Puertas = Dibujar_Mapa(
                mapa_surface,
                mapa,
                TILE_SIZE
            )

            pacman.reiniciar_posicion(
                Pos_Pm[0] + TILE_SIZE // 2,
                Pos_Pm[1] + TILE_SIZE // 2
            )

            pacman.nivel_completado = False

            if nivel in [3, 6, 10, 14, 18]:
                nivel_intermission_actual = nivel
                iniciar_intermission_por_nivel(nivel_intermission_actual)
                estado_juego = "intermission"
            else:
                estado_juego = "jugando"

    elif estado_juego == "intermission":

        termino = intermission.actualizar_intermission()

        if termino:
            estado_juego = "jugando"

    elif estado_juego == "game_over":

        if not contando:
            Tiempo = pg.time.get_ticks()
            contando = True

        if pg.time.get_ticks() - Tiempo >= Duracion_GO:
            jugando = False

    high_score = HUD.actualizar_high_score(
        pacman,
        high_score
    )

    # ---------------------
    # DIBUJAR
    # ---------------------

    if estado_juego == "intermission":
        pantalla.fill((0, 0, 0))

        intermission.dibujar_intermission(
            pantalla,
            nivel_intermission_actual
        )

        pg.display.flip()
        continue

    pantalla.fill((0, 0, 0))
    mapa_surface.fill((0, 0, 0))

    grupo_paredes.draw(mapa_surface)

    if estado_juego != "flash_mapa":
        grupo_puntos.draw(mapa_surface)
        grupo_frutas.draw(mapa_surface)
        Puertas.draw(mapa_surface)

    pacman.dibujar(mapa_surface)

    pantalla.blit(
        mapa_surface,
        (0, HUD_ARRIBA)
    )

    HUD.dibujar_hud(
        pantalla,
        pacman,
        high_score,
        fuente
    )

    if estado_juego == "game_over":

        pantalla.fill((0, 0, 0))

        Fuente = pg.font.SysFont("Courier", 80, bold=True)

        Texto = Fuente.render(
            "GAME OVER",
            True,
            (255, 255, 255)
        )

        rect_Texto = Texto.get_rect(
            center=(ANCHO // 2, ALTO // 2)
        )

        pantalla.blit(Texto, rect_Texto)

    pg.display.flip()

pg.quit()