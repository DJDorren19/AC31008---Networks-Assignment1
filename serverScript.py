
import socket
import os
from _thread import *
import threading

PORT = 6667
HOST = '::1'
numberOfClients = 3 #numbers of clients allowed to connect


#decalres the socket and server address
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

#Creates a new channel if does not exists, otherwise moves player to channel
def manageChannels(newName, topic):
	
	inList = False
	
	if channelList:
		for items in channelList:
			if newName == items.name:
				inList = True
		if inList:
			#move player to specified channel
			print("Moving player")
				
		else:
			newChannel = Channel(newName, topic)
			channelList.append(newChannel)
			print("Creating a new channel")
	else:
		newChannel = Channel(newName, topic)
		channelList.append(newChannel)
		print("Creating a new channel")
		
#-----------------------------------------------------------------------------------------

#Version of python I am using (3.8) does not allow for switch statments so here we are.
#And not sure if 3.10 is "allowed" for this assignment.
def checkCommands(command):
	if command[0] == "b'JOIN":
		manageChannels(command[1], "No Topic Yet")
	else:
		print("Nothing, temp holder")
	
		#-----------------------------------------------------------------------------------------

lockThread = threading.Lock() #Used to lock the thread

#This function deals with whatever the client does
def newClient(conn):
	while True:
		data = conn.recv(1024)
		
		print(str(data))
		
		#Controls user commands
		command = str(data).split(" ")
		checkCommands(command)
		
		#If no data being send then the thread in unlocked and connection closed.
		if not data:	
			lockThread.release()		
			break
		conn.sendall(data)
		
	conn.close()


#waits for someone/thing to connect
while True:
	print('Waiting for a connection')
	connection, client_address = sock.accept() #connection occured
	
	print('Connection from', client_address)
	
	#locks the and then starts a new thread
	lockThread.acquire() 
	start_new_thread(newClient, (connection,))

sock.close() #closes the socket



#-----------------------------------------------------------------------------------------




			

	
	
	
	
	
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
