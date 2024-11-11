import asyncio
import argparse

async def send_image(image_path, ip, port):
    print(f"Conectando al servidor en {ip}:{port}...")
    try:
        reader, writer = await asyncio.open_connection(ip, port)
        print("Conexión establecida.")

        with open(image_path, 'rb') as f:
            image_data = f.read()

        print(f"Enviando imagen de tamaño {len(image_data)} bytes...")
        writer.write(image_data)
        await writer.drain()

        print("Imagen enviada, esperando respuesta del servidor...")
        response = await reader.read(1000)  
        print(response.decode())

        writer.close()
        await writer.wait_closed()
    except (ConnectionError, asyncio.TimeoutError) as e:
        print(f"Error de conexión o tiempo de espera: {e}")
    except FileNotFoundError:
        print("Error: El archivo de imagen especificado no se encuentra.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Cliente para enviar imágenes al servidor.")
    parser.add_argument('--ip', required=True, help="Dirección IP del servidor")
    parser.add_argument('--port', type=int, required=True, help="Puerto del servidor")
    parser.add_argument('--image', required=True, help="Ruta de la imagen a enviar")
    
    args = parser.parse_args()

    asyncio.run(send_image(args.image, args.ip, args.port))
