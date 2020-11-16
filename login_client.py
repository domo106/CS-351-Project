"""Login Client"""
import sys
import socket

server_IP = 127.0.0.1
server_port = 25565
count = 5
data = 'X' * count

if len(argv) > 1:
	server_IP = sys.argv[1] 
	server_port = int(sys.argv[2]) 
	count = int(sys.argv[3]) 
	data = 'X' * count 

# Create UDP client socket. Note the use of SOCK_DGRAM
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
## AF_NET - Address Family Internet (IPv4)
## SOCK_DGRAM - Socket Datagram (UDP by default)
## SOCK_STREAM - Socket Stream - TCP
## These must be same on both sides

# 3. Timeout in 1 second
clientsocket.settimeout(1.0)

for i in range(3): # 4. Iterate 3 times
	# Send data to server
	# 5. Print IP, Port, and Message when sending	
	print("Sending data to   " + host + ", " + str(port) + ": " + data + " (" + str(count) + " characters)")
	clientsocket.sendto(data.encode(), (host, port))
	# data.encode() encodes the data from string to bytecode

	try:
		# Receive the server response
		dataEcho, address = clientsocket.recvfrom(count)
		# 6. Print IP, Port, and Message when receiving
		print("Receive data from " + address[0] + ", " + str(address[1]) + ": " + dataEcho.decode())
		break
	except ConnectionResetError:
		print("Server not Responding")
		# Break here if you only want to attempt once on no server response
	except socket.timeout:
		print("Message Timed Out")
	except:
		print("Unknown Error")

	

# Close the client socket
clientsocket.close()
