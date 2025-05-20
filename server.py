import socket
import threading
import datetime
import logging
import json

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('server.log'),
            logging.StreamHandler()
        ]
    )

def handle_client(connection, client_address):
    try:
        logging.info(f'{datetime.datetime.now().strftime("%H:%M:%S")} - Received connection from {client_address}')
        
        buffer = b""
        while True:
            data = connection.recv(1024)
            if not data:
                break
            
            buffer += data
            while b"\r\n" in buffer:
                message, buffer = buffer.split(b"\r\n", 1)
                decoded = message.decode('utf-8')
                
                if decoded == "TIME":
                    response_time = datetime.datetime.now().strftime("%H:%M:%S")
                    response = f"JAM {response_time}\r\n"
                    connection.sendall(response.encode('utf-8'))
                    logging.info(f'{datetime.datetime.now().strftime("%H:%M:%S")} - Sending response for TIME to {client_address}')
                elif decoded == "QUIT":
                    logging.info(f'{datetime.datetime.now().strftime("%H:%M:%S")} - Client {client_address} disconnected')
                    return
                    
    except Exception as e:
        logging.error(f'{datetime.datetime.now().strftime("%H:%M:%S")} - Error with {client_address}: {str(e)}')
    finally:
        connection.close()


def start_server():
    setup_logging()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 45000))
    server_socket.listen(5)
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    logging.info(f'{current_time} - Server started on port 45000')

    try:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        while True:
            connection, client_address = server_socket.accept()
            thread = threading.Thread(
                target=handle_client,
                args=(connection, client_address),
                daemon=True
            )
            thread.start()
    except KeyboardInterrupt:
        logging.info(f'{current_time} - Shutting down server...')
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
