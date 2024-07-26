from PIL import Image
import numpy as np
import multiprocessing
from scipy.ndimage import gaussian_filter
import signal
import sys

# Punto 1: Carga y División de Imágenes
def cargar_dividir_imagen(ruta_imagen, n_partes):
    # Cargar la imagen
    imagen = Image.open(ruta_imagen)
    ancho, alto = imagen.size

    # Dividir la imagen en partes iguales
    parte_ancho = ancho // n_partes
    imagenes_partes = []

    for i in range(n_partes):
        # Determinar las coordenadas de cada parte
        izquierda = i * parte_ancho
        derecha = (i + 1) * parte_ancho if i < n_partes - 1 else ancho
        caja = (izquierda, 0, derecha, alto)
        parte = imagen.crop(caja)
        imagenes_partes.append(np.array(parte))

    return imagenes_partes

# Punto 2: Aplicar filtro
def aplicar_filtro(parte_imagen):
    # Aplicar un filtro de desenfoque
    return gaussian_filter(parte_imagen, sigma=5)

# Punto 3: Procesamiento Paralelo con Pipe
def worker_pipe(parte_imagen, indices_a_procesar, conn, indice):
    if indice in indices_a_procesar:
        resultado = aplicar_filtro(parte_imagen)
    else:
        resultado = parte_imagen
    conn.send(resultado)
    conn.close()

def procesar_con_pipe(imagenes_partes, indices_a_procesar):
    procesos = []
    padres_conexiones = []

    for i, parte in enumerate(imagenes_partes):
        padre_conn, hijo_conn = multiprocessing.Pipe()
        proceso = multiprocessing.Process(target=worker_pipe, args=(parte, indices_a_procesar, hijo_conn, i))
        procesos.append(proceso)
        padres_conexiones.append(padre_conn)
        proceso.start()

    resultados = [conn.recv() for conn in padres_conexiones]

    for proceso in procesos:
        proceso.join()

    return resultados

# Punto 4: Manejo de Señales

def manejador_senal(signal, frame):
    print('Interrupción recibida, terminando procesos...')
    sys.exit(0)

signal.signal(signal.SIGINT, manejador_senal)

# Punto 5: Uso de Memoria Compartida

def worker_memoria_compartida(parte_imagen, shared_array, indice, ancho_parte, indices_a_procesar):
    if indice in indices_a_procesar:
        resultado = aplicar_filtro(parte_imagen)
    else:
        resultado = parte_imagen
    shared_array[indice * ancho_parte : (indice + 1) * ancho_parte] = resultado.flatten()

def procesar_con_memoria_compartida(imagenes_partes, indices_a_procesar):
    ancho_parte = imagenes_partes[0].size
    shared_array = multiprocessing.Array('d', ancho_parte * len(imagenes_partes))

    procesos = []

    for i, parte in enumerate(imagenes_partes):
        proceso = multiprocessing.Process(target=worker_memoria_compartida, args=(parte, shared_array, i, ancho_parte,indices_a_procesar),)
        procesos.append(proceso)
        proceso.start()

    for proceso in procesos:
        proceso.join()

    resultados = [np.array(shared_array[i * ancho_parte : (i + 1) * ancho_parte]).reshape(imagenes_partes[0].shape) for i in range(len(imagenes_partes))]
    return resultados

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

    # Elegir un método de procesamiento: Pipe o Memoria Compartida

    #resultados_procesados = procesar_con_pipe(partes_imagen, indices_a_procesar)
    resultados_procesados = procesar_con_memoria_compartida(partes_imagen, indices_a_procesar)

    # Combinar los resultados en una imagen final

    imagen_final = combinar_partes(resultados_procesados)
    imagen_final.save('imagen_procesada_v5.jpg')

if __name__ == "__main__":
    main()
