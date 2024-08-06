from PIL import Image
import numpy as np
import multiprocessing
from scipy.ndimage import gaussian_filter
import signal
import sys

# Punto 1: Carga y División de Imágenes
def cargar_dividir_imagen(ruta_imagen, n_partes):
    print(f"Cargando imagen desde {ruta_imagen} y dividiéndola en {n_partes} partes...")
    imagen = Image.open(ruta_imagen)
    ancho, alto = imagen.size
    parte_ancho = ancho // n_partes
    imagenes_partes = []

    for i in range(n_partes):
        izquierda = i * parte_ancho
        derecha = (i + 1) * parte_ancho if i < n_partes - 1 else ancho
        caja = (izquierda, 0, derecha, alto)
        parte = imagen.crop(caja)
        imagenes_partes.append(np.array(parte))

    print("División de imagen completada.")
    return imagenes_partes

# Punto 2: Aplicar filtro
def aplicar_filtro(parte_imagen):
    print("Aplicando filtro de desenfoque...")
    return gaussian_filter(parte_imagen, sigma=5)

# Punto 3: Procesamiento Paralelo con Pipe y Memoria Compartida
def worker_pipe_memoria(parte_imagen, indices_a_procesar, pipe_conn, shared_array, indice, ancho_parte):
    pid = multiprocessing.current_process().pid
    if indice in indices_a_procesar:
        print(f"Proceso {pid} está procesando la parte de imagen en el índice {indice} con filtro...")
        resultado = aplicar_filtro(parte_imagen)
    else:
        print(f"Proceso {pid} no está procesando la parte de imagen en el índice {indice}.")
        resultado = parte_imagen
    shared_array[indice * ancho_parte : (indice + 1) * ancho_parte] = resultado.flatten()
    pipe_conn.send(f"Proceso {pid} ha terminado de procesar la parte {indice}.")
    pipe_conn.close()

def procesar_con_pipe_memoria(imagenes_partes, indices_a_procesar):
    procesos = []
    padres_conexiones = []
    ancho_parte = imagenes_partes[0].size
    shared_array = multiprocessing.Array('d', ancho_parte * len(imagenes_partes))

    for i, parte in enumerate(imagenes_partes):
        padre_conn, hijo_conn = multiprocessing.Pipe()
        proceso = multiprocessing.Process(target=worker_pipe_memoria, args=(parte, indices_a_procesar, hijo_conn, shared_array, i, ancho_parte))
        procesos.append(proceso)
        padres_conexiones.append(padre_conn)
        proceso.start()

    resultados = [conn.recv() for conn in padres_conexiones]
    for resultado in resultados:
        print(resultado)

    for proceso in procesos:
        proceso.join()

    imagenes_procesadas = [np.array(shared_array[i * ancho_parte : (i + 1) * ancho_parte]).reshape(imagenes_partes[0].shape) for i in range(len(imagenes_partes))]
    return imagenes_procesadas

# Punto 4: Manejo de Señales
def manejador_senal(signal, frame):
    print('Interrupción recibida, terminando procesos...')
    sys.exit(0)

signal.signal(signal.SIGINT, manejador_senal)

# Combinación Final de Imágenes
def combinar_partes(imagenes_partes):
    altura = imagenes_partes[0].shape[0]
    anchura_total = sum([parte.shape[1] for parte in imagenes_partes])
    imagen_completa = np.zeros((altura, anchura_total, 3), dtype=np.uint8)

    x_offset = 0
    for parte in imagenes_partes:
        anchura = parte.shape[1]
        imagen_completa[:, x_offset:x_offset + anchura] = parte
        x_offset += anchura

    return Image.fromarray(imagen_completa)

# Función principal
def main():
    signal.signal(signal.SIGINT, manejador_senal)

    ruta_imagen = '/home/leo/Escritorio/Computacion_2/Compu2/Eclipse.jpg'
    n_partes = 4
    indices_a_procesar = [0, 1, 2]  # Índices de las partes a procesar (0, 1, 2, ...)

    # Cargar y dividir la imagen
    partes_imagen = cargar_dividir_imagen(ruta_imagen, n_partes)

    # Procesamiento con Pipe y Memoria Compartida
    resultados_procesados = procesar_con_pipe_memoria(partes_imagen, indices_a_procesar)

    # Combinar los resultados en una imagen final
    imagen_final = combinar_partes(resultados_procesados)
    imagen_final.save('imagen_procesada_v5.jpg')
    print("Imagen procesada y guardada como 'imagen_procesada_v5.jpg'.")

if __name__ == "__main__":
    main()
