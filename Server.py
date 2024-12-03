import socket
import threading

HOST = '127.0.0.1'
PORT = 65432
connections = []
messages = {}  # Store messages with format {msg_id: (client_id, message)}

def handle_client(conn, client_id):
    try:
        while True:
            message = conn.recv(1024).decode('utf-8')
            if message.startswith("DELETE"):
                # Handle delete requests
                _, msg_id = message.split()
                msg_id = int(msg_id)

                if msg_id in messages and messages[msg_id][0] == client_id:
                    for c in connections:
                        c.send(f"DELETE {msg_id}".encode('utf-8'))
                    del messages[msg_id]
                else:
                    conn.send("Error: Unauthorized delete attempt.".encode('utf-8'))
            elif message:
                # Store the message with an ID and broadcast it
                msg_id = len(messages)
                messages[msg_id] = (client_id, message)
                for c in connections:
                    c.send(f"{msg_id} Client {client_id}: {message}".encode('utf-8'))
            else:
                break
    except:
        pass
    finally:
        connections.remove(conn)
        conn.close()

def main():
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
