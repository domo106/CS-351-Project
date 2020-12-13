"""Login Server, allows clients to connect and log in."""
import socket
import login_functions
import json
import _thread
import encoding

# Read server IP address and port from command-line arguments
serverIP = "127.0.0.1"
serverPort = 25575
dataSize = 1000000

OK = "OK"
ERROR = "ERROR"
ERROR_LOGIN = "ERROR_LOGIN"

open_connections = {}
# client_address:"username" when authenticated

wait_list = {}
# username:address

# Create a TCP socket.
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Assign server IP address and port number to socket
serverSocket.bind((serverIP, serverPort))

# Listen for incoming connection requests
serverSocket.listen(1)

print("The server is ready to receive on port:  " + str(serverPort) + "\n")

def connect_client(connectionSocket, client_address):
    while True:
        # Receive client request, unpack data
        data = connectionSocket.recv(dataSize)
        print("Data fetched")

        # data, client_address = serverSocket.recvfrom(1000) # Max space to receive each packet
        client_ip, client_port = client_address
        client_json_str = data.decode()
        print("Received JSON: {}".format(client_json_str))
        client_data = json.loads(client_json_str)
        print("Received data from client {}, {}: {}".format(client_ip, client_port, client_data))

        interaction_type = client_data["type"]
        response_data = {"type":interaction_type, "status":""}
        if interaction_type == "REGISTER":
            # Register
            username = client_data["username"]
            password = client_data["password"]
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
            username = client_data["username"]
            password = client_data["password"]
            error = login_functions.login_user(username, password)
            if error == OK:
                # Add to open connections
                open_connections[client_address] = username
                # OK Response
                response_data["status"] = "OK"
            else:
                # Error response
                response_data["status"] = "ERROR"
        elif interaction_type == "USER_LIST":
            # Provide list of connected users.
            print("Someone needs a USER_LIST")
            user_list = open_connections.values()
            response_data["status"] = "OK"
            response_list = ""
            if client_address in open_connections:
                print("Client is authenticated, good!")
                this_username = open_connections[client_address]
                for user in user_list:
                    if user != this_username:
                        response_list += "{},".format(user)
                response_list = response_list.strip(',')
                response_data["user_list"] = response_list
            else:
                print("Client is not authenticated correctly.")
                print("Client {} is not in {}".format(client_address, open_connections))
                response_data["status"] = "ERROR"
        elif interaction_type == "AWAIT":
            print("Client wants to await a connection")
            if client_address in open_connections:
                print("Client is authenticated, good!")
                this_username = open_connections[client_address]
                if this_username in wait_list:
                    print("Error, user's already awaiting.")
                    response_data["status"] = "ERROR"
                else:
                    wait_list[this_username] = client_address
                    response_data["status"] = "OK"
        elif interaction_type == "GET_ADDRESS":
            print("Fetching an address")
            user_requested = client_data["user_name"]
            peer_address = wait_list[user_requested]
            response_data["user_address"] = peer_address
            response_data["status"] = "OK"
        elif interaction_type == "P2P_CONFIRM":
            print("Got a connection confirmation")
            client_name = open_connections[client_address]
            print("Client A is {} with name {}".format(client_address, client_name))
            b_address_list = client_data["peer"]
            b_address = (b_address_list[0], b_address_list[1])
            b_name = open_connections[b_address]
            print("Client B is {} with name {}".format(b_address, b_name))
            del open_connections[client_address]
            del wait_list[client_name]
            print("{} removed from wait_list".format(client_name))
            response_data["status"] = "OK"
            response_data["peer_name"] = client_data[b_name]
        else:
            print("Received unexpected type: {}".format(interaction_type))
            response_data["status"] = "ERROR"

        if "status" not in response_data:
            response_data["status"] = "OK"

        # Pack server response
        response_json = json.dumps(response_data)
        response_data = response_json.encode()

        # Send back
        print("Sending data to client {}: {}".format(client_address, response_json))
        connectionSocket.send(response_data)

# Wait for message from client
while True:
    # Establish TCP Connection
    connectionSocket, client_address = serverSocket.accept()
    print("Connection established")
    _thread.start_new_thread(connect_client,(connectionSocket, client_address))


