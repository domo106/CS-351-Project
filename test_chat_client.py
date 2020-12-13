import json
import socket
import time


server_ip = "127.0.0.1"
server_port = 25575

# Open socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Establish TCP Connection
client_socket.connect((server_ip, server_port))
message_data = {"message":"I like potatoes"}
message_encoded = json.dumps(message_data).encode()

client_socket.send(message_encoded)

time.sleep(10)

message_data = {"message":"I like potatoes"}
message_encoded = json.dumps(message_data).encode()

client_socket.send(message_encoded)
