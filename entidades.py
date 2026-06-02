import pygame as pg
import math

class Criatura:
    def __init__(self,x,y,velocidad):
        self.x = x
        self.y = y
        self.velocidad = velocidad
        self.direccion = "quieto"
        self.radio = 18 # Radio de pixeles por default, tomando en cuenta el size del tile como 24x24 pixeles
    
    def mover(self):
        if self.direccion == "derecha":
            self.x += self.velocidad
        elif self.direccion == "izquierda":
            self.x -= self.velocidad
        elif self.direccion == "arriba":
            self.y -= self.velocidad
        elif self.direccion == "abajo":
            self.y += self.velocidad
    
    def obtener_hitbox(self):
        return pg.Rect(self.x - self.radio, self.y - self.radio, self.radio * 2, self.radio * 2)
         
class PacMan (Criatura):
    velocidad_normal = 0.80
    velocidad_super = 0.90
    def __init__(self, x, y):
        super().__init__(x, y, PacMan.velocidad_normal)
        self.vidas = 3
        self.puntaje = 0
        self.frame_animacion = 0 # frame_animacion = 0 - boca casi cerrada, frame_animacion = 5  - boca media abierta, frame_animacion = 10 - boca muy abierta
        self.boca_abriendo = True # True: boca se esta abriendo, False: boca se esta cerrando
        
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
        pg.draw.circle(pantalla, (255, 255, 0), centro, self.radio)
        apertura = 4 + self.frame_animacion # la boca siempre esta abierta por eso el 4
        if self.direccion == "derecha" or self.direccion == "quieto":
            boca = [centro, (self.x + self.radio, self.y - apertura), (self.x + self.radio, self.y + apertura)]
        elif self.direccion == "izquierda":
            boca = [centro, (self.x - self.radio, self.y - apertura), (self.x - self.radio, self.y + apertura)]
        elif self.direccion == "arriba":
            boca = [centro, (self.x - apertura, self.y - self.radio), (self.x + apertura, self.y - self.radio)]
        elif self.direccion == "abajo":
            boca = [centro, (self.x - apertura, self.y + self.radio), (self.x + apertura, self.y + self.radio)]
        pg.draw.polygon(pantalla, (0, 0, 0), boca)
    
    def actualizar_animacion(self):
        if self.direccion == "quieto":
            return
        if self.boca_abriendo:
            self.frame_animacion += 1
            if self.frame_animacion >= 10:
                self.boca_abriendo = False
        else:
            self.frame_animacion -= 1
            if self.frame_animacion <= 0:
                self.boca_abriendo = True
    
    def sumar_puntos(self,puntos):
        self.puntaje += puntos
    
    def perder_vida(self):
        self.vidas -= 1
        self.direccion = "quieto"

    def esta_vivo(self): # Para saber si murió PacMan
        return self.vidas > 0

    def activar_super(self):
        self.velocidad = PacMan.velocidad_super
    
    def desactivar_super(self):
        self.velocidad = PacMan.velocidad_normal
    
    def reiniciar_posicion(self, x, y): # Volver a posición inicial
        self.x = x
        self.y = y
        self.direccion = "quieto"
        self.frame_animacion = 0
        self.boca_abriendo = True
    
    def choca_con(self, otra_criatura): # Para Pacman vs Fantasmas
        return self.obtener_hitbox().colliderect(otra_criatura.obtener_hitbox()) # True o False
    

class Fantasma(Criatura):
    velocidad_normal = 0.75
    velocidad_asustado = 0.50
    velocidad_ojos = 1.50
    def __init__(self, x, y, nombre, color, esquina_scatter,pos_Pc):
        super().__init__(x, y, Fantasma.velocidad_normal)
        self.nombre = nombre
        self.color = color
        self.esquina_scatter = esquina_scatter
        self.pos_Pc = pos_Pc
        self.estado = "scatter"  
        self.direccion = "en_casa"
        self.norma = x**2 + y**2

    def calcular_Dist(self,tile=24):
        origen = pg.math.Vector2((self.x,self.y))
        destino = pg.math.Vector2 (self.pos_Pc)
        diff = origen - destino
        Dist = math.sqrt((diff.magnitude_squared()))
        return Dist
    
 
class Clyde (Fantasma):
    def __init__(self, x, y, nombre, color, esquina_scatter):
        super().__init__(x, y, "Clyde", (255,165,0), esquina_scatter, self.pos_Pc)
        self.nombre = "Clyde"
        self.color = "Naranja"
        self.esquina_scatter = esquina_scatter
        self.Dist = self.calcular_Dist(self)
        