import pygame
import math
import random

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla responsive
pantalla_info = pygame.display.Info()
ANCHO, ALTO = pantalla_info.current_w, pantalla_info.current_h
FPS = 60
COLOR_FONDO = (0, 0, 0)

# Colores
COLOR_NAVE = (0, 255, 0)
COLOR_BALA = (255, 0, 0)
COLOR_EXPLOSION = (255, 255, 0)
COLOR_ESTRELLAS = (255, 255, 255)
COLOR_SOMBRA_ASTEROIDE = (200, 200, 200)
COLOR_BARRA_VIDA = (255, 0, 0)
COLOR_BARRA_ENERGIA = (0, 255, 0)

# Tamaños
TAMANO_NAVE = 30
TAMANO_ASTEROIDE = [15, 30, 45, 60, 110, 250]  # Diferentes tamaños de asteroides

# Configuración de la pantalla
pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
pygame.display.set_caption("Juego de Naves Espaciales")

# Fuente para el texto
fuente = pygame.font.SysFont(None, 36)

# Reloj para controlar FPS
reloj = pygame.time.Clock()

# Clases
class Nave:
    def __init__(self):
        self.x = ANCHO // 2
        self.y = ALTO // 2
        self.angulo = 0
        self.velocidad = 5
        self.arma = 0  # 0: pistola, 1: ametralladora
        self.tipo_disparo = 0  # 0: único, 1: ráfaga
        self.vida = 100
        self.energia = 20
        self.tiempo_golpe = 0

    def mover(self, teclas):
        if teclas[pygame.K_w]:
            self.y -= self.velocidad
        if teclas[pygame.K_s]:
            self.y += self.velocidad
        if teclas[pygame.K_a]:
            self.x -= self.velocidad
        if teclas[pygame.K_d]:
            self.x += self.velocidad

        # Restricción de los bordes de la pantalla
        self.x = max(0, min(ANCHO, self.x))
        self.y = max(0, min(ALTO, self.y))

    def actualizar_angulo(self):
        raton_x, raton_y = pygame.mouse.get_pos()
        self.angulo = math.degrees(math.atan2(self.y - raton_y, raton_x - self.x)) % 360

    def disparar(self):
        if self.energia > 0:
            if self.tipo_disparo == 0:
                self.energia -= 1
                return [Bala(self.x, self.y, self.angulo, self.arma)]
            else:
                balas = [Bala(self.x, self.y, self.angulo + i * 10, self.arma) for i in range(-2, 3)]
                self.energia -= len(balas)
                return balas
        return []

    def dibujar(self):
        # Definir la forma de la nave con más detalle
        puntos = [
            (self.x + TAMANO_NAVE * math.cos(math.radians(self.angulo)),
             self.y - TAMANO_NAVE * math.sin(math.radians(self.angulo))),
            (self.x + (TAMANO_NAVE // 2) * math.cos(math.radians(self.angulo + 150)),
             self.y - (TAMANO_NAVE // 2) * math.sin(math.radians(self.angulo + 150))),
            (self.x + (TAMANO_NAVE // 2) * math.cos(math.radians(self.angulo - 150)),
             self.y - (TAMANO_NAVE // 2) * math.sin(math.radians(self.angulo - 150)))
        ]
        pygame.draw.polygon(pantalla, COLOR_NAVE, puntos)
        
        # Dibuja la "cabeza" de la nave como una línea
        pygame.draw.line(pantalla, (255, 255, 255), (self.x, self.y), puntos[0], 2)

        # Dibujar efecto de golpe
        if self.tiempo_golpe > 0:
            pygame.draw.circle(pantalla, (255, 0, 0), (int(self.x), int(self.y)), TAMANO_NAVE + 5, 2)
            self.tiempo_golpe -= 1

        # Dibujar barras de vida y energía
        self.dibujar_barras()

    def dibujar_barras(self):
        # Barra de vida
        longitud_barra = 50
        ancho_barra = 5
        vida_ratio = self.vida / 100
        energia_ratio = self.energia / 20

        # Barra de vida
        pygame.draw.rect(pantalla, (0, 0, 0), (self.x - longitud_barra // 2, self.y - TAMANO_NAVE - 10, longitud_barra, ancho_barra))
        pygame.draw.rect(pantalla, COLOR_BARRA_VIDA, (self.x - longitud_barra // 2, self.y - TAMANO_NAVE - 10, longitud_barra * vida_ratio, ancho_barra))

        # Barra de energía
        pygame.draw.rect(pantalla, (0, 0, 0), (self.x - longitud_barra // 2, self.y + TAMANO_NAVE + 5, longitud_barra, ancho_barra))
        pygame.draw.rect(pantalla, COLOR_BARRA_ENERGIA, (self.x - longitud_barra // 2, self.y + TAMANO_NAVE + 5, longitud_barra * energia_ratio, ancho_barra))

class Bala:
    def __init__(self, x, y, angulo, tipo_arma):
        self.x = x
        self.y = y
        self.angulo = angulo
        self.velocidad = 10
        self.tipo_arma = tipo_arma

    def mover(self):
        self.x += self.velocidad * math.cos(math.radians(self.angulo))
        self.y -= self.velocidad * math.sin(math.radians(self.angulo))

    def dibujar(self):
        pygame.draw.circle(pantalla, COLOR_BALA, (int(self.x), int(self.y)), 5)

    def fuera_de_pantalla(self):
        return not (0 <= self.x <= ANCHO and 0 <= self.y <= ALTO)

class Asteroide:
    def __init__(self):
        self.tamano = random.choice(TAMANO_ASTEROIDE)
        self.x, self.y = self.generar_fuera_de_pantalla()
        self.velocidad_x = random.uniform(-5 / (self.tamano / 15), 5 / (self.tamano / 15))
        self.velocidad_y = random.uniform(-5 / (self.tamano / 15), 5 / (self.tamano / 15))
        self.vida = self.tamano // 15
        self.explosión = False

        # Color de asteroide en tonos marrones
        self.color = (
            random.randint(100, 150),  # Rojo
            random.randint(75, 125),   # Verde
            random.randint(50, 100)    # Azul
        )

    def generar_fuera_de_pantalla(self):
        lado = random.choice(['izquierda', 'derecha', 'arriba', 'abajo'])
        if lado == 'izquierda':
            return -self.tamano, random.randint(0, ALTO)
        elif lado == 'derecha':
            return ANCHO + self.tamano, random.randint(0, ALTO)
        elif lado == 'arriba':
            return random.randint(0, ANCHO), -self.tamano
        else:
            return random.randint(0, ANCHO), ALTO + self.tamano

    def mover(self):
        self.x += self.velocidad_x
        self.y += self.velocidad_y
        if self.x < -self.tamano or self.x > ANCHO + self.tamano or self.y < -self.tamano or self.y > ALTO + self.tamano:
            self.x, self.y = self.generar_fuera_de_pantalla()

    def dibujar(self):
        if not self.explosión:
            pygame.draw.circle(pantalla, COLOR_SOMBRA_ASTEROIDE, (int(self.x) + 2, int(self.y) + 2), self.tamano)
            pygame.draw.circle(pantalla, self.color, (int(self.x), int(self.y)), self.tamano)
            fuente = pygame.font.SysFont(None, 24)
            texto_vida = fuente.render(str(self.vida), True, (255, 255, 255))
            pantalla.blit(texto_vida, (self.x - fuente.size(str(self.vida))[0] // 2, self.y - fuente.size(str(self.vida))[1] // 2))

    def explotar(self):
        self.explosión = True
        pygame.time.set_timer(pygame.USEREVENT + 1, 200)

def crear_fondo_espacial():
    fondo = pygame.Surface((ANCHO, ALTO))
    fondo.fill(COLOR_FONDO)
    for _ in range(200):
        x = random.randint(0, ANCHO)
        y = random.randint(0, ALTO)
        color = random.choice([COLOR_ESTRELLAS, (100, 100, 255)])
        fondo.set_at((x, y), color)
    return fondo

def mostrar_pantalla_inicio():
    global reloj
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                raton_x, raton_y = pygame.mouse.get_pos()
                if boton_jugar.collidepoint((raton_x, raton_y)):
                    return

        pantalla.blit(fondo_espacial, (0, 0))
        pygame.draw.rect(pantalla, (0, 255, 0), boton_jugar)
        texto_jugar = fuente.render("JUGAR", True, (0, 0, 0))
        pantalla.blit(texto_jugar, (boton_jugar.x + 10, boton_jugar.y + 10))

        pygame.display.flip()
        reloj.tick(FPS)

def mostrar_resumen(puntos, asteroides_destruidos, balas_disparadas):
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                raton_x, raton_y = pygame.mouse.get_pos()
                if boton_reiniciar.collidepoint((raton_x, raton_y)):
                    return

        pantalla.blit(fondo_espacial, (0, 0))
        resumen_texto = [
            f"Puntuación: {puntos}",
            f"Asteroides destruidos: {asteroides_destruidos}",
            f"Balas disparadas: {balas_disparadas}",
        ]
        y = 10
        for linea in resumen_texto:
            texto = fuente.render(linea, True, (255, 255, 255))
            pantalla.blit(texto, (10, y))
            y += 40

        pygame.draw.rect(pantalla, (0, 255, 0), boton_reiniciar)
        texto_reiniciar = fuente.render("JUGAR DE NUEVO", True, (0, 0, 0))
        pantalla.blit(texto_reiniciar, (boton_reiniciar.x + 10, boton_reiniciar.y + 10))

        pygame.display.flip()
        reloj.tick(FPS)

# Crear fondo espacial
fondo_espacial = crear_fondo_espacial()

# Configurar el botón de "JUGAR" y "JUGAR DE NUEVO"
boton_jugar = pygame.Rect(ANCHO // 2 - 100, ALTO // 2 - 30, 200, 60)
boton_reiniciar = pygame.Rect(ANCHO // 2 - 150, ALTO // 2 - 30, 300, 60)

# Bucle principal del juego
def juego():
    # Inicializar objetos
    nave = Nave()
    balas = []
    asteroides = [Asteroide() for _ in range(3)]
    puntuacion = 0
    asteroides_destruidos = 0
    balas_disparadas = 0

    reloj = pygame.time.Clock()
    ejecutando = True
    disparo_temporal = 0

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_f:
                    nave.arma = (nave.arma + 1) % 2
                elif evento.key == pygame.K_r:
                    nave.tipo_disparo = (nave.tipo_disparo + 1) % 2
            elif evento.type == pygame.USEREVENT + 1:
                for asteroide in asteroides:
                    if asteroide.explosión:
                        asteroides.remove(asteroide)
                        asteroides_destruidos += 1

        teclas = pygame.key.get_pressed()
        nave.mover(teclas)
        nave.actualizar_angulo()

        if pygame.mouse.get_pressed()[0] and disparo_temporal <= 0 and nave.energia > 0:
            balas.extend(nave.disparar())
            balas_disparadas += len(nave.disparar())
            disparo_temporal = 10

        # Mover balas
        for bala in list(balas):
            bala.mover()
            if bala.fuera_de_pantalla():
                balas.remove(bala)

        # Mover asteroides
        for asteroide in asteroides:
            asteroide.mover()

        # Colisiones balas y asteroides
        for bala in list(balas):
            for asteroide in asteroides:
                distancia = math.hypot(bala.x - asteroide.x, bala.y - asteroide.y)
                if distancia < asteroide.tamano:
                    asteroide.vida -= 1
                    if bala in balas:
                        balas.remove(bala)
                    if asteroide.vida <= 0:
                        puntuacion += asteroide.tamano // 15
                        asteroide.explotar()

        # Colisiones nave y asteroides
        for asteroide in asteroides:
            distancia = math.hypot(nave.x - asteroide.x, nave.y - asteroide.y)
            if distancia < asteroide.tamano:
                # El asteroide rebota
                asteroide.velocidad_x *= -1
                asteroide.velocidad_y *= -1
                # Daño a la nave
                dano = random.randint(1, 10)
                nave.vida -= dano
                nave.tiempo_golpe = 10
                if nave.vida <= 0:
                    nave.vida = 0
                    pantalla.fill(COLOR_FONDO)
                    mostrar_resumen(puntuacion, asteroides_destruidos, balas_disparadas)
                    pygame.time.wait(2000)
                    return

        # Incrementar el máximo de asteroides progresivamente
        max_asteroides = min(8 + puntuacion // 100, 20)
        if len(asteroides) < max_asteroides:
            nuevo_asteroide = Asteroide()
            asteroides.append(nuevo_asteroide)

        # Dibujar
        pantalla.blit(fondo_espacial, (0, 0))
        nave.dibujar()
        for bala in balas:
            bala.dibujar()
        for asteroide in asteroides:
            asteroide.dibujar()

        # Dibujar puntuación
        texto_puntuacion = fuente.render(f'Puntuación: {puntuacion}', True, (255, 255, 255))
        pantalla.blit(texto_puntuacion, (10, 10))

        pygame.display.flip()

        # Controlar FPS y recargar energía
        disparo_temporal -= 1
        if not pygame.mouse.get_pressed()[0] and nave.energia < 20:
            nave.energia += 0.1
        reloj.tick(FPS)

# Pantalla de inicio
mostrar_pantalla_inicio()

# Iniciar juego
juego()

# Cerrar Pygame
pygame.quit()
