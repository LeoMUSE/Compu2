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

def procesar_parte(parte_imagen, indices_a_procesar, parte_indice):
    if parte_indice in indices_a_procesar:
        return aplicar_filtro(parte_imagen)
    else:
        return parte_imagen

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
    indices_a_procesar = [0, 1, 2]  # Índices de las partes a procesar (0, 1, 2, ...)

    # Cargar y dividir la imagen
    partes_imagen = cargar_dividir_imagen(ruta_imagen, n_partes)

    # Procesar las partes especificadas
    resultados_procesados = [
        procesar_parte(parte, indices_a_procesar, i) for i, parte in enumerate(partes_imagen)
    ]

    # Combinar los resultados en una imagen final
    imagen_final = combinar_partes(resultados_procesados)
    imagen_final.save('imagen_procesada_parte_3_de_4.jpg')

if __name__ == "__main__":
    main()
