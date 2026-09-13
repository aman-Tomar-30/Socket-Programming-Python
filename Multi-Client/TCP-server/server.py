import socket
import threading

HOST = "127.0.0.1" #localhost for self testing
PORT = 5000

clients = []
nicknames = []


def broadcast(message):
    """Send a message to every connected client."""
    for client in clients:
        try:
            client.send(message)
        except:
            pass


def handle_client(conn, addr):
    print(f"Client connected: {addr}")

    try:
        nickname = conn.recv(1024).decode()

        clients.append(conn)
        nicknames.append(nickname)

        print(f"{nickname} joined the chat.")

        broadcast(f"{nickname} joined the chat!\n".encode())

        while True:
            data = conn.recv(1024)

            if not data:
                break

            message = f"{nickname}: {data.decode()}"
            print(message)

            broadcast(message.encode())

    except ConnectionResetError:
        pass

    finally:
        if conn in clients:
            index = clients.index(conn)

            clients.remove(conn)
            nickname = nicknames.pop(index)

            print(f"{nickname} disconnected.")

            broadcast(f"{nickname} left the chat.\n".encode())

        conn.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen(10)

print(f"Chat server running on {HOST}:{PORT}")

while True:
    conn, addr = server.accept()

    thread = threading.Thread(
        target=handle_client,
        args=(conn, addr),
        daemon=True
    )

    thread.start()
