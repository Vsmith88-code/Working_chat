import socket
import threading
from cryptography.fernet import Fernet

HOST = '127.0.0.1'
PORT = 65432

# Enter the server encryption key
key = input("Enter the server key: ").encode()
cipher = Fernet(key)

messages = {}  # Dictionary to store received messages


def receive_messages(sock):
    while True:
        try:
            encrypted_message = sock.recv(1024)
            if not encrypted_message:
                print("Disconnected from server.")
                break

            # Decrypt the message
            try:
                message = cipher.decrypt(encrypted_message).decode()
            except Exception as e:
                print(f"[ERROR] Decryption failed: {e}")
                continue

            if message.startswith("DELETE"):
                # Handle delete message
                _, msg_id = message.split()
                if msg_id in messages:
                    messages[msg_id] = "[Deleted]"
            elif message.startswith("[READ RECEIPT]"):
                print(f"[READ RECEIPT] {message[14:]}")
            else:
                # Store and display the message
                if message.startswith("[MESSAGE]"):
                    _, msg_id, msg_content = message.split(" ", 2)
                else:
                    msg_id, msg_content = message.split(" ", 1)
                messages[msg_id] = msg_content
                print(f"{msg_id}: {msg_content}")

            # Display all messages
            print("\nCurrent messages:")
            for msg_id, msg_content in messages.items():
                print(f"{msg_id}: {msg_content}")
        except Exception as e:
            print(f"[ERROR] {e}")
            break


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print("Connected to the server.")

        # Start a thread to handle incoming messages
        threading.Thread(target=receive_messages, args=(sock,)).start()

        while True:
            try:
                message = input("Enter message (or 'DELETE <ID>'): ")
                # Encrypt the message before sending
                if message.startswith("DELETE"):
                    sock.send(cipher.encrypt(message.encode('utf-8')))
                else:
                    # Send the main message
                    encrypted_message = cipher.encrypt(message.encode('utf-8'))
                    sock.send(encrypted_message)

                    # Send a read receipt request
                    read_receipt_request = f"[MESSAGE] {len(messages)} {message}"
                    encrypted_receipt_request = cipher.encrypt(read_receipt_request.encode('utf-8'))
                    sock.send(encrypted_receipt_request)
            except Exception as e:
                print(f"[ERROR] {e}")
                break


if __name__ == "__main__":
    main()
