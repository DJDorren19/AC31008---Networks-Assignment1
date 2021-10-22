
import socket
import os
from _thread import *
import threading
import re


#####WHAT TO DO
#	YOU ADDED CONNECTION TO CLIENT SO MAKE THE FUNCTIONS BETTER


#Map used to store all the error codes
error_Codes = {

	'ERR_NONICKNAMEGIVEN': 431,
	'ERR_ERRONEUSN'
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
	def __init__(self, name):
		self.name = name
		self.clientList = [] #List to hold clients 
		self.topic = {}

#-----------------------------------------------------------------------------------------

#Class to hold all of the client details
class Clients:
	def __init__(self, conn, clientAddress):
		self.nick = {}
		self.connection = conn
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

	#Simple function to just create user and add them to the list of clients on server
	def createClient(self, conn, host):
		self.clientNew = Clients(conn, host)
		clientList.append(self.clientNew)
	
	#sets the nick of the client
	def setNick(self, nick, client):
		if client in clientList:
			client.nick = nick

		
	#Gets the client by their host (I know this is stupid but it's a bandaid solution righ now)
	def getClient(self, host):
		if clientList:
			for clients in clientList:
				if clients.host == host:
					return clients

	#Sets the client's username
	def setUsername(self, username, client):
		if client in clientList:
			client.username = username
			print(client.username)

	#Makese sure the client is registered
	def registerClient(self, client):
		if client in clientList:
				client.registered = True

				#Client is registered, here we send the 
				#RPL_WECLOME code/message

	#-----------------------------------------------------------------------------------------

	#Handles the different errors that could occur when assigning a nick
	def handleNick(self, nick):

		#Another "switch" that looks for any issues with nick
		if clientList: #checks if the nick is already taken

			for clients in clientList:
				if clients.nick == nick:
					return "ERR_NICKNAMEINUSE"	

		if len(nick) > 9: #Checks if the nick name is too long
			#send the ERR_ERRONEUSNICKNAME here
			pass 

		if not nick: #Checks if nick is empty
			#send the ERR_NONICKNAMEGIVEN here
			pass

		#If no issues
		return "NO_ERROR"
		
	#-----------------------------------------------------------------------------------------
	
	#Determines what command has been entered by the client
	def checkCommands(self, command, client, conn):
		
		#for the number of lines in list
		for lines in command:

			#Splits up all the lines to be readable
			sentLine = lines.split(" ")
			tempCommand = sentLine[0]

			#A "switch" to see what command has been entered
			if tempCommand == "JOIN":
				if sentLine[1][0] == "#":
					self.manageChannels(sentLine[1]) #creates a new channel
				else:
					#ERROR FOR BAD NAMING PRACTICE, NO # AT THE START FOR CHANNEL
					pass

			elif tempCommand == "NICK":
				#Checks if nick is already taken (should change NO_ERROR to something else)
				anyError = self.handleNick(sentLine[1]) 
				if anyError == "NO_ERROR":
					self.setNick(sentLine[1], client)
				else:
					self.checkError(anyError)


			elif tempCommand == "USER":
				self.setUsername(sentLine[1], client) #Changes the username of client
			else:
				pass #nothing

	#-----------------------------------------------------------------------------------------

	def checkError(anyError):

		if anyError == "ERR_NICKNAMEINUSE":
			pass





	
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

	#This function deals with whatever the client does
	def newClient(self, conn, client_address):
		while True:
			data = conn.recv(self.ircMessagesLength)
			
			#Decodes the data to make it more readable and splits it by line
			msg = data.decode("utf-8")
			line = msg.split("\r\n")
		
			#Splits the client's address
			strClientAddress = str(client_address)
			clientAddress = strClientAddress.split(" ")
			clientAddressSubbed  = re.sub(',', '', clientAddress[1]) #gets rid of the ','

			#creates a new client
			self.createClient(conn, clientAddressSubbed)
			newClient = self.getClient(clientAddressSubbed) #gets the new client for later use

			#checks if/what command has been used
			self.checkCommands(line, newClient, conn)

			#Registers the client 
			self.registerClient(newClient)

			
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