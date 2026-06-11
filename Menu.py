from HUD import cargar_high_score
import pygame as pg
from entidades import TILE_SIZE
from Mapa import MAPA_ALTO , MAPA_ANCHO , ANCHO , ALTO , HUD_ABAJO ,HUD_ARRIBA

High = str(cargar_high_score())

ROJO = (255, 0, 0)
ROSA = (255, 184, 255)
CELESTE = (0, 255, 255)
NARANJA = (255, 184, 82)
VERDE = (0, 255, 0)
VIOLETA = (128, 0, 128)
AMARILLO = (255, 255, 0)
BLANCO = (255, 255, 255)
GRIS = (150, 150, 150)
NEGRO = (0,0,0)
GRIS_O = (50, 50, 50)

FANTASMAS = [
    {"id": 1, "nombre": "Blinky", "color": ROJO, "desc": "- El perseguidor."},
    {"id": 2, "nombre": "Pinky", "color": ROSA, "desc": "- El emboscador."},
    {"id": 3, "nombre": "Inky", "color": CELESTE, "desc": "- El flanqueador."},
    {"id": 4, "nombre": "Clyde", "color": NARANJA, "desc": "- El tímido."},
    {"id": 5, "nombre": "#Aca va el nombre", "color": GRIS_O, "desc": "- La sombra"},
    {"id": 6, "nombre": "Spark", "color": AMARILLO, "desc": "- El doble cara"}
]


def menu_inicio(pantalla):
    fuente_titulo = pg.font.SysFont("Courier", 50, bold=True)
    fuente_normal = pg.font.SysFont("Courier", 20, bold=True)
    fuente_chica = pg.font.SysFont("Courier", 16, bold=False)
    menu = True
    seleccionados = []
    Esquinas = {}
    Esquinas_actual = 0
    estado_actual = "Inicio"
    while menu:
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                pg.quit()
                exit()
            if evento.type == pg.KEYDOWN:
                if estado_actual == "Inicio":
                    if evento.key == pg.K_RETURN:
                        estado_actual = "Seleccion"
                elif estado_actual == "Seleccion":
                    if pg.K_1 <= evento.key <= pg.K_6:
                            id_elegido = evento.key - pg.K_1 + 1
                            if id_elegido in seleccionados:
                                seleccionados.remove(id_elegido)
                            elif len(seleccionados) < 4:
                                seleccionados.append(id_elegido)
                    elif evento.key == pg.K_RETURN:
                            if len(seleccionados) == 4:
                                estado_actual = "asignacion"
                                Esquinas_actual = 0
                elif estado_actual == "asignacion":
                    if pg.K_1 <= evento.key <= pg.K_4:
                        Esquinas_Elegida = evento.key - pg.K_1 + 1
                        Fantama = seleccionados[Esquinas_actual]
                        Esquinas[Fantama] = Esquinas_Elegida
                        Esquinas_actual += 1
                        if estado_actual >= 4:
                            return Esquinas , seleccionados
            

        pantalla.fill(NEGRO)

        if estado_actual == "Inicio":
            texto_puntaje = fuente_normal.render("High Score: ",True,GRIS)
            cantidad = fuente_chica.render(High,True,AMARILLO)
            pantalla.blit(texto_puntaje,texto_puntaje.get_rect(center= ((ANCHO//2),ALTO//2+200)))
            pantalla.blit(cantidad,cantidad.get_rect(center=(ANCHO//2,ALTO//2+250)))
            titulo = fuente_titulo.render("PAC-MAN", True, AMARILLO)
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO//2, ALTO//2 - 50)))

            tiempo = pg.time.get_ticks()
            if (tiempo//500) % 2 == 0:
                txt_jugar = fuente_normal.render("Presioná ENTER para jugar", True, BLANCO)
            else:
                txt_jugar = fuente_normal.render("Presioná ENTER para jugar", True, NEGRO)
            pantalla.blit(txt_jugar, txt_jugar.get_rect(center=(ANCHO//2, ALTO//2 + 50)))

        elif estado_actual == "Seleccion":
            titulo = fuente_normal.render(f"Elija hasta 4 Fantasmas: {len(seleccionados)}/4",False,BLANCO)
            pantalla.blit (titulo,titulo.get_rect(center=(ANCHO//2,60)))
            Y_primerF = 120
            espaciado = 60
            for i,fantasma in enumerate(FANTASMAS):
                y_actual = Y_primerF + (i * espaciado)
                x_centro = ANCHO // 2
                if fantasma["id"] in seleccionados:
                    pg.draw.rect(pantalla, BLANCO, (x_centro - 150, y_actual - 25, 350, 50), 2)
                num = fuente_normal.render(str(fantasma["id"]), True, BLANCO)
                pantalla.blit(num, (x_centro - 130, y_actual - 10))
                pg.draw.circle(pantalla, fantasma["color"], (x_centro -90, y_actual), 12)
                nombre = fuente_normal.render(fantasma["nombre"],True,GRIS)
                descrip = fuente_normal.render(fantasma["desc"],True,GRIS)
                pantalla.blit(nombre, (x_centro - 50, y_actual - 20))
                pantalla.blit(descrip, (x_centro - 50, y_actual +2))

        elif estado_actual == "asignacion":
            for fantasma in seleccionados:
                titulo = fuente_normal.render(f"Elija la esquina para {fantasma["nombre"]}:",False,BLANCO)
                pantalla.blit (titulo,titulo.get_rect(center=(ANCHO//2,60)))
                





        pg.display.flip()