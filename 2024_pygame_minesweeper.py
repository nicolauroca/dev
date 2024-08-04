import pygame
import random
import time

# Configuración de Pygame
pygame.init()

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (192, 192, 192)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)

# Parámetros de las celdas
ANCHO_CELDA = 30
ALTO_CELDA = 30

# Crear la ventana
ANCHO_VENTANA = 600
ALTO_VENTANA = 400
ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption('Buscaminas')

# Definir dificultades
DIFICULTADES = {
    'Facil': (10, 10, 10),
    'Medio': (16, 16, 40),
    'Dificil': (24, 24, 99)
}

# Variables globales del juego
cuadricula = []
celda_descubierta = []
celda_marcada = []
FILA = 0
COL = 0
NUM_MINAS = 0
jugando = False
inicio_tiempo = 0
fin_tiempo = 0
margen_x = 0
margen_y = 0
victoria = False

def crear_cuadricula(fila, col):
    return [[0 for _ in range(col)] for _ in range(fila)]

def colocar_minas(cuadricula, fila, col, num_minas):
    minas_colocadas = 0
    while minas_colocadas < num_minas:
        x = random.randint(0, fila - 1)
        y = random.randint(0, col - 1)
        if cuadricula[x][y] == 0:
            cuadricula[x][y] = -1
            minas_colocadas += 1
            for i in range(max(0, x - 1), min(fila, x + 2)):
                for j in range(max(0, y - 1), min(col, y + 2)):
                    if cuadricula[i][j] != -1:
                        cuadricula[i][j] += 1

def dibujar_cuadricula(cuadricula, fila, col):
    ventana.fill(NEGRO)
    for x in range(fila):
        for y in range(col):
            rect = pygame.Rect(margen_x + y * ANCHO_CELDA, margen_y + x * ALTO_CELDA, ANCHO_CELDA, ALTO_CELDA)
            if celda_descubierta[x][y]:
                pygame.draw.rect(ventana, BLANCO, rect)
                if cuadricula[x][y] == -1:
                    pygame.draw.circle(ventana, ROJO, rect.center, ANCHO_CELDA // 4)
                elif cuadricula[x][y] > 0:
                    font = pygame.font.Font(None, 24)
                    texto = font.render(str(cuadricula[x][y]), True, NEGRO)
                    ventana.blit(texto, texto.get_rect(center=rect.center))
            else:
                pygame.draw.rect(ventana, GRIS, rect)
                if celda_marcada[x][y]:
                    pygame.draw.line(ventana, AZUL, rect.topleft, rect.bottomright, 3)
                    pygame.draw.line(ventana, AZUL, rect.bottomleft, rect.topright, 3)
            pygame.draw.rect(ventana, NEGRO, rect, 1)
    pygame.display.flip()

def descubrir_celda(cuadricula, fila, col, x, y):
    if x < 0 or x >= fila or y < 0 or y >= col or celda_descubierta[x][y] or celda_marcada[x][y]:
        return
    celda_descubierta[x][y] = True
    if cuadricula[x][y] == 0:
        for i in range(max(0, x - 1), min(fila, x + 2)):
            for j in range(max(0, y - 1), min(col, y + 2)):
                descubrir_celda(cuadricula, fila, col, i, j)

def pantalla_inicio():
    ventana.fill(NEGRO)
    font = pygame.font.Font(None, 36)
    texto = font.render('Seleccione la Dificultad', True, BLANCO)
    ventana.blit(texto, (ANCHO_VENTANA // 2 - texto.get_width() // 2, ALTO_VENTANA // 4))

    botones = []
    for idx, dificultad in enumerate(DIFICULTADES.keys()):
        rect = pygame.Rect(ANCHO_VENTANA // 2 - 75, ALTO_VENTANA // 2 + idx * 50, 150, 40)
        pygame.draw.rect(ventana, GRIS, rect)
        texto = font.render(dificultad, True, NEGRO)
        ventana.blit(texto, (rect.x + (rect.width - texto.get_width()) // 2, rect.y + (rect.height - texto.get_height()) // 2))
        botones.append((rect, dificultad))

    pygame.display.flip()
    return botones

def pantalla_final(mensaje):
    ventana.fill(NEGRO)
    font = pygame.font.Font(None, 36)
    texto = font.render(mensaje, True, BLANCO)
    ventana.blit(texto, (ANCHO_VENTANA // 2 - texto.get_width() // 2, ALTO_VENTANA // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

def verificar_victoria(fila, col):
    for x in range(fila):
        for y in range(col):
            if cuadricula[x][y] != -1 and not celda_descubierta[x][y]:
                return False
    return True

def main():
    global cuadricula, celda_descubierta, celda_marcada, FILA, COL, NUM_MINAS, jugando, inicio_tiempo, fin_tiempo, margen_x, margen_y, ventana, ANCHO_VENTANA, ALTO_VENTANA, victoria

    ejecutando = True
    while ejecutando:
        seleccionando_dificultad = True
        while seleccionando_dificultad:
            botones = pantalla_inicio()
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    for rect, dificultad in botones:
                        if rect.collidepoint(evento.pos):
                            FILA, COL, NUM_MINAS = DIFICULTADES[dificultad]
                            ANCHO_VENTANA = COL * ANCHO_CELDA
                            ALTO_VENTANA = FILA * ALTO_CELDA
                            ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
                            pygame.display.set_caption('Buscaminas')
                            cuadricula = crear_cuadricula(FILA, COL)
                            colocar_minas(cuadricula, FILA, COL, NUM_MINAS)
                            celda_descubierta = [[False for _ in range(COL)] for _ in range(FILA)]
                            celda_marcada = [[False for _ in range(COL)] for _ in range(FILA)]
                            seleccionando_dificultad = False
                            jugando = True
                            inicio_tiempo = time.time()
                            margen_x = (ventana.get_width() - (COL * ANCHO_CELDA)) // 2
                            margen_y = (ventana.get_height() - (FILA * ALTO_CELDA)) // 2

        while jugando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    x, y = evento.pos
                    x = (x - margen_x) // ANCHO_CELDA
                    y = (y - margen_y) // ALTO_CELDA
                    if 0 <= x < COL and 0 <= y < FILA:
                        if evento.button == 1:  # Clic izquierdo
                            if cuadricula[y][x] == -1:
                                celda_descubierta[y][x] = True
                                dibujar_cuadricula(cuadricula, FILA, COL)
                                pantalla_final("¡Perdiste!")
                                jugando = False
                            else:
                                descubrir_celda(cuadricula, FILA, COL, y, x)
                        elif evento.button == 3:  # Clic derecho
                            if not celda_descubierta[y][x]:
                                celda_marcada[y][x] = not celda_marcada[y][x]

            dibujar_cuadricula(cuadricula, FILA, COL)

            if verificar_victoria(FILA, COL):
                fin_tiempo = time.time()
                tiempo_total = fin_tiempo - inicio_tiempo
                pantalla_final(f'¡Has ganado! Tiempo: {tiempo_total:.2f} segundos')
                jugando = False

    pygame.quit()

if __name__ == "__main__":
    main()
