
import socket

PORT = 6667
HOST = '::1'
numberOfClients = 3 #numbers of clients allowed to connect

#Creates a socket
sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)



server_adderess = (HOST, PORT)
print('Starting up on {} port {}'.format(*server_adderess))

#Allows to reuse the socket. Big POG.
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#Binds the created socket to the port
sock.bind(server_adderess)

#Allows for 2 clients
sock.listen(numberOfClients)


#Will wait for someone/thing to connect
while True:
	print('Waiting for a connection')
	connection, client_address = sock.accept()
	
	try:
		print('Connection from', client_address)
		
		#Gets the data and prints it.
		while True:
			data = connection.recv(1024)
			if not data:
				break
			connection.sendall(data)
			
				
	#Closes the connection
	finally:
		print("Closing current connection")
		connection.close()




###THIS IS ME TRYING TO FIGURE OUT HOW CHANNELS AND WHAT NOT WORKS...###

#Class to hold all of the channel details
class Channel:
	def __init__(self, name, topic='No Topic'):
		self.name = name
		self.topic = topic
		self.clients = Set["Clients"] = set()

class Client:
	def __init__(self, request, client_adress, server):
		self.user = None
		self.host = client_address
		self.nick
		self.send_queue = []
		self.channels = {}
		
		
	def joinChannel():
		channel = self.server.Channels.setdefault(r_channel_name, channel(r_channel_name)
		channel.clients.add(self)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
