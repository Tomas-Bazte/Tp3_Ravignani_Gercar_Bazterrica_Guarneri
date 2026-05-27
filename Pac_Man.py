import pygame as pg

class Criatura:
    def __init__(self,pos_x,pos_y,Velocidad):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.velocidad = Velocidad
        pass

class Pac_Man (Criatura):
    def __init__(self, pos_x, pos_y, Velocidad,Vidas,Direccion):
        super().__init__(pos_x, pos_y, Velocidad)
        self.vidas = Vidas
        self.direccion = Direccion
        self.forma = pg.Surface((40,40),pg.SRCALPHA)
        pg.draw.polygon(self.forma,(0,0,0),[(20,20),(40,10),(40,30)])
        self.animaciones = {
            'Derecha': self.forma,
            'Arriba':pg.transform.rotate(self.forma, 90),
            'Izquierda':pg.transform.rotate(self.forma, 180),
            'Abajo':pg.transform.rotate(self.forma, 270),
        }
