import pygame as pg

TILE_SIZE = 18
MAPA_ANCHO = 28 * TILE_SIZE
MAPA_ALTO = 31 * TILE_SIZE
ANCHO = MAPA_ANCHO # Para transformar las imagenes
HUD_ARRIBA = 75
HUD_ABAJO = 45
ALTO = HUD_ARRIBA + MAPA_ALTO + HUD_ABAJO

class Intermission:
    def __init__(self):
        self.frames_intermission_1 = []
        self.frames_intermission_2 = []
        self.frames_intermission_3 = []
        self.cantidad_frames = 300
        self.frame_intermission_actual = 0
        self.tiempo_inicio_intermission = 0
        self.duracion_intermission = 10500
        self.sonido_intermission = pg.mixer.Sound("sonidos_pacman/intermission.wav")

    def cargar_frames_intermission_1(self, nivel): # Faltan los otros niveles.
            self.frames_intermission_1 = []
            self.frames_intermission_2 = []
            self.frames_intermission_3 = []
            if nivel == 3:
                for i in range(300):
                    imagen = pg.image.load(f"intermission_1/frame_{i:03}.png").convert_alpha()
                    imagen = pg.transform.scale(imagen, (ANCHO, ALTO))
                    canvas = pg.Surface((ANCHO, ALTO))
                    canvas.fill((0, 0, 0))
                    # Ajuste estos valores hasta centrarlo a los pngs
                    o_x = 0
                    o_y = -70 
                    canvas.blit(imagen, (o_x, o_y))
                    self.frames_intermission_1.append(canvas)
            elif nivel == 6:
                for i in range(300):
                    imagen = pg.image.load(f"intermission_2/frame_{i:03}.png").convert_alpha()
                    imagen = pg.transform.scale(imagen, (ANCHO, ALTO))
                    canvas = pg.Surface((ANCHO, ALTO))
                    canvas.fill((0, 0, 0))
                    # Ajuste estos valores hasta centrarlo a los pngs
                    o_x = 0
                    o_y = -20 
                    canvas.blit(imagen, (o_x, o_y))
                    self.frames_intermission_2.append(canvas)
            elif nivel == 10 or nivel == 14 or nivel == 18:
                for i in range(300):
                    imagen = pg.image.load(f"intermission_3/frame_{i:03}.png").convert_alpha()
                    imagen = pg.transform.scale(imagen, (ANCHO, ALTO))
                    canvas = pg.Surface((ANCHO, ALTO))
                    canvas.fill((0, 0, 0))
                    # Ajuste estos valores hasta centrarlo a los pngs
                    o_x = 0
                    o_y = -50 
                    canvas.blit(imagen, (o_x, o_y))
                    self.frames_intermission_3.append(canvas)
                
    def iniciar_intermission(self):   
        self.frame_intermission_actual = 0
        self.tiempo_inicio_intermission = pg.time.get_ticks()
        self.sonido_intermission.play(-1)
        
    def actualizar_intermission(self):
        tiempo_actual = pg.time.get_ticks()
        tiempo_transcurrido = tiempo_actual - self.tiempo_inicio_intermission
        porcentaje = tiempo_transcurrido / self.duracion_intermission # Para calcular que porcentaje de la animacion va
        self.frame_intermission_actual = int(porcentaje * self.cantidad_frames) # Para ver que frame se dibuja dependiendo del porcentaje de la animacion len(self.frames_intermission_1) = al de 2
        if self.frame_intermission_actual >= self.cantidad_frames:
            self.frame_intermission_actual = self.cantidad_frames -1
            self.sonido_intermission.stop()
            return True # La intermission termino
        return False
    
    def dibujar_intermission(self, pantalla, nivel):
        if nivel == 3 and len(self.frames_intermission_1) > 0:
            imagen = self.frames_intermission_1[self.frame_intermission_actual]
            pantalla.blit(imagen, (0, 0))
        elif nivel == 6 and len(self.frames_intermission_2) > 0:
            imagen = self.frames_intermission_2[self.frame_intermission_actual]
            pantalla.blit(imagen, (0, 0))
        elif (nivel == 10 or nivel == 14 or nivel == 18) and len(self.frames_intermission_3) > 0:
            imagen = self.frames_intermission_3[self.frame_intermission_actual]
            pantalla.blit(imagen, (0, 0))
            