from entidades import Criatura, TILE_SIZE
import pygame as pg
import random

Estado = [7000, 20000, 7000, 20000, 5000, 20000, 5000]
direcciones_default = {
    'derecha': (1,0),
    'izquierda': (-1,0),
    'arriba': (0,-1),
    'abajo': (0,1)
}
opuesto = {'derecha':'izquierda', 'izquierda': 'derecha', 'arriba': 'abajo', 'abajo': 'arriba'}

class Fantasma(Criatura):
    velocidad_normal = 0.75
    velocidad_asustado = 0.50
    velocidad_ojos = 1.50
    
    def __init__(self, x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes):
        super().__init__(x, y, Fantasma.velocidad_normal)
        self.nombre = nombre
        self.color = color
        self.esquina_scatter = esquina_scatter
        self.pos_Pc = pos_Pc
        self.estado = "scatter"  
        self.rect = pg.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.estado_actual = 0
        self.tiempo_estado = pg.time.get_ticks()
        self.xr = float(x)
        self.yr = float(y)
        self.casa = (x_casa, y_casa)
        self.grupo_Paredes = grupo_Paredes
        self.frame_actual = 0
        self.tiempo_frame = pg.time.get_ticks()
        self.duracion_frame = 200
        self.sprites_compartidos = {
            'asustado': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Asustado/Arcade - Pac-Man - General Sprites - Blue Ghost (1)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Asustado/Arcade - Pac-Man - General Sprites - Blue Ghost (1)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Asustado/Arcade - Pac-Man - General Sprites - White Ghost_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Asustado/Arcade - Pac-Man - General Sprites - White Ghost_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE))
            ],
            'ojos_derecha': pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Ojos/Ojos_derecha.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            'ojos_izquierda': pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Ojos/Ojos_izquierda.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            'ojos_arriba': pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Ojos/Ojos_arriba.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            'ojos_abajo': pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Ojos/Ojos_abajo.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        }

    def definir_objetivo(self):
        None

    def analizar_colisiones(self):
        avance = max(1, int(self.velocidad))
        direcciones_libres = {}
        Direcciones = {
            'derecha': (avance, 0),
            'izquierda': (-avance, 0),
            'arriba': (0, -avance),
            'abajo': (0, avance)
        }
        for direccion, (x,y) in Direcciones.items():
            hitbox_fantasma = self.rect.move(x,y)
            colision = bool(hitbox_fantasma.collideobjects(self.grupo_Paredes))
            direcciones_libres[direccion] = not colision
        return direcciones_libres
    
    def direcciones(self, objetivo):
        direcciones_libres = self.analizar_colisiones()
        posibles_posiciones = {}
        for direccion, disponible in direcciones_libres.items():
            if not disponible or direccion == opuesto[self.direccion]:
                continue
            x, y = direcciones_default[direccion]
            proxima_posicion = (self.rect.x + x, self.rect.y + y)
            distancia = (objetivo[0] - proxima_posicion[0])**2 + (objetivo[1] - proxima_posicion[1])**2
            posibles_posiciones[direccion] = distancia
        return min(posibles_posiciones, key=posibles_posiciones.get)

    def estados(self):
        if self.estado == 'scatter':
            self.velocidad = self.velocidad_normal
            objetivo = self.esquina_scatter
        elif self.estado == 'chase':
            self.velocidad = self.velocidad_normal
            objetivo = self.definir_objetivo()
        elif self.estado == 'muerto':
            self.velocidad = self.velocidad_ojos
            objetivo = self.casa
        elif self.estado == 'asustado':
            self.asustado()
            return
        self.direccion = self.direcciones(objetivo)

    def activar_asustado(self):
        self.estado = 'asustado'
        self.velocidad = self.velocidad_asustado
        self.direccion = opuesto[self.direccion]

    def asustado(self):
        Direccion = []
        posibles_direcciones = self.analizar_colisiones()
        for direccion in posibles_direcciones.keys():
            if posibles_direcciones[direccion]:
                if direccion == opuesto[self.direccion]:
                    continue
                Direccion.append(direccion)
        self.direccion = random.choice(Direccion)

    def muerto(self):
        self.estado = 'muerto'

    def alternar_estado(self):
        if self.estado == 'asustado':
            return
        if self.estado == 'muerto':
            if self.rect.collidepoint(self.casa):
                self.estado = 'scatter'
            return
        if self.estado_actual < len(Estado):
            if pg.time.get_ticks() - self.tiempo_estado >= Estado[self.estado_actual]:
                self.estado_actual += 1
                self.tiempo_estado = pg.time.get_ticks()
                if self.estado_actual % 2 == 0:
                    self.estado = 'scatter'
                else:
                    self.estado = 'chase'
        else:
            self.estado = 'chase'

    def mover(self, dt):
        x, y = direcciones_default[self.direccion]
        self.xr += x * self.velocidad * TILE_SIZE * dt
        self.yr += y * self.velocidad * TILE_SIZE * dt
        self.rect.x = int(self.xr)
        self.rect.y = int(self.yr)

    def Dibujar(self, pantalla):
        if pg.time.get_ticks() - self.tiempo_frame >= self.duracion_frame:
            if self.estado == 'asustado':
                self.frame_actual = (1 + self.frame_actual) % len(self.sprites_compartidos['asustado'])
            elif self.estado != 'muerto':
                self.frame_actual = 1 - self.frame_actual
            self.tiempo_frame = pg.time.get_ticks()
        if self.estado == 'asustado':
            sprite = self.sprites_compartidos['asustado'][self.frame_actual]
        elif self.estado == 'muerto':
            sprite = self.sprites_compartidos[f'ojos_{self.direccion}']
        else:
            sprite = self.sprites[self.direccion][self.frame_actual]
        pantalla.blit(sprite, self.rect)

class Blinky(Fantasma, pg.sprite.Sprite):
    def __init__(self, x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes):
        super().__init__(x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes)

        self.sprites = {
        'derecha': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Right)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Right)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        'izquierda': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Left)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Left)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        'arriba': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Up)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Up)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        'abajo': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Down)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Down)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        }

    def definir_objetivo(self):
        return self.pos_Pc

    def ejecutar(self, pos_Pc, dt):
        self.pos_Pc = pos_Pc
        self.alternar_estado()
        self.estados()
        self.mover(dt)

class Pinky(Fantasma, pg.sprite.Sprite):
    def __init__(self, x, y, nombre, color, esquina_scatter, pos_Pc, dir_pc, x_casa, y_casa, grupo_Paredes):
        super().__init__(x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes)
        self.dir_pc = dir_pc

        self.sprites = {
        'derecha': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Right)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Right)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        'izquierda': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Left)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Left)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        'arriba': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Up)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Up)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        'abajo': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Down)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Down)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        }

    def definir_objetivo(self):
        x, y = direcciones_default[self.dir_pc]
        objetivo = (self.pos_Pc[0] + x * 4 * TILE_SIZE, self.pos_Pc[1] + y * 4 * TILE_SIZE)
        return objetivo

    def ejecutar(self, pos_Pc, dir_pc, dt):
        self.dir_pc = dir_pc
        self.pos_Pc = pos_Pc
        self.alternar_estado()
        self.estados()
        self.mover(dt)

class Clyde(Fantasma, pg.sprite.Sprite):
    def __init__(self, x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes):
        super().__init__(x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes)
        
        self.sprites = {
        'derecha': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Right)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Right)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        'izquierda': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Left)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Left)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        'arriba': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Up)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Up)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        'abajo': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Down)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Down)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        }

    def definir_objetivo(self):
        posicion_actual = (self.rect.x, self.rect.y)
        distancia = (self.pos_Pc[0] - posicion_actual[0])**2 + (self.pos_Pc[1] - posicion_actual[1])**2
        if distancia  > (8 * TILE_SIZE)**2:
            return self.pos_Pc
        else:
            return self.esquina_scatter
    
    def ejecutar(self, pos_Pc, dt):
        self.pos_Pc = pos_Pc
        self.alternar_estado()
        self.estados()
        self.mover(dt)

class Inky(Fantasma, pg.sprite.Sprite):
    def __init__(self, x, y, nombre, color, esquina_scatter, pos_Pc, dir_pc, blinky, x_casa, y_casa, grupo_Paredes):
        super().__init__(x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes)
        self.dir_pc = dir_pc
        self.blinky = blinky

        self.sprites = {
        'derecha': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Right)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Right)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        'izquierda': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Left)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Left)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        'arriba': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Up)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Up)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        'abajo': [
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Down)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pg.transform.smoothscale(pg.image.load('Tp3_Ravignani_Gercar_Bazterrica_Guarneri/fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Down)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
        ],
        }

    def definir_objetivo(self):
        x, y = direcciones_default[self.dir_pc]
        objetivo_parcial = (self.pos_Pc[0] + x * 2 * TILE_SIZE, self.pos_Pc[1] + y * 2 * TILE_SIZE)
        objetivo = (2 * objetivo_parcial[0] - self.blinky.rect.x, 2 * objetivo_parcial[1] - self.blinky.rect.y)
        return objetivo
    
    def ejecutar(self, pos_Pc, dir_pc, dt):
        self.pos_Pc = pos_Pc
        self.dir_pc = dir_pc
        self.alternar_estado()
        self.estados()
        self.mover(dt)