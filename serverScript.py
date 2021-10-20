
import socket
import os
from _thread import *
import threading
import re


#Map used to store all the error codes
error_Codes = {

	'ERR_NONICKNAMEGIVEN': 431,
	'ERR_NICKNAMEINUSE': 433, 
	'ERR_NICKCOLLISION': 436, 
	'ERR_RESTRICTED': 484


}

#Map used to store all the reply codes
reply_codes = {

	'RPL_WELCOME': 1,

}




#Global lists (Very secure /s)
channelList = [] #Stores all the channels
clientList = [] #Stores all the clients

#-----------------------------------------------------------------------------------------

#Class to hold all of the channel details
class Channel:
	
	#Sets up the object
	def __init__(self, name):
		self.name = name
		self.clientList = [] #List to hold clients 
		self.topic = {}

#-----------------------------------------------------------------------------------------

#Class to hold all of the client details
class Clients:
	
	#Sets up the object
	def __init__(self, nick, clientAddress):
		self.nick = nick
		self.connectedChannels = []
		self.userName = {}
		self.host = clientAddress
		self.server = {}
		self.registered = False

#-----------------------------------------------------------------------------------------

#Everything to do with the server and handling of channels and clients
class Server:
	
	#global variables
	sock = None 
	ircMessagesLength = 512 #Pretty sure this is the max number of characters allowed
	
	#Server constructor
	def __init__(self):

		PORT = 6667
		HOST = '::1'
		numberOfClients = 3 #numbers of clients allowed to connect
		
		#decalres the socket and server address
		self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		server_adderess = (HOST, PORT)
		print('Listening on port:', PORT)

		#Allows to reuse the socket. Big POG and binds scoket to port.
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(server_adderess)

		#Allows for an x number of clients
		self.sock.listen(numberOfClients)

	#-----------------------------------------------------------------------------------------

	#Handles the different errors that could occur when assigning a nick
	def handleNick(self, nick):

		#checks if the nick is already taken
		if clientList:
			for clients in clientList:
				if clients.nick == nick:
					#send error code here for ERR_NICKNAMEINUSE
					pass 
		
		#Checks if the nick name is too long
		if len(nick) > 9:
			#send the ERR_ERRONEUSNICKNAME here
			pass 
		
		#Checks if nick is empty
		if not nick:
			#send the ERR_NONICKNAMEGIVEN here
			pass

	#-----------------------------------------------------------------------------------------


	#Deals with the changing of nick
	def changeNick(self, nick, clientAddress):

		nickChanged = False #keeps track if nick changed

		#checks if the client is already registered
		for clients in clientList:
			if clients.host == clientAddress:
				clients.nick = nick # if they are then nick changed
				nickChanged = True


		##############################################
		#I THINK THERE SHOULD BE A RPL/ERR HERE TOO??
		##############################################


		#whether or not the nick has been changed
		return nickChanged

	#-----------------------------------------------------------------------------------------

	#Simple function to just create user and add them to the list of clients on server
	def createClient(self, nick, clientAddress):
		
		#deals with any circumstances regarding the nick
		self.handleNick(nick)

		#creates a new client object and adds it to client list
		if not self.changeNick(nick, clientAddress):
			self.clientNew = Clients(nick, clientAddress)
			clientList.append(self.clientNew)

	#-----------------------------------------------------------------------------------------

	#Creates a new channel if does not exists, otherwise moves player to channel
	def manageChannels(self, newName):
		
		inList = False #used to see if channel already exists

		if channelList:
			#checks if channel already exists
			for items in channelList:
				if newName == items.name:
					inList = True
			if inList:
				#move player to specified channel
				print("Moving player")	
			else:
				newChannel = Channel(newName)
				channelList.append(newChannel)
				print("Creating a new channel")
		else:
			newChannel = Channel(newName)
			channelList.append(newChannel)
			print("Creating a new channel")

	#-----------------------------------------------------------------------------------------

	#Changes the username of the client
	def editUsername(self, username, clientAdderss):
		for clients in clientList:
			if clients.host == clientAdderss:
				clients.userName = username

	#-----------------------------------------------------------------------------------------

	#Version of python I am using (3.8) does not allow for switch statments so here we are.
	def checkCommands(self, command, clientAddress):
		
		#for the number of lines in list
		for lines in command:

			#Splits up all the lines to be readable
			sentLine = lines.split(" ")
			tempCommand = sentLine[0]

			if tempCommand == "JOIN":
				self.manageChannels(sentLine[1]) #creates a new channel
			elif tempCommand == "NICK":
				self.createClient(sentLine[1], clientAddress) #Creates a new user
			elif tempCommand == "USER":
				self.editUsername(sentLine[1], clientAddress) #Changes the username of client
			else:
				pass

	#-----------------------------------------------------------------------------------------

	#Makese sure the client is registered
	def registerClient(self, nick, host, username):

		#If the details are valid then it registers the client
		for clients in clientList:
			if clients.nick == nick and clients.host == host and clients.userName == username:
				clients.registered = True

				#Client is registered, here we send the 
				#RPL_WECLOME code/message


	#-----------------------------------------------------------------------------------------

	#This function deals with whatever the client does
	def newClient(self, conn, client_address):
		while True:
			data = conn.recv(self.ircMessagesLength)
			
			#print(str(data)) #prints raw data
			
			#Decodes the data to make it more readable and splits it by line
			msg = data.decode("utf-8")
			line = msg.split("\r\n")
		
			#Splits the client's address
			strClientAddress = str(client_address)
			clientAddress = strClientAddress.split(" ")
			clientAddressSubbed  = re.sub(',', '', clientAddress[1]) #gets rid of the ','

			#checks if/what command has been used
			self.checkCommands(line, clientAddressSubbed)
			






			#If no data being send and connection closed.
			if not data:			
				break
			conn.sendall(data)
		conn.close()	

	#Function  used to establish the server
	def startServer(self):
		#waits for someone/thing to connect
		while True:
			connection, client_address = self.sock.accept() #connection occured and accepted
		
			#Starts a new thread
			start_new_thread(self.newClient, (connection, client_address))
		
		sock.close() #closes the socket

	#-----------------------------------------------------------------------------------------


#Main calls the main server class to run the server
def main():
	x= Server()
	x.startServer()
	
#Executes the main function
main()