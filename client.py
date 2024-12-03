import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

messages = {}  # Dictionary to store received messages

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if message.startswith("DELETE"):
                _, msg_id = message.split()
                if msg_id in messages:
                    messages[msg_id] = "[Deleted]"
            else:
                msg_id, msg_content = message.split(" ", 1)
                messages[msg_id] = msg_content

            for msg_id, msg_content in messages.items():
                print(f"{msg_id}: {msg_content}")
        except:
            print("Disconnected from server.")
            break


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print("Connected to the server.")

        threading.Thread(target=receive_messages, args=(sock,)).start()

        while True:
            message = input("Enter message (or 'DELETE <ID>'): ")
            sock.send(message.encode('utf-8'))

if __name__ == "__main__":
    main()
