import pygame as pg

class Criatura:
    def __init__(self,x,y,velocidad):
        self.x = x
        self.y = y
        self.velocidad = velocidad
        self.direccion = "quieto"
    
    def mover(self):
        if self.direccion == "derecha":
            self.x += self.velocidad
        elif self.direccion == "izquierda":
            self.x -= self.velocidad
        elif self.direccion == "arriba":
            self.y -= self.velocidad
        elif self.direccion == "abajo":
            self.y += self.velocidad
            
class PacMan (Criatura):
    velocidad_normal = 0.80
    velocidad_super = 0.90
    def __init__(self, x, y):
        super().__init__(x, y, PacMan.velocidad_normal)
        self.vidas = 3
        self.puntaje = 0
        self.radio = 18 # Radio de pixeles por default, tomando en cuenta el size del tile como 24x24 pixeles
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

class Fantasma(Criatura):
    velocidad_normal = 0.75
    velocidad_asustado = 0.50
    velocidad_ojos = 1.50
    def __init__(self, x, y, nombre, color, esquina_scatter):
        super().__init__(x, y, Fantasma.velocidad_normal)
        self.nombre = nombre
        self.color = color
        self.esquina_scatter = esquina_scatter
        self.estado = "scatter"  
        self.direccion = "en_casa"
        self.radio = 18
