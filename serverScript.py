
import socket

PORT = 6667
HOST = '127.0.0.1'

#Creates a socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Binds the created socket to the port
server_adderess = (HOST, PORT)
print('Starting up on {} port {}'.format(*server_adderess))
sock.bind(server_adderess)

#Allows for 2 clients
sock.listen(2)


#Will wait for someone/thing to connect
while True:
	print('Waiting for a connection')
	connection, client_address = sock.accept()
	
	try:
		print('Connection from', client_address)
		
		#Gets the data and prints it.
		while True:
			data = connection.recv(16)
			print('recived {!r}'.format(data))
			if data:
				print('Sending data back to client')
				connection.sendall(data)
			else:
				print('No data from', client_address)
				break
				
	#Closes the connection
	finally:
		print("Closing current connection")
		connection.close()


			
