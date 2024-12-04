import socket
import threading
from cryptography.fernet import Fernet

HOST = '127.0.0.1'
PORT = 65432

# Generate a key for encryption
key = Fernet.generate_key()
cipher = Fernet(key)

connections = []
messages = {}  # Store messages with format {msg_id: (client_id, message)}
clients = {}  # Map client addresses to sockets

def handle_client(conn, addr):
    client_id = addr
    connections.append(conn)
    clients[addr] = conn
    try:
        while True:
            encrypted_message = conn.recv(1024)
            if not encrypted_message:
                break

            # Decrypt the message
            try:
                message = cipher.decrypt(encrypted_message).decode()
            except Exception as e:
                print(f"[ERROR] Decryption failed: {e}")
                continue

            print(f"[RECEIVED] from {addr}: {message}")

            if message.startswith("DELETE"):
                # Handle delete requests
                _, msg_id = message.split()
                msg_id = int(msg_id)

                if msg_id in messages and messages[msg_id][0] == client_id:
                    for c in connections:
                        c.send(cipher.encrypt(f"DELETE {msg_id}".encode('utf-8')))
                    del messages[msg_id]
                else:
                    error_message = "Error: Unauthorized delete attempt."
                    conn.send(cipher.encrypt(error_message.encode('utf-8')))
            else:
                # Store and broadcast the message
                msg_id = len(messages)
                messages[msg_id] = (client_id, message)

                for c in connections:
                    broadcast_message = f"{msg_id} Client {client_id}: {message}"
                    c.send(cipher.encrypt(broadcast_message.encode('utf-8')))

                # Send receipt confirmation to the sender
                confirmation_message = "Message received"
                conn.send(cipher.encrypt(confirmation_message.encode('utf-8')))
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        print(f"[DISCONNECTED] {addr} disconnected.")
        connections.remove(conn)
        del clients[addr]
        conn.close()

def start_server():
    print(f"[STARTING] Server is starting on {HOST}:{PORT}...")
    print(f"[KEY] {key.decode()}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print("[LISTENING] Waiting for connections...")

        while True:
            conn, addr = server_socket.accept()
            print(f"[CONNECTED] {addr} connected.")
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    start_server()
