import socket
import threading

HOST = '127.0.0.1'  # Localhost
PORT = 65432        # Port to listen on
connections = []    # List to hold connected clients

def handle_client(conn, client_id):
    """Handles messages from each client and forwards them to the other."""
    try:
        while True:
            message = conn.recv(1024).decode('utf-8')
            if message:
                print(f"Client {client_id}: {message}")
                # Send the message to the other client
                recipient_id = 1 if client_id == 0 else 0
                if len(connections) > recipient_id:
                    connections[recipient_id].send(f"Client {client_id}: {message}".encode('utf-8'))
            else:
                break
    except:
        pass
    finally:
        connections.remove(conn)
        conn.close()

def main():
    # Set up and run the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(2)
        print("Server is listening for connections...")

        while len(connections) < 2:
            conn, addr = server_socket.accept()
            print(f"Client connected from {addr}")
            connections.append(conn)
            client_id = len(connections) - 1
            threading.Thread(target=handle_client, args=(conn, client_id)).start()

if __name__ == "__main__":
    main()
