from entidades import Criatura, TILE_SIZE
from Mapa import MAPA_ANCHO, MAPA_ALTO
import pygame as pg
import random

Estado = [7000, 20000, 7000, 20000, 5000, 20000, 5000]
direcciones_default = {
    'derecha': (1, 0),
    'izquierda': (-1, 0),
    'arriba': (0, -1),
    'abajo': (0, 1)
}
opuesto = {'derecha': 'izquierda', 'izquierda': 'derecha', 'arriba': 'abajo', 'abajo': 'arriba'}

class Fantasma(Criatura):
    velocidad_normal = (7.5 * 0.75)
    velocidad_asustado = (7.5 * 0.50)
    velocidad_ojos = (7.5 * 1.5)

    def __init__(self, x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes):
        super().__init__(x, y, Fantasma.velocidad_normal)
        self.nombre = nombre
        self.color = color
        self.esquina_scatter = esquina_scatter
        self.pos_Pc = pos_Pc
        self.estado = "scatter"
        self.direccion = 'derecha'
        self.en_casa = True
        self.grupo_Puertas = pg.sprite.Group()
        self.rect = pg.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.estado_actual = 0
        self.tiempo_estado = pg.time.get_ticks()
        self.puerta_x = MAPA_ANCHO // 2
        self.puerta_y = 12 * TILE_SIZE
        self.puerta = (self.puerta_x, self.puerta_y)
        self.xr = float(x)
        self.yr = float(y)
        self.x_casa = x_casa
        self.y_casa = y_casa
        self.casa = (x_casa, y_casa)
        self.grupo_Paredes = grupo_Paredes
        self.frame_actual = 0
        self.tiempo_frame = pg.time.get_ticks()
        self.duracion_frame = 200
        self.tiempo_asustado = 0
        self.ultimo_tile = (-1, -1)
        self.recien_salio = False
        self.dir_bounce = -1
        self.mejor_dist_objetivo = float('inf')
        self.tiempo_sin_progreso = pg.time.get_ticks()
        self.forzar_random_hasta = 0
        self.bounce_limite_sup = y_casa - TILE_SIZE
        self.bounce_limite_inf = y_casa + TILE_SIZE
        self.sonido_muerte = pg.mixer.Sound("sonidos_pacman/eat_ghost.wav")

        self.sprites_compartidos = {
            'asustado': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Asustado/Arcade - Pac-Man - General Sprites - Blue Ghost (1)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Asustado/Arcade - Pac-Man - General Sprites - Blue Ghost (1)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Asustado/Arcade - Pac-Man - General Sprites - White Ghost_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Asustado/Arcade - Pac-Man - General Sprites - White Ghost_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE))
            ],
            'ojos_derecha':   pg.transform.smoothscale(pg.image.load('fantasmas/Ojos/Ojos_derecha.png').convert_alpha(),   (TILE_SIZE, TILE_SIZE)),
            'ojos_izquierda': pg.transform.smoothscale(pg.image.load('fantasmas/Ojos/Ojos_izquierda.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            'ojos_arriba':    pg.transform.smoothscale(pg.image.load('fantasmas/Ojos/Ojos_arriba.png').convert_alpha(),    (TILE_SIZE, TILE_SIZE)),
            'ojos_abajo':     pg.transform.smoothscale(pg.image.load('fantasmas/Ojos/Ojos_abajo.png').convert_alpha(),     (TILE_SIZE, TILE_SIZE)),
        }

    def definir_objetivo(self):
        return self.esquina_scatter

    def alineado(self):
        cx = self.rect.x % TILE_SIZE
        cy = self.rect.y % TILE_SIZE
        return cx == 0 and cy == 0

    def analizar_colisiones(self, tile_x, tile_y): # Esta funcion lo que hace es mirar las 4 casillas vecinas al fantasma y devolver cuales estan disponibles para moverse.
        direcciones_libres = {}
        en_casa_o_saliendo = self.estado in ['saliendo', 'muerto'] or self.en_casa # Determinar si el fantasma esta adentro de la casa

        for direccion, (dx, dy) in direcciones_default.items(): # Recorrer las cuatro direcciones
            objx = tile_x + dx
            objy = tile_y + dy
            if direccion == 'arriba' and self.estado not in ['muerto', 'asustado'] and not self.recien_salio: # Restriccion especial de la ghost house
                if (objy == 10 or objy == 22) and (11 <= objx <= 16): # Zona prohibida
                    direcciones_libres[direccion] = False # Si intentan subir aca quedan "bloqueados"
                    continue

            rect_prueba = pg.Rect(objx * TILE_SIZE, objy * TILE_SIZE, TILE_SIZE, TILE_SIZE) # Rect de prueba

            col_pared = bool(rect_prueba.collideobjects(self.grupo_Paredes.sprites())) # Ver si chocaria con una pared
            col_puerta = False
            if not en_casa_o_saliendo and hasattr(self, 'grupo_Puertas'):
                col_puerta = bool(rect_prueba.collideobjects(self.grupo_Puertas.sprites()))

            direcciones_libres[direccion] = not col_pared and not col_puerta
        return direcciones_libres

    def direcciones(self, objetivo):
        tile_x = self.rect.x // TILE_SIZE # Obtener el tile actual
        tile_y = self.rect.y // TILE_SIZE

        direcciones_libres = self.analizar_colisiones(tile_x, tile_y) # Ver qué caminos están disponibles
        posibles_posiciones = {} # Calcular distancia al objetivo desde cada posible movimiento

        for direccion, disponible in direcciones_libres.items(): # Recorrer las direcciones
            if not disponible or direccion == opuesto[self.direccion]:
                continue
            dx, dy = direcciones_default[direccion] # Simular el siguiente tile
            proximo_tile_x = tile_x + dx
            proximo_tile_y = tile_y + dy
            dist_x = (objetivo[0] // TILE_SIZE) - proximo_tile_x
            dist_y = (objetivo[1] // TILE_SIZE) - proximo_tile_y
            posibles_posiciones[direccion] = dist_x ** 2 + dist_y ** 2 # Medir distancia al objetivo, distancia euclidiana

        if not posibles_posiciones: # Si no hay opciones, vuelve
            return opuesto[self.direccion]

        dist_actual = (((objetivo[0] // TILE_SIZE) - tile_x) ** 2 +
                       ((objetivo[1] // TILE_SIZE) - tile_y) ** 2) # Distancia actual al objetivo

        if dist_actual < self.mejor_dist_objetivo: # Ver si esta progresando
            self.mejor_dist_objetivo = dist_actual
            self.tiempo_sin_progreso = pg.time.get_ticks()

        ahora = pg.time.get_ticks()
        en_modo_random = ahora < self.forzar_random_hasta

        if not en_modo_random and ahora - self.tiempo_sin_progreso > 3000: # Si durante 3 segundos no consiguio acercarse al objetivo:
            self.tiempo_sin_progreso = ahora
            self.mejor_dist_objetivo = float('inf')
            self.forzar_random_hasta = ahora + 2000
            en_modo_random = True

        if en_modo_random: # Scatter
            dirs_libres = [d for d, libre in direcciones_libres.items() if libre and d != opuesto[self.direccion]]
            if dirs_libres:
                return random.choice(dirs_libres)

        prioridad = ['arriba', 'izquierda', 'abajo', 'derecha']
        min_dist = min(posibles_posiciones.values()) # Elegir la mejor direccion
        mejores = [d for d, dist in posibles_posiciones.items() if dist == min_dist]
        for p in prioridad:
            if p in mejores:
                return p
        return mejores[0]

    def estados(self):
        pos_actual = (self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE)

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
            self.velocidad = self.velocidad_asustado
            if self.alineado() and pos_actual != self.ultimo_tile:
                self.ultimo_tile = pos_actual
                self.asustado()
            return
        elif self.estado == 'saliendo':
            return

        if self.en_casa:
            return
        if self.alineado() and pos_actual != self.ultimo_tile:
            self.ultimo_tile = pos_actual
            self.direccion = self.direcciones(objetivo)
            self.recien_salio = False
            

    def activar_asustado(self):
        if self.en_casa:
            return
        if self.estado in ['scatter', 'chase', 'asustado']:
            self.estado = 'asustado'
            self.velocidad = self.velocidad_asustado
            self.direccion = opuesto[self.direccion] # Invierte la direccion
            self.frame_actual = 0
            self.tiempo_asustado = pg.time.get_ticks()
            self.ultimo_tile = (-1, -1) # Resetear ultimo tile

    def asustado(self):
        pos_x = self.rect.x // TILE_SIZE
        pos_y = self.rect.y // TILE_SIZE
        posibles_direcciones = self.analizar_colisiones(pos_x, pos_y)

        direcciones_validas = [
            d for d, libre in posibles_direcciones.items()
            if libre and d != opuesto[self.direccion]
        ]
        if not direcciones_validas:
            direcciones_validas = [d for d, libre in posibles_direcciones.items() if libre]
        if direcciones_validas:
            self.direccion = random.choice(direcciones_validas)

    def muerto(self):
        if self.estado != 'muerto':
            self.estado = 'muerto'
            self.velocidad = self.velocidad_ojos
            self.ultimo_tile = (-1, -1)

    def alternar_estado(self):
        if self.estado == 'saliendo' or self.en_casa:
            return
        if self.estado == 'asustado':
            if pg.time.get_ticks() - self.tiempo_asustado >= 6000:
                self.frame_actual = 0
                self.ultimo_tile = (-1, -1)
                self.mejor_dist_objetivo = float('inf')
                self.tiempo_sin_progreso = pg.time.get_ticks()
                self.forzar_random_hasta = 0
                self.estado = 'scatter' if self.estado_actual % 2 == 0 else 'chase'
            return
        if self.estado == 'muerto':
            pos_actual_x = self.rect.x // TILE_SIZE
            pos_actual_y = self.rect.y // TILE_SIZE
            casa_tile_x = self.casa[0] // TILE_SIZE
            casa_tile_y = self.casa[1] // TILE_SIZE
            if pos_actual_x == casa_tile_x and abs(pos_actual_y - casa_tile_y) <= 1:
                self.xr = float(self.casa[0])
                self.yr = float(self.casa[1])
                self.rect.x = self.casa[0]
                self.rect.y = self.casa[1]
                self.estado = 'saliendo'
                self.ultimo_tile = (-1, -1)
                self.mejor_dist_objetivo = float('inf')
                self.tiempo_sin_progreso = pg.time.get_ticks()
                self.forzar_random_hasta = 0
                self.tiempo_estado = pg.time.get_ticks()
            return

        if self.estado_actual < len(Estado):
            if pg.time.get_ticks() - self.tiempo_estado >= Estado[self.estado_actual]:
                self.estado_actual += 1
                self.tiempo_estado = pg.time.get_ticks()
                self.ultimo_tile = (-1, -1)
                self.mejor_dist_objetivo = float('inf')
                self.tiempo_sin_progreso = pg.time.get_ticks()
                self.forzar_random_hasta = 0
                self.estado = 'scatter' if self.estado_actual % 2 == 0 else 'chase'
        else:
            self.estado = 'chase'

    def mover_en_casa(self, dt):
        velocidad = self.velocidad_normal * TILE_SIZE * dt
        self.yr += self.dir_bounce * velocidad
        self.rect.y = int(self.yr)

        if self.yr <= self.bounce_limite_sup:
            self.yr = float(self.bounce_limite_sup)
            self.rect.y = self.bounce_limite_sup
            self.dir_bounce = 1
            self.direccion = 'abajo'
        elif self.yr >= self.bounce_limite_inf:
            self.yr = float(self.bounce_limite_inf)
            self.rect.y = self.bounce_limite_inf
            self.dir_bounce = -1
            self.direccion = 'arriba'

    def mover(self, dt):
        if self.estado == 'saliendo':
            velocidad = self.velocidad_normal * TILE_SIZE * dt
            if abs(self.rect.x - self.puerta_x) > 2:
                if self.rect.x < self.puerta_x:
                    self.xr += velocidad
                else:
                    self.xr -= velocidad
                self.rect.x = int(self.xr)
            else:
                self.xr = float(self.puerta_x)
                self.rect.x = self.puerta_x
                self.yr -= velocidad
                self.rect.y = int(self.yr)
                destino_y = self.puerta_y - TILE_SIZE
                if self.rect.y <= destino_y:
                    self.rect.y = destino_y
                    self.yr = float(destino_y)
                    self.estado = 'scatter'
                    self.ultimo_tile = (-1, -1)
                    self.mejor_dist_objetivo = float('inf')
                    self.tiempo_sin_progreso = pg.time.get_ticks()
                    self.forzar_random_hasta = 0
                    self.recien_salio = True
                    self.tiempo_estado = pg.time.get_ticks()
            return

    

        dx, dy = direcciones_default[self.direccion]
        self.xr += dx * self.velocidad * TILE_SIZE * dt
        self.yr += dy * self.velocidad * TILE_SIZE * dt
        ancho_mapa = MAPA_ANCHO
        if self.xr < -TILE_SIZE:
            self.xr += ancho_mapa + TILE_SIZE
        elif self.xr > ancho_mapa:
            self.xr -= ancho_mapa + TILE_SIZE

        self.rect.x = int(self.xr)
        self.rect.y = int(self.yr)
        if self.estado not in ['saliendo']:
            col_pared = bool(self.rect.collideobjects(self.grupo_Paredes.sprites()))
            if col_pared:
                if dx > 0:
                    self.xr = float((self.rect.x // TILE_SIZE) * TILE_SIZE)
                elif dx < 0:
                    self.xr = float(((self.rect.x // TILE_SIZE) + 1) * TILE_SIZE)
                elif dy > 0:
                    self.yr = float((self.rect.y // TILE_SIZE) * TILE_SIZE)
                elif dy < 0:
                    self.yr = float(((self.rect.y // TILE_SIZE) + 1) * TILE_SIZE)
                self.rect.x = int(self.xr)
                self.rect.y = int(self.yr)

    def reiniciar(self, x, y):
        self.xr = float(x)
        self.yr = float(y)
        self.rect.topleft = (x, y)
        self.direccion = 'derecha'
        self.estado = 'scatter'
        self.en_casa = True
        self.estado_actual = 0
        self.ultimo_tile = (-1, -1)
        self.mejor_dist_objetivo = float('inf') # crea un numero especial que es mas grande que cualquier otro numero.
        self.tiempo_sin_progreso = pg.time.get_ticks()
        self.forzar_random_hasta = 0
        self.recien_salio = False
        self.tiempo_estado = pg.time.get_ticks()
        self.dir_bounce = -1

    def Dibujar(self, pantalla):
        if pg.time.get_ticks() - self.tiempo_frame >= self.duracion_frame:
            if self.estado == 'asustado':
                self.frame_actual = (self.frame_actual + 1) % 4
            elif self.estado != 'muerto':
                self.frame_actual = (self.frame_actual + 1) % 2
            self.tiempo_frame = pg.time.get_ticks()

        if self.estado == 'asustado':
            tiempo_restante = 6000 - (pg.time.get_ticks() - self.tiempo_asustado)
            if tiempo_restante <= 2000:
                sprite = self.sprites_compartidos['asustado'][self.frame_actual]
            else:
                sprite = self.sprites_compartidos['asustado'][self.frame_actual % 2]
        elif self.estado == 'muerto':
            sprite = self.sprites_compartidos[f'ojos_{self.direccion}']
        else:
            sprite = self.sprites[self.direccion][self.frame_actual % 2]

        pantalla.blit(sprite, self.rect)


class Blinky(Fantasma, pg.sprite.Sprite):
    def __init__(self, x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes):
        super().__init__(x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes)
        self.sprites = self._cargar_sprites()

    def _cargar_sprites(self):
        return {
            'derecha': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Right)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Right)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'izquierda': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Left) (1)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Left) (1)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'arriba': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Up)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Up)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'abajo': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Down)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Blinky/Arcade - Pac-Man - General Sprites - Blinky (Down)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
        }

    def definir_objetivo(self):
        return self.pos_Pc

    def ejecutar(self, pos_Pc, dt):
        if self.en_casa:
            self.mover_en_casa(dt)
            return
        self.pos_Pc = pos_Pc
        self.alternar_estado()
        self.estados()
        self.mover(dt)


class Pinky(Fantasma, pg.sprite.Sprite):
    def __init__(self, x, y, nombre, color, esquina_scatter, pos_Pc, dir_pc, x_casa, y_casa, grupo_Paredes):
        super().__init__(x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes)
        self.dir_pc = dir_pc
        self.sprites = self._cargar_sprites()

    def _cargar_sprites(self):
        return {
            'derecha': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Right)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Right)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'izquierda': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Left)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Left)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'arriba': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Up)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Up)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'abajo': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Down)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Pinky/Arcade - Pac-Man - General Sprites - Pinky (Down)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
        }

    def definir_objetivo(self):
        dx, dy = direcciones_default.get(self.dir_pc, (0, 0))
        if self.dir_pc == 'arriba':
            return (self.pos_Pc[0] - 4 * TILE_SIZE, self.pos_Pc[1] - 4 * TILE_SIZE)
        return (self.pos_Pc[0] + dx * 4 * TILE_SIZE, self.pos_Pc[1] + dy * 4 * TILE_SIZE)

    def ejecutar(self, pos_Pc, dir_pc, dt):
        if self.en_casa:
            self.mover_en_casa(dt)
            return
        self.dir_pc = dir_pc
        self.pos_Pc = pos_Pc
        self.alternar_estado()
        self.estados()
        self.mover(dt)


class Clyde(Fantasma, pg.sprite.Sprite):
    def __init__(self, x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes):
        super().__init__(x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes)
        self.sprites = self._cargar_sprites()

    def _cargar_sprites(self):
        return {
            'derecha': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Right)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Right)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'izquierda': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Left)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Left)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'arriba': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Up)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Up)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'abajo': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Down) (1)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Clyde/Arcade - Pac-Man - General Sprites - Clyde (Down) (1)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
        }

    def definir_objetivo(self):
        dist_x = (self.pos_Pc[0] - self.rect.x) // TILE_SIZE
        dist_y = (self.pos_Pc[1] - self.rect.y) // TILE_SIZE
        if (dist_x ** 2 + dist_y ** 2) > 64:
            return self.pos_Pc
        return self.esquina_scatter

    def ejecutar(self, pos_Pc, dt):
        if self.en_casa:
            self.mover_en_casa(dt)
            return
        self.pos_Pc = pos_Pc
        self.alternar_estado()
        self.estados()
        self.mover(dt)


class Inky(Fantasma, pg.sprite.Sprite):
    def __init__(self, x, y, nombre, color, esquina_scatter, pos_Pc, dir_pc, blinky, x_casa, y_casa, grupo_Paredes):
        super().__init__(x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes)
        self.dir_pc = dir_pc
        self.blinky = blinky
        self.sprites = self._cargar_sprites()

    def _cargar_sprites(self):
        return {
            'derecha': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Right)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Right)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'izquierda': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Left)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Left)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'arriba': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Up)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Up)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'abajo': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Down)_frame_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Inky/Arcade - Pac-Man - General Sprites - Inky (Down)_frame_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
        }

    def definir_objetivo(self):
        dx, dy = direcciones_default.get(self.dir_pc, (0, 0))
        if self.dir_pc == 'arriba':
            p_x = self.pos_Pc[0] - 2 * TILE_SIZE
            p_y = self.pos_Pc[1] - 2 * TILE_SIZE
        else:
            p_x = self.pos_Pc[0] + dx * 2 * TILE_SIZE
            p_y = self.pos_Pc[1] + dy * 2 * TILE_SIZE

        if self.blinky is not None:
            b_x, b_y = self.blinky.rect.x, self.blinky.rect.y
        else:
            b_x, b_y = self.esquina_scatter

        return (b_x + 2 * (p_x - b_x), b_y + 2 * (p_y - b_y))

    def ejecutar(self, pos_Pc, dir_pc, dt):
        if self.en_casa:
            self.mover_en_casa(dt)
            return
        self.pos_Pc = pos_Pc
        self.dir_pc = dir_pc
        self.alternar_estado()
        self.estados()
        self.mover(dt)


class Tracer (Fantasma,pg.sprite.Sprite):
    def __init__(self, x, y, nombre, color, esquina_scatter, pos_Pc, dir_pc, x_casa, y_casa, grupo_Paredes):
        super().__init__(x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes)
        self.Turno = int(self.tiempo_estado - 1000)
        self.dir_pc = dir_pc
        self.historial = []
        self.objetivo = pos_Pc
        self.retraso = 60 # Pacman desde hace 60 frames
        self.sprites = self._cargar_sprites()

    def _cargar_sprites(self):
        return {
            'derecha': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Tracer/Tracer Right 1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Tracer/Tracer Right 2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'izquierda': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Tracer/Tracer Left 1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Tracer/Tracer Left 2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'arriba': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Tracer/Tracer Up 1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Tracer/Tracer Up 2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'abajo': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Tracer/Tracer Down 1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Tracer/Tracer Down 2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
        }

    def definir_objetivo(self):
        dist_x = abs(self.objetivo[0] - self.rect.x)
        dist_y = abs(self.objetivo[1] - self.rect.y)
        if (dist_x + dist_y) < (TILE_SIZE * 3):
            return self.pos_Pc
        return self.objetivo
    
    def ejecutar(self, pos_Pc, dir_pc, dt):
        self.pos_Pc = pos_Pc
        self.dir_pc = dir_pc
        self.historial.append(self.pos_Pc)
        if len(self.historial) > self.retraso:
            self.objetivo = self.historial.pop(0)
        if self.estado == 'chase':
            self.tiempo_sin_progreso = pg.time.get_ticks()
        if self.en_casa:
            self.mover_en_casa(dt)
            return
        self.alternar_estado()
        self.estados()
        self.mover(dt)
        
    def reiniciar(self, x, y):
        super().reiniciar(x, y)
        self.historial.clear()
        self.objetivo = self.pos_Pc

class Patrullero(Fantasma, pg.sprite.Sprite):
    def __init__(self, x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes):
        super().__init__(x, y, nombre, color, esquina_scatter, pos_Pc, x_casa, y_casa, grupo_Paredes)
        self.ruta = [(14*TILE_SIZE, 5*TILE_SIZE),   # arriba centro
        (23*TILE_SIZE, 14*TILE_SIZE),  # derecha centro
        (14*TILE_SIZE, 26*TILE_SIZE),  # abajo centro
        (4*TILE_SIZE, 14*TILE_SIZE)    # izquierda centro
        ]
        self.punto_actual = 0 # Posicion de la lista de ruta
        self.sprites = self._cargar_sprites()

    def _cargar_sprites(self):
        return {
            'derecha': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Patrullero/Patrullero_derecha_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Patrullero/Patrullero_derecha_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'izquierda': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Patrullero/Patrullero_izquierda_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Patrullero/Patrullero_izquierda_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'arriba': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Patrullero/Patrullero_arriba_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Patrullero/Patrullero_arriba_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
            'abajo': [
                pg.transform.smoothscale(pg.image.load('fantasmas/Patrullero/Patrullero_abajo_1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
                pg.transform.smoothscale(pg.image.load('fantasmas/Patrullero/Patrullero_abajo_2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            ],
        }

    def definir_objetivo(self):
        objetivo = self.ruta[self.punto_actual] # Obtener el objetivo
        dist_x = (objetivo[0] - self.rect.x) // TILE_SIZE
        dist_y = (objetivo[1] - self.rect.y) // TILE_SIZE # Calcular la distancia
        
        if dist_x ** 2 + dist_y ** 2 <= 1: # Ver si llego al objetivo
            self.punto_actual = (self.punto_actual + 1) % len(self.ruta) # Pasar al siguiente punto
            objetivo = self.ruta[self.punto_actual] # Actualizar objetivo

        return objetivo

    def ejecutar(self, pos_Pc, dt):
        if self.en_casa:
            self.mover_en_casa(dt)
            return

        self.pos_Pc = pos_Pc
        self.alternar_estado()
        self.estados()
        self.mover(dt)
        




