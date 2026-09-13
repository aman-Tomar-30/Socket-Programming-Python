import socket
import threading

HOST = "127.0.0.1"
PORT = 5000


def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode()

            if not message:
                break

            print("\n" + message)
            print("> ", end="", flush=True)

        except:
            print("\nDisconnected from server.")
            break


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))

nickname = input("Enter your name: ")

# Send nickname to server
client.send(nickname.encode())

# Thread for receiving messages
receive_thread = threading.Thread(
    target=receive_messages,
    daemon=True
)

receive_thread.start()

print("Connected to chat!")
print("Type your messages below.")
print("Type /quit to leave.\n")

while True:
    message = input("> ")

    if message.lower() == "/quit":
        client.close()
        break

    if message.strip():
        client.send(message.encode())
