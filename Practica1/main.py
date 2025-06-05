import pygame
import heapq
import math

# Configuración de la ventana y el tamaño de la cuadrícula
ANCHO_VENTANA = 700  # Ancho de la ventana en píxeles
FILAS = 11  # Número de filas y columnas (cuadrícula de 11x11)
ANCHO_NODO = ANCHO_VENTANA // FILAS  # Tamaño de cada nodo en píxeles

# Definición de colores en formato RGB
BLANCO = (255, 255, 255)  # Espacio libre
NEGRO = (0, 0, 0)  # Paredes
GRIS = (200, 200, 200)  # Líneas de la cuadrícula
VERDE = (0, 255, 0)  # Nodo de inicio
ROJO = (255, 0, 0)  # Nodo de fin
AZUL = (0, 0, 255)  # Camino más corto
AMARILLO = (255, 255, 0)  # Nodos explorados

# Inicializar Pygame
pygame.init()
VENTANA = pygame.display.set_mode((ANCHO_VENTANA, ANCHO_VENTANA))  # Crear ventana
pygame.display.set_caption("A* - Exploración consistente")  # Título de la ventana
clock = pygame.time.Clock()  # Reloj para controlar la velocidad de fotogramas

# Clase Nodo que representa cada celda de la cuadrícula
class Nodo:
    def __init__(self, fila, col):
        self.fila = fila  # Fila en la cuadrícula
        self.col = col  # Columna en la cuadrícula
        self.x = fila * ANCHO_NODO  # Posición x en píxeles
        self.y = col * ANCHO_NODO  # Posición y en píxeles
        self.color = BLANCO  # Color inicial (espacio libre)
        self.vecinos = []  # Lista de nodos vecinos accesibles
        self.g = float('inf')  # Costo acumulado desde el inicio
        self.f = float('inf')  # Costo total estimado (g + heurística)
        self.padre = None  # Nodo previo en el camino
        self.explorado = False  # Si el nodo ha sido explorado

    def es_pared(self):
        return self.color == NEGRO  # Devuelve True si el nodo es una pared

    def hacer_inicio(self):
        self.color = VERDE  # Marca el nodo como inicio (color verde)

    def hacer_fin(self):
        self.color = ROJO  # Marca el nodo como fin (color rojo)

    def hacer_pared(self):
        self.color = NEGRO  # Marca el nodo como pared (color negro)

    def dibujar(self, ventana):
        pygame.draw.rect(ventana, self.color, (self.x, self.y, ANCHO_NODO, ANCHO_NODO))  # Dibuja el nodo

    def _lt_(self, other):
        if self.f == other.f:
            # Desempate basado en la posición (prioriza nodos con menor fila o columna)
            return (self.fila + self.col) < (other.fila + other.col)
        return self.f < other.f

# Crea la cuadrícula de nodos
def crear_grid(filas):
    grid = []
    for i in range(filas):
        grid.append([])
        for j in range(filas):
            nodo = Nodo(i, j)  # Crea un nodo en la posición (i, j)
            grid[i].append(nodo)
    return grid

# Dibuja las líneas de la cuadrícula
def dibujar_grid(ventana, filas):
    for i in range(filas):
        pygame.draw.line(ventana, GRIS, (0, i * ANCHO_NODO), (ANCHO_VENTANA, i * ANCHO_NODO))  # Líneas horizontales
        for j in range(filas):
            pygame.draw.line(ventana, GRIS, (j * ANCHO_NODO, 0), (j * ANCHO_NODO, ANCHO_VENTANA))  # Líneas verticales

# Dibuja la cuadrícula completa con los nodos
def dibujar(ventana, grid, filas):
    ventana.fill(BLANCO)  # Limpia la ventana con color blanco
    for fila in grid:
        for nodo in fila:
            nodo.dibujar(ventana)  # Dibuja cada nodo
    dibujar_grid(ventana, filas)  # Dibuja las líneas de la cuadrícula
    pygame.display.update()  # Actualiza la pantalla

# Obtiene la posición de un clic del mouse y la convierte en coordenadas de la cuadrícula
def obtener_click_pos(pos, filas):
    x, y = pos
    fila = x // ANCHO_NODO  # Calcula la fila en la cuadrícula
    col = y // ANCHO_NODO  # Calcula la columna en la cuadrícula
    return fila, col

# Conecta los nodos vecinos (incluyendo diagonales)
def conectar_vecinos(grid, filas):
    for fila in grid:
        for nodo in fila:
            if not nodo.es_pared():  # Si el nodo no es una pared
                # Vecinos horizontales y verticales
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if 0 <= nodo.fila + dx < filas and 0 <= nodo.col + dy < filas:
                        vecino = grid[nodo.fila + dx][nodo.col + dy]
                        if not vecino.es_pared():
                            nodo.vecinos.append(vecino)
                # Vecinos diagonales
                for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    if 0 <= nodo.fila + dx < filas and 0 <= nodo.col + dy < filas:
                        # Verificar que no haya paredes bloqueando el movimiento diagonal
                        if not grid[nodo.fila + dx][nodo.col].es_pared() and not grid[nodo.fila][nodo.col + dy].es_pared():
                            vecino = grid[nodo.fila + dx][nodo.col + dy]
                            if not vecino.es_pared():
                                nodo.vecinos.append(vecino)

# Función heurística: distancia de Chebyshev (adecuada para diagonales)
def heuristica(nodo1, nodo2):
    dx = abs(nodo1.fila - nodo2.fila)
    dy = abs(nodo1.col - nodo2.col)
    return dx + dy  # Distancia de Manhattan

# Algoritmo A* para encontrar el camino óptimo
def a_estrella(start, end, grid):
    open_set = []
    heapq.heappush(open_set, (start.f, 0, start))
    start.g = 0
    start.f = heuristica(start, end)
    counter = 0

    while open_set:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return []

        current = heapq.heappop(open_set)[2]
        current.explorado = True

        if current == end:
            return reconstruir_camino(end)

        for vecino in current.vecinos:
            dx = abs(vecino.fila - current.fila)
            dy = abs(vecino.col - current.col)
            # Coste base: 1 para rectos, √2 para diagonales
            costo_movimiento = 1 if dx + dy == 1 else math.sqrt(2)
            # Coste adicional basado en el terreno (ejemplo: agua tiene un coste de 2)
            if vecino.color == AZUL:  # Supongamos que el agua es de color azul
                costo_movimiento += 1
            tentative_g = current.g + costo_movimiento

            if tentative_g < vecino.g:
                vecino.padre = current
                vecino.g = tentative_g
                vecino.f = tentative_g + heuristica(vecino, end)
                if not any(vecino == item[2] for item in open_set):
                    counter += 1
                    heapq.heappush(open_set, (vecino.f, counter, vecino))

        # Visualización
        dibujar(VENTANA, grid, FILAS)
        for fila in grid:
            for nodo in fila:
                if nodo.explorado and nodo != start and nodo != end:
                    nodo.color = AMARILLO
        start.dibujar(VENTANA)
        end.dibujar(VENTANA)
        pygame.display.update()
        clock.tick(30)

    return []

# Reconstruye el camino encontrado por A*
def reconstruir_camino(end):
    camino = []
    current = end
    while current.padre:  # Recorre los nodos padres desde el fin hasta el inicio
        camino.append(current)
        current = current.padre
    camino.reverse()  # Invierte el camino para que vaya de inicio a fin
    for nodo in camino:
        nodo.color = AZUL  # Colorea el camino de azul
    pygame.display.update()  # Actualiza la pantalla
    return camino

# Función principal del programa
def main():
    grid = crear_grid(FILAS)  # Crea la cuadrícula
    start = None  # Nodo de inicio
    end = None  # Nodo de fin
    running = True  # Controla el bucle principal
    solving = False  # Indica si el algoritmo está en ejecución

    while running:
        dibujar(VENTANA, grid, FILAS)  # Dibuja la cuadrícula
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Si el usuario cierra la ventana
                running = False

            if pygame.mouse.get_pressed()[0] and not solving:  # Clic izquierdo
                pos = pygame.mouse.get_pos()
                fila, col = obtener_click_pos(pos, FILAS)  # Obtiene la posición del clic
                clicked_node = grid[fila][col]  # Nodo clickeado
                if not start and clicked_node != end:  # Si no hay inicio, establece el inicio
                    start = clicked_node
                    start.hacer_inicio()
                elif not end and clicked_node != start:  # Si no hay fin, establece el fin
                    end = clicked_node
                    end.hacer_fin()
                elif clicked_node != start and clicked_node != end:  # Si no es inicio ni fin, establece una pared
                    clicked_node.hacer_pared()

            if pygame.mouse.get_pressed()[2] and not solving:  # Clic derecho
                pos = pygame.mouse.get_pos()
                fila, col = obtener_click_pos(pos, FILAS)  # Obtiene la posición del clic
                clicked_node = grid[fila][col]  # Nodo clickeado
                if clicked_node == start:  # Si es el inicio, lo elimina
                    start.color = BLANCO  # Restablece el color
                    start = None  # Restablece la variable start
                elif clicked_node == end:  # Si es el fin, lo elimina
                    end.color = BLANCO  # Restablece el color
                    end = None  # Restablece la variable end
                elif clicked_node.es_pared():  # Si es una pared, la elimina
                    clicked_node.color = BLANCO  # Restablece el color

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end and not solving:  # Presiona espacio para iniciar A*
                    conectar_vecinos(grid, FILAS)  # Conecta los vecinos
                    solving = True  # Indica que el algoritmo está en ejecución
                    a_estrella(start, end, grid)  # Ejecuta A*

    pygame.quit()  # Cierra Pygame

if __name__ == "__main__":
    main()  # Ejecuta la función principal