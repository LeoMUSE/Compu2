import asyncio
from aiohttp import web
from PIL import Image
import io
import os
import socket

# Configuración de ruta de almacenamiento y URL base
SCALE_IMAGES_DIR = "./scaled_images"
BASE_URL = "http://127.0.0.1:8082"  # Puerto del servidor HTTP de archivos

# Asegúrate de que la carpeta exista
os.makedirs(SCALE_IMAGES_DIR, exist_ok=True)

async def process_image(reader, writer):
    print("Cliente conectado.")
    data = await reader.read(1000000)
    print(f"Recibido {len(data)} bytes de la imagen del cliente.")

    # Convertir a imagen y cambiar a escala de grises
    try:
        image = Image.open(io.BytesIO(data))
        image = image.convert("L")  # Escala de grises
    except Exception as e:
        print(f"Error al abrir la imagen: {e}")
        writer.close()
        return

    # Conectar y enviar la imagen al servidor de escalado
    scaled_image_data = await send_to_scale_server(image)
    if not scaled_image_data:
        print("Error: No se recibió la imagen escalada.")
        writer.close()
        return

    # Guardar la imagen escalada en el sistema de archivos y obtener su URL
    image_url = await save_and_get_image_url(scaled_image_data)
    response = f"Imagen escalada disponible en: {image_url}\n"
    
    writer.write(response.encode())
    await writer.drain()
    print(f"Enlace de imagen escalada enviado al cliente: {image_url}")
    writer.close()

async def send_to_scale_server(image):
    try:
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        image_data = image_bytes.getvalue()
        print(f"Enviando {len(image_data)} bytes al servidor de escalado.")

        reader, writer = await asyncio.open_connection('127.0.0.1', 8001)

        writer.write(len(image_data).to_bytes(4, 'big'))
        writer.write(image_data)
        await writer.drain()
        print("Imagen enviada al servidor de escalado.")

        scaled_size_data = await reader.read(4)
        scaled_size = int.from_bytes(scaled_size_data, 'big')
        scaled_image_data = await reader.read(scaled_size)
        writer.close()
        await writer.wait_closed()
        return scaled_image_data
    except (ConnectionError, asyncio.TimeoutError) as e:
        print(f"Error de conexión o tiempo de espera con el servidor de escalado: {e}")
        return None

async def save_and_get_image_url(image_data):
    image_name = f"scaled_image_{int(asyncio.get_event_loop().time())}.jpg"
    image_path = os.path.join(SCALE_IMAGES_DIR, image_name)

    with open(image_path, "wb") as f:
        f.write(image_data)
    print(f"Imagen escalada guardada en {image_path}")

    image_url = f"{BASE_URL}/{image_name}"
    return image_url

async def main(ip, port):
    print(f"Intentando iniciar el servidor en {ip}:{port}...")
    server = await asyncio.start_server(process_image, ip, port, family=socket.AF_UNSPEC)
    print(f"Servidor escuchando en {ip}:{port}")

    app = web.Application()
    app.router.add_static("/", SCALE_IMAGES_DIR)
    runner = web.AppRunner(app)
    await runner.setup()
    file_server = web.TCPSite(runner, "127.0.0.1", 8082)
    await file_server.start()
    print(f"Servidor de archivos escalados escuchando en {BASE_URL}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Servidor asincrónico de procesamiento de imágenes")
    parser.add_argument('--ip', required=True, help="Dirección IP de escucha")
    parser.add_argument('--port', type=int, required=True, help="Puerto de escucha")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.ip, args.port))
    except Exception as e:
        print(f"Error al iniciar el servidor: {e}")
