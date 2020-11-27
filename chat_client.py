"""
Holds client-side logic for after 
logging into the server
"""
import json
import socket
from encoding import json_decode, json_encode
import encoding
p2p_ip = "127.0.0.1"
p2p_port = 26665
dataSize = 1000000

def get_user_list(server_socket):
	"""Requests user_list from the server"""
	request_data = {
		"type":"USER_LIST"
	}

	encoded_request = json_encode(request_data)
	server_socket.send(encoded_request)

	server_response = server_socket.recv(dataSize)
	response_data = json_decode(server_response)
	if response_data["type"] != "USER_LIST":
		print("Client expected USER_LIST, got:{}".format(response_data["type"]))
		return None

	if len(response_data["user_list"]) > 0:
		user_list = response_data["user_list"].split(',')
		
	return user_list

def await_connection(server_socket):
	"""Allows the current client to await another's connection"""
	# First tell server we're waiting
	data = {
		"type":"AWAIT"
	}
	encoded_data = json_encode(data)
	server_socket.send(encoded_data)
	# Set up Listening socket
	# Create a TCP socket.
	await_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Assign server IP address and port number to socket
	await_socket.bind((p2p_ip, p2p_port))

	# Listen for incoming connection requests
	await_socket.listen(1)

	# Accept B
	peer_socket, peer_address = await_socket.accept()

	# Await/Accept Public key of B
	b_key_data = peer_socket.recv(dataSize)
	b_key_dict = json_decode(b_key_data)
	b_public_key = b_key_dict["public_key"]

	# Send Public Key of A
	my_public_key, my_private_key = encoding.generate_keys()
	key_dict = {"public_key":my_public_key}
	encoded_key = json_encode(key_dict)
	peer_socket.send(encoded_key)

	# Confirm connection with Server
	data = {"type":"P2P_CONFIRM", "peer":peer_address}
	encoded_data = json.dumps(data).encode()
	server_socket.send(encoded_data)

	# Establish encrypted chat with other client
	print("Engaging in chat with client: {}".format(peer_address))
	keys = {"my_private_key":my_private_key,"peer_public_key":b_public_key}
	encrypt_chat(peer_socket, keys)

def establish_connection(server_socket, peer_address):
	"""
	Open a socket with a waiting peer
	waiting peer is noted as A, this peer is B
	"""
	# Create a TCP socket with A
	peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	peer_socket.bind(peer_address)
	# Generate Keys
	b_public_key, b_private_key = encoding.generate_keys()

	# Give A Public.B
	b_key_data = {"type":"key", "public_key":b_public_key}
	peer_socket.send(b_key_data)

	# Get Public.A
	a_key_data = peer_socket.recv(dataSize)
	a_key_dict = json_decode(a_key_data)
	a_public_key = a_key_dict["public_key"]

	keys = {"my_private_key":b_private_key, "peer_public_key":a_public_key}
	# Message
	encrypt_chat(peer_socket, keys)

def encrypt_chat(peer_socket, keys):
	"""
	Generates Public/Private Keys
	Establishes an encrypted chat with the peer
	Manages chat UI with the peer
	"""
	print("We are now chatting securely.")

def main_user_list(server_socket):
	"""Handles the user UI for user_list"""
	user_list = get_user_list(server_socket)
	print("Client got a user list: {}".format(user_list))
	if len(user_list) == 0:
		print("No users online, so we'll wait for an incoming connection...")
		await_connection(server_socket)
	else:
		print("==Connected Users==")
		for user in user_list:
			print(user)
		print("type a user name or type \"wait\"")
		user_name = input(">")
		if user_name == "wait":
			await_connection(server_socket)
		elif user_name in user_list:
			# Ask server for user_name
			request_data = {"type":"get_address", "user_name":user_name}
			encoded_request = json_encode(request_data)
			server_socket.send(encoded_request)

			encoded_response = server_socket.recv(dataSize)
			response_dict = json_decode(encoded_response)
			peer_address = response_dict["user_address"]

			# Establish connection with peer
			establish_connection(server_socket, peer_address)

