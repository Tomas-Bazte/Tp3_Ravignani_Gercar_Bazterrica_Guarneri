import pygame as pg
import HUD
from entidades import PacMan
from Mapa import Cargar_Mapa, Dibujar_Mapa, dibujar_ready, dibujar_game_over , MAPA_ALTO , MAPA_ANCHO , ANCHO , ALTO , HUD_ABAJO ,HUD_ARRIBA
from Frutas import Frutas
from Intermissions import Intermission
from entidades import TILE_SIZE
from Menu import menu_inicio
from Fantasma import Blinky, Pinky, Clyde, Inky , Tracer, Patrullero

class PuntosFlotantes(pg.sprite.Sprite):
    """Muestra los puntos obtenidos al comer un fantasma, igual que Frutas."""
    def __init__(self, x, y, puntos):
        super().__init__()
        fuente = pg.font.SysFont("Courier", 12, bold=True)
        self.image = fuente.render(str(puntos), True, (0, 255, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.tiempo_inicio = pg.time.get_ticks()
        self.duracion = 1000

    def actualizar(self):
        if pg.time.get_ticks() - self.tiempo_inicio >= self.duracion:
            self.kill()

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
grupo_paredes, grupo_puntos, Pos_Pm, Puertas, Spawns = Dibujar_Mapa(mapa_surface,mapa,TILE_SIZE)
pacman = PacMan(Pos_Pm[0] + TILE_SIZE // 2, Pos_Pm[1] + TILE_SIZE // 2)
pacman.cargar_frames_muerte()
high_score = HUD.cargar_high_score()
grupo_frutas = pg.sprite.Group()
grupo_puntos_flotantes = pg.sprite.Group()
intermission = Intermission()
nivel_intermission_actual = 3
nivel = 1
contador_puntos_comidos = 0
frutas_aparecidas = 0
POS_FRUTA = (MAPA_ANCHO // 2, 17 * TILE_SIZE + TILE_SIZE // 2)
estado_juego = "ready"
tiempo_inicio_estado = 0
duracion_pausa_nivel = 1000
duracion_flash_mapa = 3000
duracion_ready_sin_sonido = 2000
Tiempo = 0
Duracion_GO = 3000 # Game Over
contando = False
tiempo_freeze = 0
fantasma_comido = None
sonido_inicio = pg.mixer.Sound("sonidos_pacman/start.wav")
sonido_fantasma = pg.mixer.Sound("sonidos_pacman/eat_ghost.wav")
canal_inicio = None
def cambiar_color_paredes(grupo_paredes, color : tuple)->None:
    """hace que parpade las paredes
    Argumentos:
        Grupo_paredes: son todas las paredes del mapa
        color: tupla con rgb con color de paredes"""
    for pared in grupo_paredes:
        pared.image.fill((0, 0, 0))
        pg.draw.rect(pared.image,color,pared.image.get_rect(),1)

def iniciar_intermission_por_nivel(nivel : int) ->None:
    """inicialisa  una intermission dependiendo el nivel"""
    intermission.cargar_frames_intermission_1(nivel)
    intermission.iniciar_intermission()

def iniciar_ready(con_sonido=False) ->str:
    """inicia el modo ready del juego al principio de cada ronda 
    Argumentos:
        con_sonido: bool con si se quiere usar un sonido
    Retorna:
        devuelve ready para cambiar el estado del juego"""
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
    4: ('Clyde', Clyde),
    5: ("Tracer",Tracer),
    6 : ("Patrullero", Patrullero)
}

colores = {
    1: (255, 0, 0),
    2: (255, 184, 255),
    3: (0, 255, 255),
    4: (255, 184, 82),
    5: (50,50,50),
    6: (255, 255, 0)
}

puntos_fantasmas = [200,400,800,1600]
fantasmas_comidos = 0
salida_fantasma = [0,30,60,90]

def incorporar_fantasmas(id_elegido : list, esquinas_elegidas : dict, spawns : list, grupo_paredes)->list:
    """crea los fantsmas elejidos en el menu 
    recorre los id seleccionados, busca a que clase corresponde, toma su color, su esquina scatter, su pocicion de spawn y creea el objeto fantasma correspondiente
    Argumentos:
        id_elejido: Lista con los nuemros de fantasmas elejidos
        esquina elejids: direcion con la esquina sactter de cada fantasma 
        spawn: lista de posisiones donde aparesen los fantasmas
        grupo_paredes: grupos de paredes usado para detectar colisones
    Retorna:
        lista con los fantasmas creeados para usar en el juego"""
    lista_fantasmas = []
    blinky_ref = None
    x_casa = MAPA_ANCHO // 2
    y_casa = 14 * TILE_SIZE
    for i, id in enumerate(id_elegido):
        if id not in fantasmas:
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
        elif clase == Tracer:
            f = Tracer (x,y,Tracer,(50,50,50),esquina_scatter,pos_Pc,pacman.direccion ,x_casa,y_casa,grupo_paredes)
        elif clase == Patrullero:
            f = Patrullero(x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_paredes)
        lista_fantasmas.append(f)
    return lista_fantasmas
fantasmas_juego = incorporar_fantasmas(Fantasmas, Esquinas, Spawns, grupo_paredes)
for fantasma in fantasmas_juego:
    fantasma.grupo_Puertas = Puertas
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
                    fruta = Frutas(POS_FRUTA[0], POS_FRUTA[1], nivel, TILE_SIZE)
                    grupo_frutas.add(fruta)
                elif pacman.estado != "muriendo":
                    pacman.cambiar_direccion(evento.key)
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
                pacman.reiniciar_posicion(Pos_Pm[0] + TILE_SIZE // 2 ,Pos_Pm[1] + TILE_SIZE // 2)
                contador_puntos_comidos = 0
                fantasmas_comidos = 0
                for i, fantasma in enumerate(fantasmas_juego):
                    if i < len(Spawns):
                        spawn = Spawns[i]
                    else:
                        spawn = Spawns[0]
                    fantasma.reiniciar(spawn[0], spawn[1])
                estado_juego = iniciar_ready(False)
                if pacman.vidas >= 0:
                    estado_juego = iniciar_ready(con_sonido=False)
        else:
            en_freeze = tiempo_freeze > 0 and pg.time.get_ticks() - tiempo_freeze < 1000
            if not en_freeze:
                tiempo_freeze = 0

            if not en_freeze:
                pacman.Choque(dt, TILE_SIZE, grupo_paredes, Puertas)
            if not en_freeze:
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
                            fruta = Frutas( POS_FRUTA[0], POS_FRUTA[1], nivel, TILE_SIZE)
                            grupo_frutas.add(fruta)
                            frutas_aparecidas += 1
                    punto.kill()
            for i, fantasma in enumerate(fantasmas_juego):
                if (fantasma.estado == "scatter" and fantasma.en_casa and contador_puntos_comidos >= salida_fantasma[i]):
                    fantasma.en_casa = False
                    fantasma.estado = "saliendo"
            if not en_freeze:
                for fantasma in fantasmas_juego:
                    if type(fantasma) == Pinky or type(fantasma) == Inky or type(fantasma) == Tracer:
                        fantasma.ejecutar((int(pacman.x), int(pacman.y)), pacman.direccion, dt)
                    else:
                        fantasma.ejecutar((int(pacman.x), int(pacman.y)), dt)
            if not en_freeze:
                for fantasma in fantasmas_juego:
                    if pacman.rect.colliderect(fantasma.rect):
                        if fantasma.estado == 'muerto':
                            continue
                        elif fantasma.estado == 'asustado':
                            if pacman.modo_super:
                                pts = puntos_fantasmas[min(fantasmas_comidos, len(puntos_fantasmas) - 1)]
                                fantasma.muerto()
                                pacman.sumar_puntos(pts)
                                fantasmas_comidos += 1
                                sonido_fantasma.play()
                                pf = PuntosFlotantes(fantasma.rect.centerx, fantasma.rect.centery, pts)
                                grupo_puntos_flotantes.add(pf)
                                tiempo_freeze = pg.time.get_ticks()
                                fantasma_comido = fantasma
                                break 
                        else:
                            pacman.iniciar_muerte()
                            fantasmas_comidos = 0
                            break
            for fruta in grupo_frutas.copy():
                fruta.comer_frutas(pacman)
                fruta.actualizar()
            for pf in grupo_puntos_flotantes.copy():
                pf.actualizar()
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
            grupo_paredes, grupo_puntos, Pos_Pm, Puertas, Spawns = Dibujar_Mapa(mapa_surface, mapa, TILE_SIZE)
            pacman.reiniciar_posicion(Pos_Pm[0] + TILE_SIZE // 2, Pos_Pm[1] + TILE_SIZE // 2)
            pacman.nivel_completado = False
            fantasmas_juego = incorporar_fantasmas(Fantasmas, Esquinas, Spawns, grupo_paredes)
            for fantasma in fantasmas_juego:
                fantasma.grupo_Puertas = Puertas
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
    high_score = HUD.actualizar_high_score(pacman, high_score)
    if estado_juego == "intermission":
        pantalla.fill((0, 0, 0))
        intermission.dibujar_intermission(pantalla, nivel_intermission_actual)
        HUD.dibujar_frutas_hud(pantalla, pacman)
        pg.display.flip()
        continue
    pantalla.fill((0, 0, 0))
    mapa_surface.fill((0, 0, 0))
    grupo_paredes.draw(mapa_surface)
    if estado_juego != "flash_mapa":
        grupo_puntos.draw(mapa_surface)
        grupo_frutas.draw(mapa_surface)
        Puertas.draw(mapa_surface)
    en_freeze_dibujo = tiempo_freeze > 0 and pg.time.get_ticks() - tiempo_freeze < 1000
    if not en_freeze_dibujo:
        pacman.dibujar(mapa_surface)
    for fantasma in fantasmas_juego:
        if en_freeze_dibujo and fantasma is fantasma_comido:
            continue
        fantasma.Dibujar(mapa_surface)
    grupo_puntos_flotantes.draw(mapa_surface)
    if estado_juego == "ready":
        dibujar_ready(mapa_surface)
    elif estado_juego == "game_over":
        dibujar_game_over(mapa_surface)
    pantalla.blit(mapa_surface, (0, HUD_ARRIBA))
    HUD.dibujar_hud(pantalla, pacman, high_score, fuente)
    pg.display.flip()
pg.quit()