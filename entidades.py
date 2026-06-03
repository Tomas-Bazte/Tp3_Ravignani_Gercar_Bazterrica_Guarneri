import pygame as pg
import math

TILE_SIZE = 24

class Criatura:
    def __init__(self,x,y,velocidad):
        self.x = x
        self.y = y
        self.velocidad = velocidad # tiles/segundo
        self.direccion = "quieto"
        self.radio = 9.5 # Radio de pixeles por default, tomando en cuenta el size del tile como 24x24 pixeles
    
    def mover(self, dt, tile_size=24):  # dt = tiempo transcurrido desde el ultimo frame (en segundos). Permite usar tiles/segundos
        desplazamiento = self.velocidad * tile_size * dt
        if self.direccion == "derecha":
            self.x += desplazamiento
        elif self.direccion == "izquierda":
            self.x -= desplazamiento
        elif self.direccion == "arriba":
            self.y -= desplazamiento
        elif self.direccion == "abajo":
            self.y += desplazamiento
    
    def obtener_hitbox(self):
        return pg.Rect(self.x - self.radio, self.y - self.radio, self.radio * 2, self.radio * 2)
         
class PacMan (Criatura):
    velocidad_normal = 6 # 80 % de 7.5 - tiles/segundo
    velocidad_super = 6.75 # 90 % de 7.5
    def __init__(self, x, y):
        super().__init__(x, y, PacMan.velocidad_normal)
        self.vidas = 3
        self.puntaje = 0
        self.estado = "normal" # normal, muriendo
        self.frame_animacion = 0 # frame_animacion = 0 - boca casi cerrada, frame_animacion = 5  - boca media abierta, frame_animacion = 10 - boca muy abierta
        self.frame_min_boca = 0
        self.frame_max_boca = 10
        self.velocidad_animacion_boca = 1
        self.frames_muerte = []
        self.frame_muerte_actual = 0
        self.tiempo_ultimo_frame_muerte = 0
        self.duracion_entre_frames_muerte = 2500 // 13 # 2500 milisegundos = 2.5 segundos entre 13 frames, como pacman original
        self.boca_abriendo = True # True: boca se esta abriendo, False: boca se esta cerrando
        self.vida_extra_dada = False # A los 10k puntos se devuelve una vida, pasa solamente una vez.
        self.modo_super = False
        self.tiempo_super_inicio = 0
        self.duracion_super = 6000 # milisegundos = 6 segundos
        self.sonido_muerte = pg.mixer.Sound("sonidos_pacman/death_0.wav")
        self.sonido_dot_0 = pg.mixer.Sound("sonidos_pacman/eat_dot_0.wav")
        self.sonido_dot_1 = pg.mixer.Sound("sonidos_pacman/eat_dot_1.wav")
        self.sonido_fright = pg.mixer.Sound("sonidos_pacman/fright.wav")
        self.alternar_sonido_dot = 0
        
    def cambiar_direccion(self, tecla):
        if tecla == pg.K_RIGHT:
            self.direccion = "derecha"
        elif tecla == pg.K_LEFT:
            self.direccion = "izquierda"
        elif tecla == pg.K_UP:
            self.direccion = "arriba"
        elif tecla == pg.K_DOWN:
            self.direccion = "abajo"
            
    def dibujar(self, pantalla):
        centro = (int(self.x), int(self.y))
        if self.estado == "muriendo":
            if self.frame_muerte_actual < len(self.frames_muerte):
                imagen = self.frames_muerte[self.frame_muerte_actual]
                imagen = pg.transform.rotate(imagen, 270) # La animacion de la muerte es con la boca mirando para arriba
                rect = imagen.get_rect(center = centro)
                pantalla.blit(imagen, rect)
            return
        pg.draw.circle(pantalla, (255, 255, 0), centro, self.radio)
        if self.frame_animacion<1:
            return
        if self.direccion == "derecha" or self.direccion == "quieto":
            boca = [centro, (self.x + self.radio, self.y - self.frame_animacion), (self.x + self.radio, self.y + self.frame_animacion)]
        elif self.direccion == "izquierda":
            boca = [centro, (self.x - self.radio, self.y - self.frame_animacion), (self.x - self.radio, self.y + self.frame_animacion)]
        elif self.direccion == "arriba":
            boca = [centro, (self.x - self.frame_animacion, self.y - self.radio), (self.x + self.frame_animacion, self.y - self.radio)]
        elif self.direccion == "abajo":
            boca = [centro, (self.x - self.frame_animacion, self.y + self.radio), (self.x + self.frame_animacion, self.y + self.radio)]
        pg.draw.polygon(pantalla, (0, 0, 0), boca)
    
    def actualizar_animacion(self):
        if self.direccion == "quieto":
            return
        if self.boca_abriendo:
            self.frame_animacion += self.velocidad_animacion_boca
            if self.frame_animacion >= self.frame_max_boca:
                self.frame_animacion = self.frame_max_boca
                self.boca_abriendo = False
        else:
            self.frame_animacion -= self.velocidad_animacion_boca
            if self.frame_animacion <= self.frame_min_boca:
                self.frame_animacion = self.frame_min_boca
                self.boca_abriendo = True
    
    def sumar_puntos(self,puntos):
        self.puntaje += puntos
        if self.puntaje >= 10000 and not self.vida_extra_dada:
            self.vidas += 1
            self.vida_extra_dada = True
    
    def perder_vida(self):
        if self.vidas > 0:
            self.vidas -= 1
        self.direccion = "quieto"

    def esta_vivo(self): # Para saber si murió PacMan
        return self.vidas > 0

    def activar_super(self):
        self.modo_super = True
        self.tiempo_super_inicio = pg.time.get_ticks()
        self.velocidad = PacMan.velocidad_super
        self.sonido_fright.play(loops=-1)
    
    def desactivar_super(self):
        self.modo_super = False
        self.velocidad = PacMan.velocidad_normal
        self.sonido_fright.stop()
    
    def actualizar_super(self):
        if self.modo_super:
            tiempo_actual = pg.time.get_ticks()
            
            if tiempo_actual - self.tiempo_super_inicio >= self.duracion_super:
                self.desactivar_super()
                
    def reiniciar_posicion(self, x, y): # Volver a posición inicial
        self.x = x
        self.y = y
        self.direccion = "quieto"
        self.frame_animacion = 0
        self.boca_abriendo = True
    
    def choca_con(self, otra_criatura): # Para Pacman vs Fantasmas
        return self.obtener_hitbox().colliderect(otra_criatura.obtener_hitbox()) # True o False
    
    def comer_punto(self):
        self.sumar_puntos(10)
        if self.alternar_sonido_dot == 0:
            self.sonido_dot_0.play()
            self.alternar_sonido_dot = 1
        else:
            self.sonido_dot_1.play()
            self.alternar_sonido_dot = 0
    
    def comer_power_pellet(self):
        self.sumar_puntos(50)
        self.activar_super()
    
    def iniciar_muerte(self):
        self.estado = "muriendo"
        self.direccion = "quieto"
        self.frame_muerte_actual = 0
        self.tiempo_ultimo_frame_muerte = pg.time.get_ticks()
        self.sonido_muerte.play()
    
    def actualizar_muerte(self):
        if self.estado != "muriendo":
            return False
        tiempo_ahora = pg.time.get_ticks()
        if tiempo_ahora - self.tiempo_ultimo_frame_muerte >= self.duracion_entre_frames_muerte:
            self.frame_muerte_actual += 1
            self.tiempo_ultimo_frame_muerte = tiempo_ahora
        if self.frame_muerte_actual >= len(self.frames_muerte):
            self.perder_vida()
            self.estado = "normal"
            return True
        return False
    
    def cargar_frames_muerte(self):
        self.frames_muerte = []

        for i in range(13):
            imagen = pg.image.load(f"pacman_muerte/pacman_death_{i:02}.png").convert_alpha()
            imagen = pg.transform.scale(imagen, (self.radio * 2.8, self.radio * 2.8)) # 2.8 es una escala aproximada para que la imagen quede del mismo tamaño que el PacMan
            self.frames_muerte.append(imagen)
    
   