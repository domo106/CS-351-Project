"""
Holds client-side logic for after 
logging into the server
"""
import json
import socket
from encoding import json_decode, json_encode
import encoding
import threading
from Crypto.PublicKey import RSA
import time

p2p_ip = "127.0.0.1"
p2p_port = 26665
dataSize = 1000000

def get_user_list(server_socket):
	"""Requests user_list from the server"""
	print("Getting user_list")
	request_data = {
		"type":"USER_LIST"
	}

	encoded_request = json_encode(request_data)
	server_socket.send(encoded_request)
	print("Now we wait...")
	server_response = server_socket.recv(dataSize)
	print("Got response!")
	response_data = json_decode(server_response)
	if response_data["type"] != "USER_LIST":
		print("Client expected USER_LIST, got:{}".format(response_data["type"]))
		return None
	print("Got userlist from server: {}".format(response_data["user_list"]))
	if len(response_data["user_list"]) > 0:
		user_list = response_data["user_list"].split(',')
		return user_list
	else:
		user_list = {}
		return user_list


def await_connection(server_socket, user_name):
	"""
	Allows the current client to await another's connection
	In the context of my notes:
	this is Client A
	Peer is Client B
	"""
	# First tell server we're waiting
	print("Awaiting incoming connection...")
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
	print("Connection with B Accepted")

	# Await B's name
	name_data = peer_socket.recv(dataSize)
	name_dict = json_decode(name_data)
	print("B Name Dict:", name_dict)
	b_name = name_dict["peer_name"]

	#Await/Accept Public key of B
	b_public_string = peer_socket.recv(dataSize)

	# Generate Keys as encoded strings
	a_private_string, a_public_string,  a_session_string = encoding.generate_keys()

	# Send Public.A -> B
	peer_socket.send(a_public_string)

	# Establish encrypted chat with other client
	print("Engaging in chat with client: {}".format(peer_address))
	keys = {
		"my_private_key": RSA.import_key(a_private_string),
		"peer_public_key": RSA.import_key(b_public_string),
		"my_session_key": a_session_string,
	}
	# print("A has private key:",keys["my_private_key"])
	encrypt_chat(peer_socket, keys, b_name, user_name)

def establish_connection(server_socket, peer_address, peer_name, user_name):
	"""
	Open a socket with a waiting peer
	The peer calling this is B ~ client
	waiting peer is noted as A ~ server
	"""
	# Create a TCP socket with A
	peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	peer_ip = peer_address[0]
	peer_socket.connect((peer_ip, p2p_port))

	# B.confirm(A) -> Server
	# Confirm connection with Server
	data = {"type": "P2P_CONFIRM", "peer_name": peer_name, "my_name":user_name}
	encoded_data = json.dumps(data).encode()
	server_socket.send(encoded_data)

	# Send B's name to A
	data = {"type": "NAME", "peer_name": user_name}
	encoded_data = json.dumps(data).encode()
	peer_socket.send(encoded_data)

	# Generate Keys as encoded strings
	b_private_string, b_public_string,  b_session_string = encoding.generate_keys()

	# Give A Public.B
	peer_socket.send(b_public_string)

	# Get Public.A
	a_public_string = peer_socket.recv(dataSize)
	#a_key_dict = json_decode(a_key_data)
	#a_public_key = a_key_dict["public_key"]
	keys = {
		"my_private_key": RSA.import_key(b_private_string),
		"peer_public_key": RSA.import_key(a_public_string),
		"my_session_key": b_session_string,
	}
	#print("B has private key:", keys["my_private_key"])

	# Confirm with server
	# This is basically optional for 2 clients
	# Message
	#encrypt_chat(peer_socket, keys)
	encrypt_chat(peer_socket, keys, peer_name, user_name)



def encrypt_chat(peer_socket, keys, peer_name, user_name):
	"""
	Generates Public/Private Keys
	Establishes an encrypted chat with the peer
	Manages chat UI with the peer
	"""

	class ChatInput(threading.Thread):
		def run(self):
			while True:
				# Receive Encoded
				byte_types = ['ciphertext', 'encrypted_session_key', 'nonce', 'tag']
				peer_message_dict = {}
				for key in byte_types:
					thing = peer_socket.recv(dataSize)
					peer_message_dict[key] = thing
					print(key, len(key))

				# JSON to text
				message = encoding.decrypt_message(peer_message_dict, keys)
				print("{}:{}".format(peer_name, message))

	# Handle incoming messages
	input_handler = ChatInput()
	input_handler.daemon = True
	input_handler.start()

	print("We are now chatting securely.")
	try:
		while True:
			byte_types = ['ciphertext', 'encrypted_session_key', 'nonce', 'tag']
			local_message = input("{}:".format(user_name))
			# Text to JSON
			message_dict = encoding.encrypt_message(local_message, keys)
			for key in message_dict:
				print(key, len(key))
			# Send all JSON values
			for key in byte_types:
				peer_socket.send(message_dict[key])
				time.sleep(0.1)
			# JSON to encoded
			#encoded_message = json_encode(message_dict)
			#peer_socket.send(encoded_message)


	except KeyboardInterrupt:
		print("Exiting chat...")
		return None


def main_user_list(server_socket, user_name):
	"""Handles the user UI for user_list"""
	user_list = get_user_list(server_socket)
	print("Client got a user list: {}".format(user_list))
	if len(user_list) == 0:
		print("No users online, so we'll wait for an incoming connection...")
		await_connection(server_socket, user_name)
	else:
		print("==Connected Users==")
		for user in user_list:
			print(user)
		print("type a user name or type \"wait\"")
		peer_name = input(">")
		if peer_name == "wait":
			await_connection(server_socket, user_name)
		elif peer_name in user_list:
			# Ask server for user_name
			request_data = {"type":"GET_ADDRESS", "user_name":peer_name}
			encoded_request = json_encode(request_data)
			print("Sending Request for A's Address: {}".format(request_data))
			server_socket.send(encoded_request)

			encoded_response = server_socket.recv(dataSize)
			response_dict = json_decode(encoded_response)
			print("Got A's Address: {}".format(response_dict))
			# user_address is turned into a list, convert back to tuple
			peer_ip, peer_port = response_dict["user_address"]
			peer_address = (peer_ip, peer_port)
			# Establish connection with peer
			establish_connection(server_socket, peer_address, peer_name, user_name)
		else:
			print("User {} was not in the userlist.".format(peer_name))
