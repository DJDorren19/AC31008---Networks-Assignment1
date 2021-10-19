
import socket
import os
from _thread import *
import threading

PORT = 6667
HOST = '::1'
numberOfClients = 3 #numbers of clients allowed to connect
channelList = [] #Stores all the channels


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
	def __init__(self, nick):
		self.nick = nick
		self.connectedChannels = []

#-----------------------------------------------------------------------------------------

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

#Creates the user based on the command and assigns them to the default channel
def createUser(nick):
	newClient = Clients(nick)
	
#-----------------------------------------------------------------------------------------

#Version of python I am using (3.8) does not allow for switch statments so here we are.
def checkCommands(command):
	
	#for the number of lines in list
	for lines in command:

		#Splits up all the lines to be readable
		sentLine = lines.split(" ")
		tempCommand = sentLine[0]

		if tempCommand == "JOIN":
			manageChannels(command[1], "No Topic Yet") #creates a new channel
		elif tempCommand == "NICK":
			createUser(sentLine[1]) #Creates a new user
	else:
		pass
	
#-----------------------------------------------------------------------------------------

lockThread = threading.Lock() #Used to lock the thread

#This function deals with whatever the client does
def newClient(conn):
	while True:
		data = conn.recv(1024)
		
		#print(str(data)) #prints raw data
		
		#Decodes the data to make it more readable
		msg = data.decode("utf-8")

		#Splits it by line and checks if command
		line = msg.split("\r\n")
		checkCommands(line)

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
	
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
