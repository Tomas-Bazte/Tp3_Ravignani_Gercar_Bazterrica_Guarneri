import pygame as pg
Frutas = {
 "cherry" : {
"imagen" : "cherry.png",
"puntos": 100
}
, "strawberry" : {
"imagen" : "strawberry.png",
"puntos": 300
}
, "orange" : {
"imagen": "orange.png",
"puntos": 500
}
, "apple": {
    "imagen" : "apple.png",
    "puntos" : 700
}
, "melon" : {
    "imagen" : "melon.png",
    "puntos" : 1000
},
"galaxian" : {
    "imagen" : "galaxian.png",
    "puntos" : 2000
},
"bell": {
    "imagen" : "bell.png",
    "puntos" : 3000
},
"key": {
"imagen" : "key.png",
"puntos" : 5000
}
}
frutas_nivel = {
                1: "cherry",
                2: "strawberry", 
                3: "orange",
                4: "orange",
                5 :"apple",
                6 : "apple",
                7: "melon",
                8: "melon",
                9: "galaxian",
                10: "galaxian",
                11:"bell",
                12: "bell",
                13 : "key"
                }
class Frutas(pg.sprite.Sprite):
    def __init__(self, x, y, Frutas):
        super().__init__()
        self.x = x
        self.y = y
        self.tipo = 0 # lo detectara solo cuando tengamos el numero de nivel
        self. puntos = Frutas[self.tipo]["puntos"]
        self.imagen = Frutas[self.tipo]["imagen"]

    def obtener_frutas_nivel(self, nivel, frutas_nivel):
        if nivel > 12:
            self.tipo = "key"
        else:
            self.tipo = frutas_nivel[nivel]
    


