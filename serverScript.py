
import socket

PORT = 6667
HOST = '::1'
numberOfClients = 3 #numbers of clients allowed to connect

#Creates a socket
sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

server_adderess = (HOST, PORT)
print('Starting up on', HOST , 'PORT', PORT)

#Allows to reuse the socket. Big POG and binds scoket to port.
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(server_adderess)

#Allows for an x number of clients
sock.listen(numberOfClients)


#-----------------------------------------------------------------------------------------

#Class to hold all of the channel details
class Channel:
	
	#Sets up the object
	def __init__(self, name, topic):
		self.name = name
		self.clientList = [] #List to hold clients 
		self.topic = topic
		

#-----------------------------------------------------------------------------------------

#Class to hold all of the client details
class Clients:
	
	#Sets up the object
	def __init__(self, username, host):
		self.username = username
		self.host = host
		
#-----------------------------------------------------------------------------------------

channelList = [] #Stores all the channels

#Creates a new channel and then stores it in a list
def createChannel(name, topic):
	newChannel = Channel(name, topic)
	channelList.append(newChannel)

#-----------------------------------------------------------------------------------------

#Will wait for someone/thing to connect
while True:
	print('Waiting for a connection')
	connection, client_address = sock.accept()
	
	try:
		print('Connection from', client_address)
		
		
		########################TEST CODE FOR CHANNEL########################
		
		newClient = Clients("Daniel", client_address)
		
		createChannel("#test", "Bababooey")
		
		channelList[0].clientList.append(newClient)
		
		print("Channel: ", channelList[0].name)
		
		for i in channelList[0].clientList:
			print("User: ", i.username, "Host: ", i.host)
		
		######################################################################
	
		

		#Gets the data and prints it.
		while True:
			data = connection.recv(1024)
			
			print(str(data))
			if not data:
				break
			connection.sendall(data)
					
	#Closes the connection
	finally:
		print("Closing current connection")
		connection.close()

#-----------------------------------------------------------------------------------------




      		

			
	
	
	
	
	
	
	
	
	
	
	
	
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
