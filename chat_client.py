"""
Holds client-side logic for after 
logging into the server
"""
import json
import socket
p2p_ip = "127.0.0.1"
p2p_port = 26665
dataSize = 1000000

def get_user_list(client_socket):
	"""Requests user_list from the server"""
	request_data = {
		"type":"USER_LIST"
	}
	encoded_request = request_data.encode()
	client_socket.send(encoded_request)

	server_response = client_socket.recv(dataSize)
	if server_response["type"] != "USER_LIST":
		print("Client expected USER_LIST, got:{}".format(server_response["type"]))
		return None

	if len(server_response["user_list"]) > 0:
		user_list = server_response["user_list"].split(',')
		
	return user_list

def await_connection(server_socket):
	"""Allows the current client to await another's connection"""
	# First tell server we're waiting
	data = {
		"type":"AWAIT"
	}
	data_string = json.dumps(data)
	encoded_data = data_string.encode()
	server_socket.send(encoded_data)
	# Set up Listening socket
	# Create a TCP socket.
	await_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Assign server IP address and port number to socket
	await_socket.bind((p2p_ip, p2p_port))

	# Listen for incoming connection requests
	await_socket.listen(1)
	# Accept connection automatically
	peer_socket, peer_address = await_socket.accept()

	# Tell server we good
	data = {"type":"P2P_CONFIRM", "peer":peer_address}
	encoded_data = json.dumps(data).encode()
	server_socket.send(encoded_data)

	# Establish encrypted chat with other client
	print("Engaging in chat with client: {}".format(peer_address))
	encrypt_chat()

def encrypt_chat():
	"""
	Generates Public/Private Keys
	Establishes an encrypted chat with the peer
	Manages chat UI with the peer
	TODO: one way?
	"""
	# Generate Public/Private Keys
	# Transfer Keys


def main_user_list(client_socket):
	"""Handles the user UI for user_list"""
	user_list = get_user_list(client_socket)
	print("Client got a user list: {}".format(user_list))
	if len(user_list) == 0:
		print("No users online, so we'll wait for an incoming connection...")
	else:
		print("==Connected Users==")
		for user in user_list:
			print(user)
		print("type a user name or type \"wait\"")