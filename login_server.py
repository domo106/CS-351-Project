"""Login Server, allows clients to connect and log in."""
import sys
import socket
import login_functions
import json

# Read server IP address and port from command-line arguments
serverIP = "127.0.0.1"
serverPort = 25575
dataSize = 1000000

OK = "OK"
ERROR = "ERROR"
ERROR_LOGIN = "ERROR_LOGIN"

open_connections = {}
# client_address:"username" when authenticated

# Create a TCP socket.
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Assign server IP address and port number to socket
serverSocket.bind((serverIP, serverPort))

# Listen for incoming connection requests
serverSocket.listen(1)

print("The server is ready to receive on port:  " + str(serverPort) + "\n")

# Wait for message from client
while True:
    # Establish TCP Connection
    connectionSocket, client_address = serverSocket.accept()
    print("Connection established")

    # Receive client request, unpack data
    data = connectionSocket.recv(dataSize)
    print("Data fetched")

    # data, client_address = serverSocket.recvfrom(1000) # Max space to receive each packet
    client_IP, client_Port = client_address
    client_json_str = data.decode()
    client_data = json.loads(client_json_str)
    print("Received data from client {}, {}: {}".format(client_IP, client_Port, client_data))

    interaction_type = client_data["type"]
    username = client_data["username"]
    password = client_data["password"]
    response_data = {"type":interaction_type, "status":""}
    if interaction_type == "REGISTER":
        # Register
        error = login_functions.register_user(username, password)
        if error == OK:
            # Add to open connections
            open_connections[client_address] = username
            # Respond with register successful
            response_data["status"] = "OK"
        else:
            # Respond with an error status
            print("register threw an error")
            response_data["status"] = "ERROR"
    elif interaction_type == "LOGIN":
        # Login
        error = login_functions.login_user(username, password)
        if error == OK:
            # Add to open connections
            # OK Response
            response_data["status"] = "OK"
        else:
            # Error response
            response_data["status"] = "ERROR"
    elif interaction_type == "USER_LIST":
        # Provide list of connected users.
        user_list = open_connections.values()
        response_data["status"] = "OK"
        response_list = ""
        this_username = open_connections[client_address]
        for user in user_list:
            if user != this_username:
                response_list += "{},".format(user)
        response_list = response_list.strip(',')
        response_data["user_list"] = response_list
    else:
        print("Received unexpected type: {}".format(interaction_type))
        response_data["status"] = "ERROR"
    
    # Pack server response
    response_json = json.dumps(response_data)
    response_data = response_json.encode()

    # Send back
    print("Sending data to client {}: {}".format(client_address, response_json))
    connectionSocket.send(response_data)
