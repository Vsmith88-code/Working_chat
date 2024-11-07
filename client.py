import socket
import threading

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

def receive_messages(sock):
    """Thread to receive messages from the server."""
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if message:
                print(message)
        except:
            print("Disconnected from server.")
            break

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print("Connected to the server.")

        # Start a thread to receive messages
        threading.Thread(target=receive_messages, args=(sock,)).start()

        while True:
            message = input("Enter message: ")
            sock.send(message.encode('utf-8'))

if __name__ == "__main__":
    main()
