import socket
from socketserver import TCPServer, BaseRequestHandler
from PIL import Image
import io
from multiprocessing import Process

class ScaleImageHandler(BaseRequestHandler):
    def handle(self):
        print(f"Recibiendo imagen desde: {self.client_address}")

        image_size_data = self.request.recv(4)
        if not image_size_data:
            print("No se recibió el tamaño de la imagen.")
            return

        image_size = int.from_bytes(image_size_data, 'big')
        print(f"Tamaño de la imagen a recibir: {image_size} bytes.")

        image_data = b""
        while len(image_data) < image_size:
            chunk = self.request.recv(min(4096, image_size - len(image_data)))
            if not chunk:
                break
            image_data += chunk
        print(f"Recibido {len(image_data)} bytes de imagen.")

        try:
            image = Image.open(io.BytesIO(image_data))
            print(f"Imagen recibida con dimensiones originales: {image.width}x{image.height}")

            scale_factor = 0.5
            new_width = int(image.width * scale_factor)
            new_height = int(image.height * scale_factor)
            scaled_image = image.resize((new_width, new_height))
            print(f"Imagen escalada a {new_width}x{new_height}.")

            img_byte_arr = io.BytesIO()
            scaled_image.save(img_byte_arr, format='JPEG')
            scaled_image_data = img_byte_arr.getvalue()

            self.request.sendall(len(scaled_image_data).to_bytes(4, 'big'))
            self.request.sendall(scaled_image_data)
            print("Escalado completado, imagen escalada enviada al cliente.")
        except Exception as e:
            print(f"Error al procesar la imagen: {e}")

def run_server(ip='127.0.0.1', port=8001):
    print(f"Iniciando el servidor de escalado en {ip}:{port}")
    with TCPServer((ip, port), ScaleImageHandler) as server:
        server.serve_forever()

if __name__ == "__main__":
    p = Process(target=run_server)
    p.start()
    p.join()
