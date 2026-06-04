from entidades import Criatura
import math
import pygame as pg
import random

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

    def definir_estado(self):
        if self.estado == 'scatter':
            objx, objy = self.esquina_scatter
            self.velocidad = self.velocidad_normal
        elif self.estado == 'chase':
            objx, objy = self.pos_Pc
            self.velocidad = self.velocidad_normal
        elif self.estado == 'asustado':
            objx, objy = self.pos_Pc
        if abs(objx - self.x) == abs(objy - self.y): # Si la distancia al objetivo es la misma en eje x e y
            eleccion = random.choice(['x','y'])
            if eleccion == 'x':
                if self.x > objx:
                    self.direccion = 'izquierda'
                elif self.x < objx:
                    self.direccion = 'derecha'
            elif eleccion == 'y':
                if self.y > objy:
                    self.direccion = 'arriba'
                elif self.y < objy:
                    self.direccion = 'abajo'
        elif abs(objx - self.x) > abs(objy - self.y): # Si la distancia en el eje x es mayor se mueve en x
            if self.x > objx:
                self.direccion = 'izquierda'
            elif self.x < objx:
                self.direccion = 'derecha'
        elif abs(objy - self.y) > abs(objx - self.x): #Si la distancia en el eje y es mayor entonces se mueve en el eje y 
            if self.y > objy:
                self.direccion = 'arriba'
            elif self.y < objy:
                self.direccion = 'abajo'
        return self.direccion

    def asustado(self):
        self.estado = 'asustado'
        self.velocidad = self.velocidad_asustado
        direccion = self.definir_estado()
        if direccion == 'derecha':
            self.ndir = 'izquierda'
        elif direccion == 'izquierda':
            self.ndir = 'derecha'
        elif direccion == 'arriba':
            self.ndir = 'abajo'
        else:
            self.ndir = 'arriba'
        return self.ndir

    def ejecutar_movimientos(self):
        if self.estado == 'scatter' or self.estado == 'chase':
            direccion = self.definir_estado()
        elif self.estado == 'asustado':
            direccion = self.asustado()
        if direccion == 'derecha':
             self.x += self.velocidad
        elif direccion == 'izquierda':
             self.x -= self.velocidad
        elif direccion == 'arriba':
             self.y -= self.velocidad
        else:
             self.y += self.velocidad

class Clyde (Fantasma):
    def __init__(self, x, y, nombre, color, esquina_scatter):
        super().__init__(x, y, "Clyde", (255,165,0), esquina_scatter, self.pos_Pc)
        self.nombre = "Clyde"
        self.color = "Naranja"
        self.esquina_scatter = esquina_scatter
        self.Dist = self.calcular_Dist(self)