import pygame as pg

FRUTAS_HUD = {}
ARCHIVO_HIGH_SCORE = "high_score.txt"

def cargar_frutas_hud():
    global FRUTAS_HUD
    FRUTAS_HUD = {
        "cherry": pg.image.load("fruits/cherry.png").convert_alpha(),
        "strawberry": pg.image.load("fruits/strawberry.png").convert_alpha(),
        "orange": pg.image.load("fruits/orange.png").convert_alpha(),
        "apple": pg.image.load("fruits/apple.png").convert_alpha(),
        "melon": pg.image.load("fruits/melon.png").convert_alpha(),
        "galaxian": pg.image.load("fruits/galaxian.png").convert_alpha(),
        "bell": pg.image.load("fruits/bell.png").convert_alpha(),
        "key": pg.image.load("fruits/key.png").convert_alpha()
    }
    for fruta in FRUTAS_HUD:
        FRUTAS_HUD[fruta] = pg.transform.scale(FRUTAS_HUD[fruta],(24, 24))

def cargar_high_score():
    try:
        with open(ARCHIVO_HIGH_SCORE, "r") as archivo:
            return int(archivo.read())
    except:
        return 0

def guardar_high_score(puntaje):
    with open(ARCHIVO_HIGH_SCORE, "w") as archivo:
        archivo.write(str(puntaje))

def actualizar_high_score(pacman, high_score):
    if pacman.puntaje > high_score:
        high_score = pacman.puntaje
        guardar_high_score(high_score)
    return high_score

def dibujar_hud_arriba(pantalla, pacman, fuente, high_score):
    w = pantalla.get_width()
    tiempo = pg.time.get_ticks()
    if (tiempo // 300) % 2 == 0:
        texto_1up = fuente.render("1UP", True, (255, 255, 255))  # Devuelve un pygame.Surface. El true es para los bordes suaves del texto
    else:
        texto_1up = fuente.render("1UP", True, (0, 0, 0))
    texto_score = fuente.render(str(pacman.puntaje).rjust(7), True, (255, 255, 255)) # rjust(7) lo uso considerando el maximo score posible de PacMan
    texto_high = fuente.render("HIGH SCORE", True, (255, 255, 255))
    texto_high_score = fuente.render(str(high_score).rjust(7), True, (255, 255, 255))
    pantalla.blit(texto_1up, (w*0.10, 5)) # Dibuja al texto_1up en la posicion (85,5)
    pantalla.blit(texto_score, (w*0.001, 32))
    pantalla.blit(texto_high, (w*0.55, 5))
    pantalla.blit(texto_high_score, (w*0.60, 32))

def dibujar_hud_abajo(pantalla, pacman):
    y = pantalla.get_height() - 22
    x_inicial = 20
    for i in range(pacman.vidas):
        x = x_inicial + i * 28 # Para separar pixeles entre cada PacMan
        pg.draw.circle(pantalla, (255, 255, 0), (x, y), 10)
        # Boca mirando a la izquierda
        boca = [(x, y),(x - 10, y - 5),(x - 10, y + 5)]
        pg.draw.polygon(pantalla, (0, 0, 0), boca)

def dibujar_frutas_hud(pantalla, pacman):
    y = pantalla.get_height() - 36 # Fui probando hasta donde quede perfecto
    frutas_visibles = pacman.frutas_comidas[-7:]
    x = pantalla.get_width() - 32
    for fruta in reversed(frutas_visibles): # reversed para q aparezca la fruta comida primero mas hacia la derecha
        pantalla.blit(FRUTAS_HUD[fruta],(x, y))
        x = x - 28 # Pixeles entre frutas.

def dibujar_hud(pantalla, pacman, high_score, fuente):
    dibujar_hud_arriba(pantalla,pacman,fuente,high_score)
    dibujar_hud_abajo(pantalla,pacman)
    dibujar_frutas_hud(pantalla,pacman)