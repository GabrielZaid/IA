import pygame
import random
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import os

# importaciones----------------------------------------------------------------------------------
import numpy as np
from tensorflow.keras.utils import to_categorical
import sklearn.base
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Configuración ------------------------------------------------------------------------------------
# Ruta base donde están los assets porque si no da errores
BASE_DIR = os.path.dirname(__file__)

def cargar_imagen(rel_path):
    ruta = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(ruta):
        print(f"Archivo no encontrado: {ruta}")
    return pygame.image.load(ruta)

pygame.init()

# Asignación de variables y configuración de la pantalla ---------------------------------------------------
# Pantalla
w, h = 800, 400
pantalla = pygame.display.set_mode((w, h))
pygame.display.set_caption("Proyecto final de IA")

# Coloritos
BLANCO = (255, 255, 255)
NEGRO = (92, 29, 73)
ROJO = (228, 65, 110)
AZUL = (65, 136, 228)

# Variables
jugador = None
bala_suelo = None
bala_aire = None
fondo = None
enemigo_tierra = None
menu = None

# Variables de salto
salto = False
salto_altura = 15  # Velocidad inicial de salto
gravedad = 1
en_suelo = True
subiendo = True

# Pausa y menú
pausa = False
fuente_grande = pygame.font.SysFont('Arial', 28) #Fuente grandota
fuente_media = pygame.font.SysFont('Arial', 24) #Fuente chiquita
menu_activo = True 
modo_rn = False  # Indica si el modo de juego es automático
modo_arbol = False  # Indica si el modo de juego es árbol de decisión
modo_knn = False # Indica si el modo de juego es K vecinos más cercanos

# Lista para guardar los datillos
datos_modelo = []
modelo_entrenado = None
modelo_entrenado_arbol = None
movimiento_entrenado_arbol = None

datos_movimiento = []
modelo_entrenado_movimiento = []

intervalo_decidir_salto = 1  # Intervalo de frames para decidir si saltar
contador_decidir_salto = 0

# Cargar imágenes de enemigos y balas
bala_img = pygame.transform.scale(cargar_imagen('assets/sprites/naruto/ramen.png'), (50, 50))
bala_aire_img = pygame.transform.scale(cargar_imagen('assets/sprites/ball.png'), (30, 30))

fondo_img = cargar_imagen('assets/game/fn_naruto.png')
enemigo_tierra_img = cargar_imagen('assets/sprites/naruto/jiray.png')
enemigo_aereo_img = pygame.transform.scale(cargar_imagen('assets/sprites/naruto/oroch.png'), (120, 100))
menu_img = cargar_imagen('assets/game/menu.png')

fondo_img = pygame.transform.scale(fondo_img, (w, h))

# Crear los rectángulos de las variables
jugador = pygame.Rect(50, h - 100, 32, 48)
bala_suelo = pygame.Rect(w - 50, h - 90, 16, 16)
bala_aire = pygame.Rect(0, -50, 16, 16)  
enemigo_tierra = pygame.Rect(w - 100, h - 130, 64, 64)
enemigo_aereo = pygame.Rect(0, 0, 64, 64)  

# Variables para el movimiento
zigzag_direccion = 1  #Derecha e izquierda
zigzag_velocidad = 5  # Velocidad en zigzag
enemigo_aereo_disparo_cooldown = 0
enemigo_aereo_disparo_intervalo = 60  # frames entre disparos
velocidad_bala_aire = [0, 5]  # [velocidad_x, velocidad_y]

menu_rect = pygame.Rect(w // 2 - 135, h // 2 - 90, 270, 180)  # Para el menú

# Variables de animación
current_frame = 0
frame_speed = 10  
frame_count = 0

# Variables para las balas
velocidad_bala_suelo = -10 
bala_disparada_suelo = False
bala_disparada_aire = False

fondo_x1 = 0
fondo_x2 = w

ultimo_disparo_aire = 0

# Movimiento del enemigo aéreo 
def mover_enemigo_aereo():
    global enemigo_aereo, zigzag_direccion, enemigo_aereo_disparo_cooldown
    enemigo_aereo.x += zigzag_direccion * zigzag_velocidad
    enemigo_aereo_disparo_cooldown -= 1
    
    # Cambiar dirección para los límites
    if enemigo_aereo.x <= 0 or enemigo_aereo.x >= 200 - enemigo_aereo.width:
        zigzag_direccion *= -1

def disparar_bala_aire():
    global bala_aire, bala_disparada_aire, velocidad_bala_aire, ultimo_disparo_aire, enemigo_aereo_disparo_cooldown
    
    # Solo disparar si el cooldown ha terminado y Miku está en pantalla
    if not bala_disparada_aire and enemigo_aereo_disparo_cooldown <= 0 and 0 <= enemigo_aereo.x <= w:
        # La bala comienza en la posición de Miku
        bala_aire.x = enemigo_aereo.x + enemigo_aereo.width // 2 - bala_aire.width // 2
        bala_aire.y = enemigo_aereo.y + enemigo_aereo.height
        
        # Velocidad para disparo inferior
        velocidad_bala_aire[0] = 0  
        velocidad_bala_aire[1] = 5  
        
        bala_disparada_aire = True
        enemigo_aereo_disparo_cooldown = enemigo_aereo_disparo_intervalo
        ultimo_disparo_aire = pygame.time.get_ticks()

# Jueguito
def disparar_bala():
    global bala_disparada_suelo, velocidad_bala_suelo
    if not bala_disparada_suelo:
        velocidad_bala_suelo = random.randint(-8, -3)
        bala_disparada_suelo = True

def mover_jugador():
    global jugador, en_suelo, salto, pos_actual
    keys = pygame.key.get_pressed()
    pos_actual = 1  # Posición inicial en el centro
    # Limitar el movimiento del jugador al rango de 0 a 200
    if keys[pygame.K_LEFT] and jugador.x > 0:
        jugador.x -= 5
        pos_actual = 0
    if keys[pygame.K_RIGHT] and jugador.x < 200 - jugador.width:
        jugador.x += 5
        pos_actual = 2
    if keys[pygame.K_UP] and en_suelo:
        salto = True
        en_suelo = False

def reset_bala():
    global bala_suelo, bala_disparada_suelo
    bala_suelo.x = w - 50
    bala_disparada_suelo = False
    
def reset_bala_aire():
    global bala_aire, bala_disparada_aire
    bala_aire.y = -50
    bala_disparada_aire = False    

def manejar_salto():
    global jugador, salto, salto_altura, gravedad, en_suelo, subiendo

    if salto:
        if subiendo:
            jugador.y -= salto_altura
            salto_altura -= gravedad

            if salto_altura <= 0:
                subiendo = False
        else:
            jugador.y += salto_altura
            salto_altura += gravedad

            if jugador.y >= h - 100:
                jugador.y = h - 100
                salto = False
                salto_altura = 15
                subiendo = True
                en_suelo = True

def update():
    global bala_suelo, bala_aire, current_frame, frame_count, fondo_x1, fondo_x2
    mover_enemigo_aereo()
    
    # Imagenes de Len
    jugador_rect = [
         pygame.image.load('assets/sprites/mono_frame_1.png'),
         pygame.image.load('assets/sprites/mono_frame_2.png'),
         pygame.image.load('assets/sprites/mono_frame_3.png'),
         pygame.image.load('assets/sprites/mono_frame_4.png')
    ]

    jugador_rect_salto = [
        pygame.transform.scale(pygame.image.load(r'assets/sprites/mono_frame_1.png'), (35, 45)),
        pygame.transform.scale(pygame.image.load(r'assets/sprites/mono_frame_2.png'), (35, 45)),
    ]

    # Mover el fondo
    fondo_x1 -= 3
    fondo_x2 -= 3

    if fondo_x1 <= -w:
        fondo_x1 = w
    if fondo_x2 <= -w:
        fondo_x2 = w

    pantalla.blit(fondo_img, (fondo_x1, 0))
    pantalla.blit(fondo_img, (fondo_x2, 0))

    # Animación de Lencito
    if salto:
        if subiendo:
            pantalla.blit(jugador_rect_salto[0], (jugador.x, jugador.y))
        else:
            pantalla.blit(jugador_rect_salto[1], (jugador.x, jugador.y))
    else:
        frame_count += 10
        if frame_count >= frame_speed:
            current_frame = (current_frame + 1) % len(jugador_rect)
            frame_count = 0
        pantalla.blit(jugador_rect[current_frame], (jugador.x, jugador.y))

    pantalla.blit(enemigo_tierra_img, (enemigo_tierra.x, enemigo_tierra.y))
    pantalla.blit(enemigo_aereo_img, (enemigo_aereo.x, enemigo_aereo.y+75))

    # Balitas
    if bala_disparada_suelo:
        bala_suelo.x += velocidad_bala_suelo
        pantalla.blit(bala_img, (bala_suelo.x, bala_suelo.y))
        
    if bala_disparada_aire:
        bala_aire.x += velocidad_bala_aire[0]  
        bala_aire.y += velocidad_bala_aire[1]  
        pantalla.blit(bala_aire_img, (bala_aire.x, bala_aire.y))

    if bala_suelo.x < 0:
        reset_bala()
        
    if bala_aire.y > h or bala_aire.x < 0 or bala_aire.x > w:
        reset_bala_aire()

    # Detectar colisiones    
    if jugador.colliderect(bala_suelo) or  jugador.colliderect(bala_aire): 
        print("Colisión detectada, estás muerto.")
        reiniciar_juego()

def guardar_datos():
    global jugador, bala_suelo, velocidad_bala_suelo, salto
    distancia_suelo = abs(jugador.x - bala_suelo.x)
    salto_hecho = 1 if salto else 0

    distancia_aire_x = abs(jugador.centerx - bala_aire.centerx)
    distancia_aire_y = abs(jugador.centery - bala_aire.centery)
    hay_bala_aire = 1 if bala_disparada_aire else 0

    datos_modelo.append((
        velocidad_bala_suelo,
        distancia_suelo,
        distancia_aire_x,
        distancia_aire_y,
        hay_bala_aire,
        jugador.x,
        salto_hecho
    ))

    distancia_bala_suelo = abs(jugador.x - bala_suelo.x)

    datos_movimiento.append((
        jugador.x,
        jugador.y,
        bala_aire.centerx,
        bala_aire.centery,
        bala_suelo.x,
        bala_suelo.y,
        distancia_bala_suelo,
        1 if salto else 0,
        pos_actual
    ))

def pausa_juego():
    global pausa
    pausa = not pausa
    if pausa:
        imprimir_datos()
    else:
        print("Juego reanudado.")

def mostrar_menu():
    global menu_activo, modo_rn, modo_arbol, modo_knn
    global datos_modelo, datos_movimiento
    global modelo_entrenado, modelo_entrenado_movimiento
    global modelo_entrenado_arbol, movimiento_entrenado_arbol

    pantalla.fill(NEGRO)
    pantalla.blit(fuente_grande.render("MENU PRINCIPAL", True, BLANCO), (w//2 - 120, h//4 - 30))
    
    pantalla.blit(fuente_media.render("Presiona 'R' para Modo Red Neuronal", True, BLANCO), (w//2 - 180, h//4 + 30))
    pantalla.blit(fuente_media.render("Presiona 'M' para Modo Manual", True, BLANCO), (w//2 - 180, h//4 + 55))
    pantalla.blit(fuente_media.render("Presiona 'E' para Entrenar Modelo", True, BLANCO), (w//2 - 180, h//4 + 80))
    pantalla.blit(fuente_media.render("Presiona 'A' para Modo Arbol", True, BLANCO), (w//2 - 180, h//4 + 105))
    pantalla.blit(fuente_media.render("Presiona 'K' para KNN", True, BLANCO), (w//2 - 180, h//4 + 130))
    pantalla.blit(fuente_media.render("Presiona 'Q' para Salir", True, BLANCO), (w//2 - 180, h//4 + 155))
    pygame.display.flip()

    while menu_activo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    if(datos_modelo and datos_movimiento):
                        modo_rn = True
                        modo_arbol = False
                        modo_knn = False
                        menu_activo = False
                    else:
                        print("Falta jugar para obtener datos, presiona 'M'")
                if evento.key == pygame.K_e:
                    if len(datos_modelo) > 0 and len(datos_movimiento) > 0:
                        modelo_entrenado = entrenar_modelo(datos_modelo)
                        modelo_entrenado_movimiento = entrenar_red_movimiento(datos_movimiento)

                elif evento.key == pygame.K_m:
                    modo_rn = False
                    modo_arbol = False
                    modo_knn = False
                    menu_activo = False
                    datos_modelo = []
                    datos_movimiento = []
                elif evento.key == pygame.K_a:
                    modo_rn = False
                    modo_arbol = True
                    modo_knn = False
                    menu_activo = False
                    modelo_entrenado_arbol = entrenar_arbol_salto(datos_modelo)
                    movimiento_entrenado_arbol = entrenar_arbol_movimiento(datos_movimiento)
                elif evento.key == pygame.K_x:
                    reiniciar_juego()    
                if evento.key == pygame.K_k:
                    modo_rn = False
                    modo_arbol = False
                    modo_knn = True
                    menu_activo = False
                    modelo_entrenado = entrenar_knn_salto(datos_modelo)
                    modelo_entrenado_movimiento = entrenar_knn_movimiento(datos_movimiento, jugador)    
                elif evento.key == pygame.K_q:
                    imprimir_datos()
                    pygame.quit()
                    exit()

def reiniciar_juego():
    global menu_activo, jugador, bala_suelo, bala_aire, enemigo_tierra, bala_disparada_suelo, bala_disparada_aire, salto, en_suelo
    menu_activo = True
    jugador.x, jugador.y = 50, h - 100
    bala_suelo.x = w - 50
    bala_aire.y = -50
    enemigo_tierra.x, enemigo_tierra.y = w - 100, h - 100
    bala_disparada_suelo = False
    bala_disparada_aire = False
    salto = False
    en_suelo = True
    imprimir_datos()
    mostrar_menu()
    
def imprimir_datos():
    for dato in datos_movimiento:
        print(dato)
        
def main():
    global salto, en_suelo, bala_disparada_suelo, bala_disparada_aire, contador_decidir_salto

    reloj = pygame.time.Clock()
    mostrar_menu()
    correr = True

    while correr:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                correr = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and en_suelo and not pausa:
                    salto = True
                    en_suelo = False
                if evento.key == pygame.K_p:
                    pausa_juego()
                if evento.key == pygame.K_q:
                    imprimir_datos()
                    pygame.quit()
                    exit()

        if not pausa:
            # Modo manual
            if not modo_rn and not modo_arbol and not modo_knn:
                mover_jugador()
                if salto:
                    manejar_salto()
                guardar_datos()

            # Modo Red neuronal
            if modo_rn and modelo_entrenado and modelo_entrenado_movimiento:
                    salto, en_suelo = decidir_salto(jugador, bala_suelo, velocidad_bala_suelo, bala_aire, bala_disparada_aire, modelo_entrenado, salto, en_suelo)
                    manejar_salto()
                    jugador.x, pos_actual = decidir_movimiento(jugador, bala_aire, modelo_entrenado_movimiento, salto, bala_suelo)
                    mover_jugador()
            # Modo KNN
            if modo_knn:         
                    salto, en_suelo = decidir_salto_knn(jugador, bala_suelo, velocidad_bala_suelo, bala_aire, bala_disparada_aire, modelo_entrenado, salto, en_suelo)
                    manejar_salto()
                    jugador.x, pos_actual = decidir_movimiento_knn(jugador, bala_aire, modelo_entrenado_movimiento, salto, bala_suelo)

            # Modo Árbol de decisión
            if modo_arbol:         
                    salto, en_suelo = decidir_salto_arbol(jugador, bala_suelo, velocidad_bala_suelo, bala_aire, bala_disparada_aire, modelo_entrenado_arbol, salto, en_suelo)
                    manejar_salto()
                    jugador.x, pos_actual = decidir_movimiento_arbol(jugador, bala_aire, movimiento_entrenado_arbol, salto, bala_suelo)

            if not bala_disparada_suelo:
                disparar_bala()
                
            disparar_bala_aire()
            
            update()
                            
        pygame.display.flip()
        reloj.tick(30)

    pygame.quit()



# Apartado para el modelo de arbol de decisión ---------------------------------------------------------------------------------
def entrenar_arbol_salto(datos_modelo):
    if len(datos_modelo) < 10:
        print("No hay suficientes datos para entrenar el árbol.")
        return None

    datos = np.array(datos_modelo)
    X = datos[:, :6] 
    y = datos[:, 6]  

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    arbol = DecisionTreeClassifier(max_depth=10)
    arbol.fit(X_train, y_train)

    accuracy = arbol.score(X_test, y_test)
    print(f"Precisión del árbol de salto: {accuracy:.2f}")

    return arbol

def decidir_salto_arbol(jugador, bala, velocidad_bala, bala_aire, bala_disparada_aire, arbol_salto, salto, en_suelo):
    if arbol_salto is None:
        print("Árbol no entrenado.")
        return salto, en_suelo

    distancia_suelo = abs(jugador.x - bala.x)
    distancia_aire_x = abs(jugador.centerx - bala_aire.centerx)
    distancia_aire_y = abs(jugador.centery - bala_aire.centery)
    hay_bala_aire = 1 if bala_disparada_aire else 0

    entrada = np.array([[velocidad_bala, distancia_suelo, distancia_aire_x, distancia_aire_y, hay_bala_aire, jugador.x]])

    prediccion = arbol_salto.predict(entrada)[0]

    if prediccion == 1 and en_suelo:
        salto = True
        en_suelo = False

    return salto, en_suelo

def entrenar_arbol_movimiento(datos_movimiento):
    if len(datos_movimiento) < 10:
        print("No hay suficientes datos para entrenar el árbol de movimiento.")
        return None

    datos = np.array(datos_movimiento)
    X = datos[:, :8].astype('float32')
    y = datos[:, 8].astype('int') 

    arbol = DecisionTreeClassifier(max_depth=10)
    arbol.fit(X, y)

    return arbol

def decidir_movimiento_arbol(jugador, bala_aire, arbol_movimiento, salto, bala_suelo):
    if arbol_movimiento is None:
        print("Árbol de movimiento no entrenado.")
        return jugador.x, 1 

    distancia_bala_suelo = abs(jugador.x - bala_suelo.x)

    entrada = np.array([[
        jugador.x,
        jugador.y,
        bala_aire.centerx,
        bala_aire.centery,
        bala_suelo.x,
        bala_suelo.y,
        distancia_bala_suelo,
        1 if salto else 0
    ]], dtype='float32')

    accion = arbol_movimiento.predict(entrada)[0]

    if accion == 0 and jugador.x > 0:
        jugador.x -= 5
    elif accion == 2 and jugador.x < 200 - jugador.width:
        jugador.x += 5
    else:
        jugador.x += 0  

    return jugador.x, accion

# Apartado para el modelo de KNN -----------------------------------------------------------------------------------------------
def entrenar_knn_salto(datos_modelo):
    if len(datos_modelo) < 10:
        print("Insuficientes datos para entrenar el modelo KNN de salto.")
        return None

    datos = np.array(datos_modelo)
    X = datos[:, :6] 
    y = datos[:, 6]  

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo_knn = KNeighborsClassifier(n_neighbors=10)
    modelo_knn.fit(X_train, y_train)

    accuracy = modelo_knn.score(X_test, y_test)
    print(f"Precisión del modelo KNN de salto: {accuracy:.2f}")
    
    return modelo_knn

def decidir_salto_knn(jugador, bala, velocidad_bala, bala_aire, bala_disparada_aire, modelo_knn, salto, en_suelo):
    if modelo_knn is None:
        print("Modelo KNN no entrenado. No se puede decidir.")
        return False, en_suelo

    distancia_suelo = abs(jugador.x - bala.x)
    distancia_aire_x = abs(jugador.centerx - bala_aire.centerx)
    distancia_aire_y = abs(jugador.centery - bala_aire.centery)
    hay_bala_aire = 1 if bala_disparada_aire else 0

    entrada = np.array([[velocidad_bala, distancia_suelo, distancia_aire_x, distancia_aire_y, hay_bala_aire, jugador.x]])

    prediccion = modelo_knn.predict(entrada)[0]

    if prediccion == 1 and en_suelo:
        salto = True
        en_suelo = False

    return salto, en_suelo

def entrenar_knn_movimiento(datos_movimiento, jugador):
    if len(datos_movimiento) < 10:
        print("Insuficientes datos para entrenar el modelo KNN de movimiento.")
        return jugador.x, 1

    datos = np.array(datos_movimiento)
    X = datos[:, :8].astype('float32') 
    y = datos[:, 8].astype('int') 

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo_knn = KNeighborsClassifier(n_neighbors=10)
    modelo_knn.fit(X_train, y_train)

    accuracy = modelo_knn.score(X_test, y_test)
    print(f"Precisión del modelo KNN de movimiento: {accuracy:.2f}")

    return modelo_knn

def decidir_movimiento_knn(jugador, bala_aire, modelo_knn_mov, salto, bala_suelo):
    if modelo_knn_mov is None:
        print("Modelo KNN de movimiento no entrenado.")
        return None

    distancia_bala_suelo = abs(jugador.x - bala_suelo.x)

    entrada = np.array([[jugador.x,
                         jugador.y,
                         bala_aire.centerx,
                         bala_aire.centery,
                         bala_suelo.x,
                         bala_suelo.y,
                         distancia_bala_suelo,
                         1 if salto else 0
                         ]], dtype='float32')

    prediccion = modelo_knn_mov.predict(entrada)
    accion = int(prediccion[0])

    if accion == 0 and jugador.x > 0:
        jugador.x -= 5
    elif accion == 2 and jugador.x < 200 - jugador.width:
        jugador.x += 5
    else:
        jugador.x = jugador.x

    return jugador.x, accion



# Apartado para el modelo de red neuronal --------------------------------------------------------------------------------
def entrenar_modelo(datos_modelo):
    if len(datos_modelo) < 10:
        print("Insuficientes datos para entrenar el modelo.")
        return None

    datos = np.array(datos_modelo)
    X = datos[:, :6]  # Nuevas 6 características
    y = datos[:, 6]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo = Sequential([
        Dense(32, input_dim=6, activation='relu'),
        Dense(32, activation='relu'),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    modelo.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    modelo.fit(X_train, y_train, epochs=100, batch_size=32, verbose=1)
    loss, accuracy = modelo.evaluate(X_test, y_test, verbose=0)
    print(f"Modelo entrenado con precisión: {accuracy:.2f}")
    
    return modelo

def decidir_salto(jugador, bala, velocidad_bala, bala_aire, bala_disparada_aire, modelo_entrenado, salto, en_suelo):
    if modelo_entrenado is None:
        print("Modelo no entrenado. No se puede decidir.")
        return False, en_suelo

    distancia_suelo = abs(jugador.x - bala.x)
    distancia_aire_x = abs(jugador.centerx - bala_aire.centerx)
    distancia_aire_y = abs(jugador.centery - bala_aire.centery)
    hay_bala_aire = 1 if bala_disparada_aire else 0

    entrada = np.array([[velocidad_bala, distancia_suelo, distancia_aire_x, distancia_aire_y, hay_bala_aire, jugador.x]])

    # Detecta si es un modelo de scikit-learn
    if isinstance(modelo_entrenado, sklearn.base.ClassifierMixin):
        prediccion = modelo_entrenado.predict(entrada)[0]
        # Si el modelo devuelve 0/1, puedes usarlo directamente
        prediccion = float(prediccion)
    else:
        prediccion = modelo_entrenado.predict(entrada, verbose=0)[0][0]

    if prediccion > 0.5 and en_suelo:
        salto = True
        en_suelo = False

    return salto, en_suelo

def entrenar_red_movimiento(datos_movimiento):
    if len(datos_movimiento) < 10:
        print("No hay suficientes datos para entrenar.")
        return None

    datos = np.array(datos_movimiento)
    X = datos[:, :8].astype('float32') 
    y = datos[:, 8].astype('int')

    y_categorical = to_categorical(y, num_classes=3)

    X_train, X_test, y_train, y_test = train_test_split(X, y_categorical, test_size=0.2, random_state=42)

    model = Sequential([
        Dense(64, input_dim=8, activation='relu'),
        Dense(32, activation='relu'),
        Dense(3, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=1)

    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"Precisión del modelo de movimiento: {accuracy:.2f}")
    
    return model

def decidir_movimiento(jugador, bala, modelo_movimiento, salto, bala_suelo):
    if modelo_movimiento is None:
        print("Modelo no entrenado.")
        return jugador.x, 1 

    distancia_bala_suelo = abs(jugador.x - bala_suelo.x)

    entrada = np.array([[
        jugador.x,                    
        jugador.y,                    
        bala.centerx,                  
        bala.centery,                 
        bala_suelo.x,                 
        bala_suelo.y,                 
        distancia_bala_suelo,         
        1 if salto else 0             
    ]], dtype='float32')

    prediccion = modelo_movimiento.predict(entrada, verbose=0)[0]
    accion = np.argmax(prediccion)

    if accion == 0 and jugador.x > 0:
        jugador.x -= 5
    elif accion == 2 and jugador.x < 200 - jugador.width:
        jugador.x += 5
    else:
        jugador.x += 0

    return jugador.x, accion


if __name__ == "__main__":
    main()