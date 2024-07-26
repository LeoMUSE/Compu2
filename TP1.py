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

# Punto 2: Procesamiento Paralelo
def aplicar_filtro(parte_imagen):
    # Aplicar un filtro de desenfoque
    return gaussian_filter(parte_imagen, sigma=5)

def procesar_en_paralelo(imagenes_partes):
    with multiprocessing.Pool(processes=len(imagenes_partes)) as pool:
        resultados = pool.map(aplicar_filtro, imagenes_partes)
    return resultados

# Punto 3: Comunicación y Sincronización
def worker(parte_imagen, conn):
    resultado = aplicar_filtro(parte_imagen)
    conn.send(resultado)
    conn.close()

def procesar_con_comunicacion(imagenes_partes):
    procesos = []
    padres_conexiones = []

    for parte in imagenes_partes:
        padre_conn, hijo_conn = multiprocessing.Pipe()
        proceso = multiprocessing.Process(target=worker, args=(parte, hijo_conn))
        procesos.append(proceso)
        padres_conexiones.append(padre_conn)
        proceso.start()

    resultados = [conn.recv() for conn in padres_conexiones]

    for proceso in procesos:
        proceso.join()

    return resultados

# Punto 4: Manejo de Señales
def manejador_señal(signal, frame):
    print('Interrupción recibida, terminando procesos...')
    sys.exit(0)

signal.signal(signal.SIGINT, manejador_señal)

# Punto 5: Uso de Memoria Compartida
def worker_memoria_compartida(parte_imagen, shared_array, indice, largo_parte):
    resultado = aplicar_filtro(parte_imagen)
    shared_array[indice * largo_parte : (indice + 1) * largo_parte] = resultado.flatten()

def procesar_con_memoria_compartida(imagenes_partes):
    largo_parte = imagenes_partes[0].size
    shared_array = multiprocessing.Array('d', largo_parte * len(imagenes_partes))

    procesos = []

    for i, parte in enumerate(imagenes_partes):
        proceso = multiprocessing.Process(target=worker_memoria_compartida, args=(parte, shared_array, i, largo_parte))
        procesos.append(proceso)
        proceso.start()

    for proceso in procesos:
        proceso.join()

    resultados = [np.array(shared_array[i * largo_parte : (i + 1) * largo_parte]).reshape(imagenes_partes[0].shape) for i in range(len(imagenes_partes))]
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
    ruta_imagen = '/home/leo/Escritorio/Computacion_2/Compu2/Eclipse.jpg'
    n_partes = 4

    # Cargar y dividir la imagen
    partes_imagen = cargar_dividir_imagen(ruta_imagen, n_partes)

    # Procesar las partes en paralelo con memoria compartida
    resultados_procesados_memoria_compartida = procesar_con_memoria_compartida(partes_imagen)

    # Combinar los resultados en una imagen final
    imagen_final = combinar_partes(resultados_procesados_memoria_compartida)
    imagen_final.save('imagen_procesada.jpg')

if __name__ == "__main__":
    main()
