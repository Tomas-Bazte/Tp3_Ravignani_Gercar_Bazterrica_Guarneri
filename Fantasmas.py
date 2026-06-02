from entidades import Criatura
import math
import pygame as pg

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