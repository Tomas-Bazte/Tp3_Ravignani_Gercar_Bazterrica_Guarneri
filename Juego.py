import pygame as pg
import HUD
from entidades import PacMan
from Mapa import Cargar_Mapa, Dibujar_Mapa, dibujar_ready, dibujar_game_over , MAPA_ALTO , MAPA_ANCHO , ANCHO , ALTO , HUD_ABAJO ,HUD_ARRIBA
from Frutas import Frutas
from Intermissions import Intermission
from entidades import TILE_SIZE
from Menu import menu_inicio
from Fantasma import Blinky, Pinky, Clyde, Inky

pg.init()
pg.mixer.init()
pg.font.init()


pantalla = pg.display.set_mode((ANCHO, ALTO))
pg.display.set_caption("Test Pac-Man")

HUD.cargar_frutas_hud()

mapa_surface = pg.Surface((MAPA_ANCHO, MAPA_ALTO))

reloj = pg.time.Clock()
fuente = pg.font.SysFont("Courier", 30, bold=True)

mapa = Cargar_Mapa("mapa.txt")

grupo_paredes, grupo_puntos, Pos_Pm, Puertas, Spawns = Dibujar_Mapa(
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

estado_juego = "ready"
tiempo_inicio_estado = 0

duracion_pausa_nivel = 1000
duracion_flash_mapa = 3000
duracion_ready_sin_sonido = 2000

Tiempo = 0
Duracion_GO = 3000
contando = False

sonido_inicio = pg.mixer.Sound("sonidos_pacman/start.wav")
canal_inicio = None

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


def iniciar_ready(con_sonido=False):
    global canal_inicio, tiempo_inicio_estado

    tiempo_inicio_estado = pg.time.get_ticks()

    if con_sonido:
        canal_inicio = sonido_inicio.play()
    else:
        canal_inicio = None

    return "ready"


jugando = True
Fantasmas , Esquinas = menu_inicio(pantalla)

esquinas_scatters = {
    "Superior Izquierda": (0, 0),
    "Superior Derecha":   (MAPA_ANCHO, 0),
    "Inferior Izquierda": (0, MAPA_ALTO),
    "Inferior Derecha":   (MAPA_ANCHO, MAPA_ALTO)
}

fantasmas = {
    1: ('Blinky', Blinky),
    2: ('Pinky', Pinky),
    3: ('Inky', Inky),
    4: ('Clyde', Clyde)
}

colores = {
    1: (255, 0, 0),
    2: (255, 184, 255),
    3: (0, 255, 255),
    4: (255, 184, 82)
}

puntos_fantasmas = [200,400,800,1600]
fantasmas_comidos = 0

def incorporar_fantasmas(id_elegido, esquinas_elegidas, spawns, grupo_paredes):
    lista_fantasmas = []
    x_casa = MAPA_ANCHO // 2
    y_casa = 14 * TILE_SIZE
    blinky_ref = None

    for i, id in enumerate(id_elegido):
        if id not in fantasmas.keys():
            continue
        nombre, clase = fantasmas[id]
        color = colores[id]
        if i < len(spawns):
            spawn = spawns[i]
        else:
            spawn = spawns[0]
        x = spawn[0]
        y = spawn[1]
        
        esquina_scatter = esquinas_scatters[esquinas_elegidas[id]]

        pos_Pc = (pacman.x, pacman.y)

        if clase == Blinky:
            f = Blinky(x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_paredes)
            blinky_ref = f
        elif clase == Clyde:
            f = Clyde(x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_paredes)
        elif clase == Pinky:
            f = Pinky(x, y, nombre, color, esquina_scatter, pos_Pc, pacman.direccion, x_casa, y_casa, grupo_paredes)
        elif clase == Inky:
            f = Inky(x, y, nombre, color, esquina_scatter, pos_Pc, pacman.direccion, blinky_ref, x_casa, y_casa, grupo_paredes)
        lista_fantasmas.append(f)
    return lista_fantasmas

fantasmas_juego = incorporar_fantasmas(Fantasmas, Esquinas, Spawns, grupo_paredes)
estado_juego = iniciar_ready(con_sonido=True)

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

    if estado_juego == "ready":

        if canal_inicio is not None:
            if not canal_inicio.get_busy():
                estado_juego = "jugando"
        else:
            if pg.time.get_ticks() - tiempo_inicio_estado >= duracion_ready_sin_sonido:
                estado_juego = "jugando"

    elif estado_juego == "jugando":

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
                        fantasmas_comidos = 0
                        for fantasma in fantasmas_juego:
                            if fantasma.estado != 'muerto':
                                fantasma.activar_asustado()
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
        
            for fantasma in fantasmas_juego:
                if type(fantasma) == Pinky or type(fantasma) == Inky:
                    fantasma.ejecutar((int(pacman.x), int(pacman.y)), pacman.direccion, dt)
                else:
                    fantasma.ejecutar((int(pacman.x), int(pacman.y)), dt)

            for fantasma in fantasmas_juego:
                if pacman.rect.colliderect(fantasma.rect):
                    if pacman.modo_super and fantasma.estado == 'asustado':
                        fantasma.muerto()
                        pacman.sumar_puntos(puntos_fantasmas[fantasmas_comidos])
                        fantasmas_comidos += 1
                    elif fantasma.estado != 'muerto' and fantasma.estado != 'asustado':
                        pacman.iniciar_muerte()
                        fantasmas_comidos = 0
                        break

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
                estado_juego = iniciar_ready(con_sonido=False)

    elif estado_juego == "intermission":

        termino = intermission.actualizar_intermission()

        if termino:
            estado_juego = iniciar_ready(con_sonido=False)

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
    for fantasma in fantasmas_juego:
        fantasma.Dibujar(mapa_surface)

    if estado_juego == "ready":
        dibujar_ready(mapa_surface)

    elif estado_juego == "game_over":
        dibujar_game_over(mapa_surface)

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

    pg.display.flip()

pg.quit()