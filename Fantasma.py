import pygame as pg
import Pac_Man
class Fantasma(Pac_Man.Criatura):
    def __init__(self, nombre, color, x, y, target, modo):
        self.nombre = nombre
        self.color = color
        self.pos_x = x
        self.pos_y = y
        self.target = target 
        self.modo = modo
    def 