import socket
import time
from datetime import datetime
import threading

SERVER_IP = '172.16.16.101'
SERVER_PORT = 45000

def sync_to_15_seconds():
    now = datetime.now()
    current_second = now.second
    delay = (15 - (current_second % 15)) % 15
    if delay == 0 and current_second != 0:
        delay = 15
    return delay

def script_runner(sock, running):
    while running[0]:
        delay = sync_to_15_seconds()
        print(f"[SCRIPT MODE] Next request in {delay} seconds")
        for _ in range(delay):
            if not running[0]:
                return
            time.sleep(1)
        if not running[0]:
            return
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Sending TIME")
            sock.sendall(b"TIME\r\n")
            response = sock.recv(1024).decode().strip()
            print(f"Server: {response}")
        except Exception as e:
            print(f"Script error: {e}")
            running[0] = False

def send_time_request():
    running = [True]
    script_mode = [False]
    script_thread = None

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_IP, SERVER_PORT))
            print(f"Connected to {SERVER_IP}:{SERVER_PORT}")

            while running[0]:
                cmd = input("Enter command (TIME, SCRIPT, QUIT): ").strip().upper()

                if cmd == "TIME":
                    s.sendall(b"TIME\r\n")
                    response = s.recv(1024).decode().strip()
                    print(response)

                elif cmd == "SCRIPT":
                    if script_mode[0]:
                        print("Script mode already running.")
                    else:
                        print("Starting script mode (15-second intervals)...")
                        script_mode[0] = True
                        script_thread = threading.Thread(target=script_runner, args=(s, running))
                        script_thread.daemon = True
                        script_thread.start()

                elif cmd == "QUIT":
                    running[0] = False
                    s.sendall(b"QUIT\r\n")
                    break

                else:
                    print("Invalid command. Use TIME, SCRIPT, or QUIT.")

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        print("Client shutting down...")

if __name__ == "__main__":
    send_time_request()
