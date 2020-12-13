"""Login Client"""
import sys
import socket
import json
import chat_client
import time


OK = "OK"
ERROR = "ERROR"
ERROR_LOGIN = "ERROR_LOGIN"

def main():
    server_ip = "127.0.0.1"
    server_port = 25575
    data_size = 1000000
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
        server_port = int(sys.argv[2])
    server_address = (server_ip, server_port)

    # Open socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Establish TCP Connection
    client_socket.connect(server_address)

    # Here we should check server DS

    # Determine what we'll send
    interaction = enter_type()
    credentials = enter_credentials()
    user_choices = {
        "type":interaction,
        "username":credentials["username"],
        "password":credentials["password"]
    }
    #print("Got choices {}".format(user_choices))
    data_string = json.dumps(user_choices)
    encoded_data = data_string.encode()

    # Send data to server
    #print("Sending data to {}: {}".format(server_address, encoded_data))
    client_socket.send(encoded_data)
    response_data = {}

    # Receive the server response

    try:
        #print("Awaiting response")
        response = client_socket.recv(data_size)
        #print(response)
        response_string = response.decode()
        response_data = json.loads(response_string)
        # 6. Print IP, Port, and Message when receiving
        print("Received data: {}".format(response_data))
    except ConnectionResetError:
        print("Server not Responding")
        # Break here if you only want to attempt once on no server response
    except socket.timeout:
        print("Message Timed Out")
    except:
        print("Unexpected error:", sys.exc_info()[0])
        print("Response Data:{}".format(response_data))

    status = response_data["status"]
    response_type = response_data["type"]
    if status == "OK":
        print("We're good")
    elif status == "ERROR":
        print("Invalid username or password")
        client_socket.close()
        return
    else:
        print("We don't know if we're good, but probably not.")
        client_socket.close()
        return

    # Starting chat client...
    time.sleep(1)
    print("Starting chat client..")
    chat_client.main_user_list(client_socket, credentials["username"])
    # finished with chat client
    print("Chat client closed, disconnecting...")
    client_socket.close()
    # print("Nothing to do when logged in, so closing connection...")


def enter_type():
    """
    Asks user if login/register
    Then asks for User/pass
    returns "LOGIN" or "REGISTER"
    """
    # Ask Login/Register
    choice = ""
    valid_choices = ["login","register","l","r"]
    while choice not in valid_choices:
        choice = input("Would you like to login or register? (l/r)")

    if choice[0].lower() == 'l':
        return "LOGIN"
    else:
        return "REGISTER"

def enter_credentials():
    """Asks user for credentials"""
    credentials = {}
    username = password = ""
    while username == "" or password == "":
        username = input("Enter a username:")
        password = input("Enter a password:")
        print("Got username:{} and password:{}".format(username,password))
    credentials["username"] = username
    credentials["password"] = password

    return credentials

if __name__ == "__main__":
    main()