## Proyecto de Escalado de Imágenes Asíncrono

Este proyecto implementa un sistema de procesamiento y escalado de imágenes que utiliza programación asíncrona y paralela para recibir imágenes de clientes, enviarlas a un servidor de escalado, y devolver un enlace donde se puede descargar la imagen escalada.

## Estructura del Proyecto

Este proyecto está dividido en tres archivos principales:

-async_server.py: El servidor principal que recibe imágenes de clientes, las convierte a escala de grises, y se comunica con el servidor de escalado.
-scale_server.py: Un servidor de escalado que recibe la imagen y la redimensiona al 50% de su tamaño original.
-cliente.py: Un cliente que envía una imagen al servidor principal y recibe un enlace para descargar la imagen escalada.

## Requisitos

El proyecto requiere Python 3.8 o superior. A continuación se listan las bibliotecas necesarias, que se pueden instalar mediante pip.

## Extensiones y Paquetes Necesarios

-aiohttp: Para servir los archivos de imágenes escaladas a través de HTTP en async_server.py.
-Pillow (PIL): Para manipulación de imágenes en Python, utilizado tanto en async_server.py como en scale_server.py.

### Instala los paquetes con:

# pip install aiohttp pillow

Configuración
Asegúrate de tener el entorno configurado:

Ten Python 3.8+ instalado.
Instala los paquetes necesarios.
Archivos del Proyecto:

Coloca los archivos async_server.py, scale_server.py, y cliente.py en el mismo directorio de trabajo.

# Crear el Directorio de Almacenamiento:

El servidor async_server.py guardará las imágenes escaladas en una carpeta llamada scaled_images. Esta carpeta se creará automáticamente en la primera ejecución, pero asegúrate de que el directorio tiene permisos de escritura.

### Ejecución

## 1. Inicia el Servidor de Escalado

El servidor de escalado debe estar activo antes de ejecutar el servidor principal. Ejecuta el siguiente comando para iniciarlo:

python3 scale_server.py
Este servidor escuchará en 127.0.0.1:8001 para recibir y escalar imágenes.

## 2. Inicia el Servidor Principal Asíncrono

Una vez que el servidor de escalado esté en ejecución, inicia el servidor principal en otra terminal. Ejecuta el siguiente comando, especificando la dirección IP y el puerto donde deseas que escuche el servidor (por ejemplo, 127.0.0.1:8080):

python3 async_server.py --ip 127.0.0.1 --port 8080
El servidor principal estará escuchando en el puerto especificado y, además, servirá las imágenes escaladas en el puerto 8082.

## 3. Envía una Imagen desde el Cliente

Para enviar una imagen, abre una tercera terminal y ejecuta el siguiente comando. Asegúrate de reemplazar Eclipse.jpg con la ruta a tu imagen y ajusta la dirección IP y el puerto al del servidor asíncrono.

python3 cliente.py --ip 127.0.0.1 --port 8080 --image Eclipse.jpg
El cliente enviará la imagen y recibirá un enlace a la imagen escalada, que puedes abrir en el navegador.

## Ejemplo de Ejecución

-Servidor de Escalado:

python3 scale_server.py

Iniciando el servidor de escalado en 127.0.0.1:8001
Recibiendo imagen desde: ('127.0.0.1', 59004)
Tamaño de la imagen a recibir: 17909 bytes.
Recibido 17909 bytes de imagen.
Imagen recibida con dimensiones originales: 350x418
Imagen escalada a 175x209.
Escalado completado, imagen escalada enviada al cliente.

-Servidor Principal Asíncrono:

python3 async_server.py --ip 127.0.0.1 --port 8080

Intentando iniciar el servidor en 127.0.0.1:8080...
Servidor escuchando en 127.0.0.1:8080
Servidor de archivos escalados escuchando en http://127.0.0.1:8082
Cliente conectado.
Recibido 936034 bytes de la imagen del cliente.
Enlace de imagen escalada enviado al cliente: http://127.0.0.1:8082/scaled_image_1697058295.jpg

-Cliente:

python3 cliente.py --ip 127.0.0.1 --port 8080 --image Imagen.jpg

Conectando al servidor en 127.0.0.1:8080...
Conexión establecida.
Enviando imagen de tamaño 936034 bytes...
Imagen enviada, esperando respuesta del servidor...
Imagen escalada recibida y guardada como imagen_escalada.jpg.

## Consideraciones y Errores Comunes

Asegúrate de que los puertos 8080 (servidor principal) y 8082 (servidor HTTP de imágenes) no estén en uso antes de iniciar el servidor.
El cliente debe utilizar la misma IP y puerto del servidor principal.
Verifica que los archivos y carpetas tengan permisos de lectura y escritura en el sistema.