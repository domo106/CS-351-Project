import socket
import threading
import json
print("Running test chat server")
dataSize = 12000

server_ip = "127.0.0.1"
server_port = 25575

class ChatInput(threading.Thread):
    def run(self):
        while 1:
            message_data = connectionSocket.recv(dataSize)
            data_str = message_data.decode()
            message_dict = json.loads(data_str)
            message = message_dict["message"]
            print("James:{}".format(message))

open_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
open_socket.bind((server_ip, server_port))

# Listen for incoming connection requests
open_socket.listen(1)

connectionSocket, peer_address = open_socket.accept()
print("Connected to client")

# Handle incoming messages
input_handler = ChatInput()
input_handler.daemon = True
input_handler.start()

# Handle outgoing messages
while True:
    local_message = input("Jason:")
#data = connectionSocket.recv(dataSize)
