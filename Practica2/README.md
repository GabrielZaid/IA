# Documentación del Proyecto del Juego

## Descripción General
Este proyecto es un juego desarrollado en Python utilizando la biblioteca Pygame. Integra modelos de aprendizaje automático para automatizar el juego, proporcionando tres modos de juego: manual, red neuronal, árbol de decisión y K-Nearest Neighbors (KNN). El juego presenta un personaje que debe evitar obstáculos e interactuar con varios elementos en la pantalla.

## Características
- **Modo Manual**: El jugador controla el personaje utilizando entradas del teclado.
- **Modo Red Neuronal**: Un modelo de red neuronal entrenado automatiza los movimientos y acciones del personaje.
- **Modo Árbol de Decisión**: Un modelo de árbol de decisión predice las acciones del personaje basado en datos del juego.
- **Modo KNN**: Un modelo K-Nearest Neighbors automatiza el juego basado en predicciones de proximidad.
- **Recolección de Datos**: El juego recopila datos durante el modo manual para entrenar los modelos de aprendizaje automático.
- **Obstáculos Dinámicos**: Incluye obstáculos terrestres y aéreos con comportamientos variados.

## Estructura del Juego
### Componentes Principales
1. **Personaje del Jugador**:
   - Controlado manualmente o por modelos de aprendizaje automático.
   - Puede moverse a la izquierda, derecha y saltar.
2. **Obstáculos**:
   - Obstáculos terrestres y aéreos que el jugador debe evitar.
   - Incluye proyectiles disparados por enemigos aéreos.
3. **Modelos de Aprendizaje Automático**:
   - **Red Neuronal**: Predice acciones de salto y movimientos.
   - **Árbol de Decisión**: Automatiza el juego basado en reglas de decisión.
   - **KNN**: Utiliza predicciones basadas en proximidad para las acciones.

### Funciones Clave
- `main()`: Punto de entrada del juego.
- `mostrar_menu()`: Muestra el menú principal y maneja la selección de modos.
- `mover_jugador()`: Maneja el movimiento del jugador.
- `manejar_salto()`: Administra la mecánica de salto.
- `update()`: Actualiza el estado del juego, incluyendo animaciones y movimientos de obstáculos.
- `entrenar_modelo()`: Entrena el modelo de red neuronal.
- `entrenar_arbol_salto()`: Entrena el árbol de decisión para predicciones de salto.
- `entrenar_knn_salto()`: Entrena el modelo KNN para predicciones de salto.

## Requisitos
- Python 3.8+
- Pygame
- TensorFlow
- scikit-learn
- numpy
- pandas
- matplotlib

Instala las dependencias utilizando:
```bash
pip install pygame tensorflow scikit-learn numpy pandas matplotlib
```

## Cómo Ejecutar
1. Asegúrate de que todas las dependencias estén instaladas.
2. Coloca los recursos necesarios en el directorio `assets/`.
3. Ejecuta el juego utilizando:
```bash
python game.py
```

## Entrenamiento de Modelos de Aprendizaje Automático
1. Juega en modo manual para recopilar datos.
2. Usa los datos recopilados para entrenar los modelos seleccionando la opción de entrenamiento adecuada en el menú.
3. Cambia al modo automatizado deseado (Red Neuronal, Árbol de Decisión o KNN) para ver los modelos en acción.

## Recursos
- **Sprites**: Ubicados en `assets/sprites/`.
- **Fondos**: Ubicados en `assets/game/`.
- **Audio**: Ubicados en `assets/audio/`.

## Notas
- Asegúrate de que el directorio `assets/` esté correctamente estructurado para evitar errores de archivos no encontrados.
- El juego requiere una cantidad mínima de datos para entrenar los modelos de aprendizaje automático de manera efectiva.