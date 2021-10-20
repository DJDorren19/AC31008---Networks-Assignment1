
import socket
import os
from _thread import *
import threading
import re

#Global lists (Very secure /s)
channelList = [] #Stores all the channels
clientList = [] #Stores all the clients


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
	def __init__(self, nick, clientAddress):
		self.nick = nick
		self.connectedChannels = []
		self.userName = {}
		self.host = clientAddress

#-----------------------------------------------------------------------------------------


	
	



class Server:
	
	#global variables
	sock = None 
	
	#Server constructor
	def __init__(self):

		PORT = 6667
		HOST = '::1'
		numberOfClients = 3 #numbers of clients allowed to connect


		#decalres the socket and server address
		self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		server_adderess = (HOST, PORT)
		print('Starting up on', HOST , 'PORT', PORT)

		#Allows to reuse the socket. Big POG and binds scoket to port.
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(server_adderess)

		#Allows for an x number of clients
		self.sock.listen(numberOfClients)

	#-----------------------------------------------------------------------------------------

	#Simple function to just create user and add them to the list of clients on server
	def createClient(self, nick, clientAddress):
		self.clientNew = Clients(nick, clientAddress)
		clientList.append(self.clientNew)

	#-----------------------------------------------------------------------------------------

	#Creates a new channel if does not exists, otherwise moves player to channel
	def manageChannels(self, newName, topic):
		
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
				newChannel = Channel(newName, topic)
				channelList.append(newChannel)
				print("Creating a new channel")
		else:
			newChannel = Channel(newName, topic)
			channelList.append(newChannel)
			print("Creating a new channel")

	#-----------------------------------------------------------------------------------------

	#Changes the username of the client
	def applyUsername(self, username, clientAdderss):
		for clients in clientList:
			if clients.host == clientAdderss:
				clients.userName = username

	#Version of python I am using (3.8) does not allow for switch statments so here we are.
	def checkCommands(self, command, clientAddress):
		
		#for the number of lines in list
		for lines in command:

			#Splits up all the lines to be readable
			sentLine = lines.split(" ")
			tempCommand = sentLine[0]

			if tempCommand == "JOIN":
				self.manageChannels(sentLine[1], "No Topic Yet") #creates a new channel
			elif tempCommand == "NICK":
				self.createClient(sentLine[1], clientAddress) #Creates a new user
			elif tempCommand == "USER":
				print("NEW USER", sentLine[1])

				self.applyUsername(sentLine[1], clientAddress)



				#it would get the user by host and then change their username

		else:
			pass

	#-----------------------------------------------------------------------------------------

	#This function deals with whatever the client does
	def newClient(self, conn, client_address):
		while True:
			data = conn.recv(1024)
			
			#print(str(data)) #prints raw data
			
			#Decodes the data to make it more readable and splits it by line
			msg = data.decode("utf-8")
			line = msg.split("\r\n")
		
			#Splits the client's address
			strClientAddress = str(client_address)
			clientAddress = strClientAddress.split(" ")
			clientAddressSubbed  = re.sub(',', '', clientAddress[1])

			#checks if/what command has been used
			self.checkCommands(line, clientAddressSubbed)

			#If no data being send and connection closed.
			if not data:			
				break
			conn.sendall(data)
		conn.close()	

	def startServer(self):
		#waits for someone/thing to connect
		while True:
			print('Waiting for a connection')
			connection, client_address = self.sock.accept() #connection occured
			
			print('Connection from', client_address)
			
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