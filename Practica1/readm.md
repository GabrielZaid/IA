# Documentación del Proyecto de Algoritmo A*

## Descripción General
Este proyecto implementa el algoritmo A* para encontrar el camino más corto en una cuadrícula. Utiliza la biblioteca Pygame para la visualización interactiva, permitiendo a los usuarios establecer nodos de inicio, fin y obstáculos, y observar cómo el algoritmo encuentra el camino óptimo.

## Características
- **Interfaz Interactiva**: Los usuarios pueden interactuar con la cuadrícula para definir el nodo de inicio, el nodo de fin y los obstáculos.
- **Visualización del Algoritmo**: Muestra en tiempo real los nodos explorados y el camino más corto encontrado.
- **Soporte para Movimientos Diagonales**: El algoritmo considera movimientos diagonales además de los horizontales y verticales.
- **Costos Personalizados**: Permite asignar costos adicionales a ciertos tipos de terreno (por ejemplo, agua).

## Estructura del Proyecto
### Componentes Principales
1. **Clase Nodo**:
   - Representa cada celda de la cuadrícula.
   - Almacena información como posición, color, vecinos, costos y el nodo padre.
2. **Funciones Clave**:
   - `crear_grid(filas)`: Crea la cuadrícula de nodos.
   - `dibujar(ventana, grid, filas)`: Dibuja la cuadrícula y actualiza la pantalla.
   - `conectar_vecinos(grid, filas)`: Conecta los nodos vecinos, incluyendo diagonales.
   - `a_estrella(start, end, grid)`: Implementa el algoritmo A* para encontrar el camino más corto.
   - `reconstruir_camino(end)`: Reconstruye y colorea el camino encontrado por A*.

## Requisitos
- Python 3.8+
- Pygame

Instala las dependencias utilizando:
```bash
pip install pygame
```

## Cómo Ejecutar
1. Asegúrate de que todas las dependencias estén instaladas.
2. Ejecuta el programa utilizando:
```bash
python main.py
```

## Instrucciones de Uso
1. **Definir Nodos**:
   - Haz clic izquierdo para establecer el nodo de inicio (verde), el nodo de fin (rojo) y los obstáculos (negro).
   - Haz clic derecho para eliminar nodos establecidos.
2. **Ejecutar el Algoritmo**:
   - Presiona la barra espaciadora para iniciar el algoritmo A*.
3. **Visualización**:
   - Los nodos explorados se colorean en amarillo.
   - El camino más corto se colorea en azul.

## Notas
- El tamaño de la cuadrícula es de 11x11, pero puede ajustarse modificando la constante `FILAS` en el código.
- El algoritmo utiliza la distancia de Manhattan como heurística.
- Asegúrate de cerrar la ventana de Pygame correctamente para evitar errores.

## Créditos
Desarrollado como una herramienta educativa para comprender el funcionamiento del algoritmo A* y su visualización interactiva.
