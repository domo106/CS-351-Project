"""Login Server, allows clients to connect and log in."""
import sys
import socket

# Read server IP address and port from command-line arguments
serverIP = "127.0.0.1"
serverPort = 25565

if len(sys.argv) > 1:
	serverIP = sys.argv[1]
	serverPort = int(sys.argv[2])

# Create a UDP socket. Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
## Same settings as in client.py

# Assign server IP address and port number to socket
serverSocket.bind((serverIP, serverPort))
# 127.0.0.1 (Loopback address)
# Port: 12000 (arbitrary)


print("The server is ready to receive on port:  " + str(serverPort) + "\n")

# Wait for message from client
while True:
    # Receive and print the client data from "data" socket
    data, client_address = serverSocket.recvfrom(100) # Max space to receive each packet
    client_IP, client_Port = client_address
    client_message = data.decode()
    print("Receive data from client {}, {}: {}".format(client_IP, client_Port, client_message))

    # Echo back to client
    
    print("Sending data to client {}, {}: {}".format(client_IP, client_Port, client_message))
    serverSocket.sendto(data, client_address)
