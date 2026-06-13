import pygame as pg
import entidades
Frutas_dic = {
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
    def __init__(self, x: int, y: int, nivel: int, tile_size : int = 18):
        super().__init__()
        self.x = x
        self.y = y
        self.tipo = self.obtener_tipo(nivel)
        self.puntos = Frutas_dic[self.tipo]["puntos"]
        self.tamaño_fruta = int(tile_size * 0.85)
        self.image = pg.image.load(f"fruits/{Frutas_dic[self.tipo]['imagen']}").convert_alpha()
        self.image = pg.transform.scale(self.image, (self.tamaño_fruta, self.tamaño_fruta)) # Para que este a escala.
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.tiempo_aparicion = pg.time.get_ticks()
        self.duracion_texto = 1000 # 1 segundo
        self.duracion_visible = 9000 # 9 segundos
        self.fuente_texto_puntos = pg.font.SysFont("Courier", 12, bold=True)
        self.comida = False
        self.sonido_fruta = pg.mixer.Sound("sonidos_pacman/eat_fruit.wav")
    
    def actualizar(self)->None:
        """actualiza el estado de la frutas 
        si la fruta no fue comida verifica si pasaron los 9 segundos de duracion, si ya fue comida
        verifica si paso el segundo donde se muestra la contidad de puntos 
        cuando se cumple uno de estos elimina la fruta del grupo de sprites 
        Retorna: 
            None"""
        tiempo_actual = pg.time.get_ticks()
        if not self.comida: # Si la fruta no fue comida, verificamos si pasaron los 9 segundos de vida.
            if tiempo_actual - self.tiempo_aparicion >= self.duracion_visible:
                self.kill()
        else: # Si la fruta fue comida, ahora estamos mostrando el texto de los puntos que aparece durante un segundo.
            if tiempo_actual - self.tiempo_comida >= self.duracion_texto:
                    self.kill() # Texto dsp de un segundo desaparece.
    
    def obtener_tipo(self,nivel: int)->str:
        """obtiene el tipo de fruta con respecto al nivel 
        para niveles iguales o mayores a 13 siempre devolvera 'key' 
        argumentos:
            nivel: numero de nivel actual
        Retorna:
            string con en nombre de la fruta"""
        if nivel >= 13:
            return "key"
        return frutas_nivel[nivel]

    def comer_frutas(self, pacman: object)->None:
        """Verifica si pacman comio la fruta 
        si pacman colisiona con la fruta se reproduce el sonido coresopondiente se guarda el tipo de fruta en una lista
        y se remplaza la imagen de la fruta por loos puntos dados
        Argumentos:
            Objeto pacman: protagonista del juego
        Retorna:
            None"""
        if self.comida:
            return        
        if pacman.rect.colliderect(self.rect):
            self.sonido_fruta.play()
            pacman.sumar_puntos(self.puntos)
            pacman.frutas_comidas.append(self.tipo)
            sonido_fruta = pg.mixer.Sound("sonidos_pacman/eat_fruit.wav")
            sonido_fruta.play()
            self.comida = True
            self.tiempo_comida = pg.time.get_ticks()
            self.image = self.fuente_texto_puntos.render(str(self.puntos), True, (255,184,255)) # Texto rosado puntos
            self.rect = self.image.get_rect(center=(self.x, self.y))