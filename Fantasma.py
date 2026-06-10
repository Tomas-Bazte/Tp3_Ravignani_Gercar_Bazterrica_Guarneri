from entidades import Criatura
import pygame as pg
import random

TILE_SIZE = 18

class Fantasma(Criatura):
    velocidad_normal = 2
    velocidad_asustado = 1
    velocidad_ojos = 3
    
    def __init__(self, x, y, nombre, color, esquina_scatter, pos_Pc):
        super().__init__(x, y, Fantasma.velocidad_normal)
        self.nombre = nombre
        self.color = color
        self.esquina_scatter = esquina_scatter
        self.pos_Pc = pos_Pc
        self.estado = "scatter"  
        self.direccion = "derecha" 
        self.rect = pg.Rect(x, y, TILE_SIZE, TILE_SIZE)

    def analizar_colisiones(self):
        hitbox_fantasma = self.rect.copy()
        if self.direccion == 'derecha':
            hitbox_fantasma.x += self.velocidad
        elif self.direccion == 'izquierda':
            hitbox_fantasma.x -= self.velocidad
        elif self.direccion == 'arriba':
            hitbox_fantasma.y -= self.velocidad
        elif self.direccion == 'abajo':
            hitbox_fantasma.y += self.velocidad
        return bool(hitbox_fantasma.collideobjects(self.grupo_Paredes))
    
    def analizar_movimientos(self, choca):
        if choca or (self.x % TILE_SIZE == 0 and self.y % TILE_SIZE == 0):
            if self.estado == 'asustado':
                self.direccion = self.asustado()
            else:
                self.direccion = self.definir_estado()

    def definir_estado(self):
        if self.estado == 'scatter':
            objx, objy = self.esquina_scatter
            self.velocidad = self.velocidad_normal
        elif self.estado == 'chase':
            objx, objy = self.pos_Pc
            self.velocidad = self.velocidad_normal
        direccion = self.direccion
        if abs(objx - self.x) > abs(objy - self.y): 
            if self.x > objx:
                direccion = 'izquierda' 
            elif self.x < objx:
                direccion ='derecha'
        elif abs(objy - self.y) > abs(objx - self.x): 
            if self.y > objy: 
                direccion = 'arriba' 
            elif self.y < objy:
                direccion ='abajo'
        if self.analizar_colisiones(): 
            opciones = ['derecha', 'izquierda', 'arriba', 'abajo']
            if direccion in opciones: 
                opciones.remove(direccion)
            for o in opciones:
                self.direccion = o
                if not self.analizar_colisiones():
                    break
        return self.direccion

    def asustado(self):
        self.estado = 'asustado'
        self.velocidad = self.velocidad_asustado
        opciones = ['derecha', 'izquierda', 'arriba', 'abajo']
        self.direccion = random.choice(opciones)
        for o in opciones:
            self.direccion = o
            if not self.analizar_colisiones():
                return o
        return self.direccion

    def ejecutar_movimientos(self):
        choca = self.analizar_colisiones()
        self.analizar_movimientos(choca)
        if self.analizar_colisiones():
            return self.x, self.y
        if self.direccion == 'derecha':
            self.x += self.velocidad
        elif self.direccion == 'izquierda': 
            self.x -= self.velocidad
        elif self.direccion == 'arriba':
            self.y -= self.velocidad
        elif self.direccion == 'abajo':
            self.y += self.velocidad
        self.rect.x = self.x
        self.rect.y = self.y        
        return self.x, self.y
    
class Clyde(Fantasma):
    def __init__(self, x, y, pos_Pc):
        super().__init__(x, y, 'Clyde', 'naranja', (0, 0), pos_Pc)


class Blinky(Fantasma):
    def __init__(self, x, y, pos_Pc):
        super().__init__(x, y, 'Blinky', 'rojo', (0, 0), pos_Pc)


class Pinky(Fantasma):
    def __init__(self, x, y, pos_Pc):
        super().__init__(x, y, 'Pinky', 'rosa', (0, 0), pos_Pc)


class Inky(Fantasma):
    def __init__(self, x, y, pos_Pc):
        super().__init__(x, y, 'Inky', 'celeste', (0, 0), pos_Pc)