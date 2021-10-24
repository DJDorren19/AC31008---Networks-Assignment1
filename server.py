
import socket
import os
from _thread import *
import threading
import re


#Map used to store all the error codes
errorCodes = {

	'ERR_NOSUCHNICK': 401, #NOT IMPLAMENTED FULLY - JUST CALL BUT NO CASE
	'ERR_NOSUCHCHANNEL': 403,
	'ERR_CANNOTSENDTOCHAN': 404, #NOT IMPLAMENTED
	'ERR_TOOMANYCHANNELS': 405,
	'ERR_TOOMANYTARGETS': 407, #NOT IMPLAMENTED
	"ERR_NORECIPIENT": 411, #NOT IMPLAMENTED
	"ERR_NOTEXTTOSEND": 412, #NOT IMPLAMENTED
	"ERR_UNKNOWNCOMMAND": 421,
	'ERR_NONICKNAMEGIVEN': 431,
	'ERR_ERRONEUSNICKNAME' : 432,
	'ERR_NICKNAMEINUSE': 433, 

	'ERR_USERNOTINCHANNEL': 441,#NOT IMPLAMENTED
	'ERR_NOTONCHANNEL': 442, #NOT IMPLAMENTED
	'ERR_USERONCHANNEL': 443, #NOT IMPLAMENTED
	'ERR_NOLOGIN': 444, #NOT IMPLAMENTED
	'ERR_NOTREGISTERED': 451, #SHOULD HAVE THE FOUNDATION FOR THIS BAD BOY

	'ERR_NEEDMOREPARAMS': 461 #NOT IMPLAMENTED/LIMITED IMPLAMENTATION
}

#Map used to store all the reply codes
replyCodes = {

	'RPL_WELCOME': 1,
	'RPL_LUSERCHANNELS': 254,
	'RPL_NOTOPIC': 331,
	'RPL_TOPIC': 332
	
}

#Global lists (Very secure /s)
channelList = [] #Stores all the channels
clientList = [] #Stores all the clients

#-----------------------------------------------------------------------------------------

#Class to hold all of the channel details
class Channel:
	def __init__(self, name):
		self.name = name
		self.clientList = [] #List to hold clients in channel
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
	ircMessagesLength = 512 #Pretty sure this is the max number of characters allowed by rfc2812
	maxChannels = 4 #max channels a user is allwed to join
	
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
		for clients in clientList:
			if clients.host == client.host:
				clients.nick = nick

	#Gets the client by their host (I know this is stupid but it's a bandaid solution righ now)
	def getClient(self, host):
		if clientList:
			for clients in clientList:
				if clients.host == host:
					return clients

	#Sets the client's username
	def setUsername(self, username, client):
		for clients in clientList:
			if clients.host == client.host:
				clients.userName = username

	#gets the channel by searching with channel name
	def getChannel(self, channelName):
		if channelList:
			for items in channelList:
				if channelName == items.name:
					return items

	#Adds the channel to client list of channels
	def addClientChannel(self, newChannel, client):
		
		channel = self.getChannel(newChannel)

		if client not in channel.clientList:
			client.connectedChannels.append(channel)
			channel.clientList.append(client)
			print("moving client to channel") #DELETE THIS FOR FINAL VERSION

	#Makese sure the client is registered
	def registerClient(self, client):
		if client in clientList:
			if client.nick and client.userName:

				print(client.nick, client.userName)

				#Registers the client and sends welcome message being sent to the user
				client.registered = True
				
				msg = str(replyCodes["RPL_WELCOME"]) + " " +"Welcome to the Internet Relay Network\n" + \
					client.nick + "!" + client.userName + "@" + client.host
				self.sendMessage(client, msg, False)

				return client.registered

	#-----------------------------------------------------------------------------------------
	
	#Used to send messages to the client
	def sendMessage(self, client, message, privateMsg=True):

		connection = client.connection
		###########################################
		senderName = "JACK" #SHOULD NOT BE JACK BUT THE CLIENT WHO IS SENDING THE MESSAGE OR SERVER
		###########################################

		#Private messages the client
		if privateMsg:
			#Sets up the message to be sent, JACK should be the sender's name, which could be another user or server 
			msg = ":" + senderName + "!" + client.userName + "@" + str(client.host) + " PRIVMSG "
			msg = msg+message+"\r\n"
			connection.send(msg.encode('utf-8'))

		#Notice message
		else:
			msg = ":" + senderName + "!" + client.userName + "@" + str(client.host) + " NOTICE "
			msg = msg+message+"\r\n"
			connection.send(msg.encode('utf-8'))

	#-----------------------------------------------------------------------------------------

	#Handles the different errors that could occur when assigning a nick
	def handleNick(self, nick):

		#Another "switch" that looks for any issues with nick
		if clientList: #checks if the nick is already taken
			for clients in clientList:
				if clients.nick == nick:
					return "ERR_NICKNAMEINUSE"	

		if len(nick) > 9: #Checks if the nick name is too long
			return "ERR_ERRONEUSNICKNAME"
 
		if not nick: #Checks if nick is empty
			return "ERR_NONICKNAMEGIVEN"

		#If no issues
		return "NO_ERROR"

	#Checks what nick error it is and sends the correspoding message
	def checkNickError(self, anyError, client, nick):

		#Think these should be private messages

		# NO ACTUAL CALL FOR THIS YET
		if anyError == "ERR_NOSUCHNICK":
			message = str(errorCodes["ERR_NOSUCHNICK"]) + " " + nick + " :No such nick"
			self.sendMessage(client, message, True)

		if anyError == "ERR_NICKNAMEINUSE":
			message = str(errorCodes['ERR_NICKNAMEINUSE']) + " " + nick + " :Nickname is already in use"
			self.sendMessage(client, message, True)

		if anyError == "ERR_NONICKNAMEGIVEN":
			message = str(errorCodes['ERR_NONICKNAMEGIVEN']) + " :No nickname given"
			self.sendMessage(client, message, True)

		if anyError == "ERR_ERRONEUSNICKNAME":
			 message = str(errorCodes['ERR_ERRONEUSNICKNAME']) + " " + nick + " :Erroneus nickname"
			 self.sendMessage(client, message, True)

	#-----------------------------------------------------------------------------------------

	#Creates a new channel if does not exists, otherwise moves player to channel
	def handleChannels(self, newName, client):
		
		channels = len(client.connectedChannels) #number of channels client is connected to
		inList = False #used to see if channel already exists
		newChannel = {}

		#checks if channel already exists
		if channelList:
			for items in channelList:
				if newName == items.name:
					inList = True

		#checks if client can join anymore channels
		if channels > self.maxChannels:
			return "ERR_TOOMANYCHANNELS"

		#channel name invalid. ADD MORE INVALID CHARACTERS
		if newName[0] != "#":
			return "ERR_NOSUCHCHANNEL"
		
		#if it does not exits, create it and add to list of channels
		if not inList:
			newChannel = Channel(newName)
			channelList.append(newChannel)

		#No errors occured
		return "NO_ERROR"


	#Checks what channel error it is and sends the correspoding message
	def checkChannelError(self, anyError, client, channel):
		if channel:
			if anyError == "ERR_TOOMANYCHANNELS":
				message = str(errorCodes['ERR_TOOMANYCHANNELS']) + " " + channel + " :You have joined too many channels"
				self.sendMessage(client, message, True)

			if anyError == "ERR_NOSUCHCHANNEL":
				message = str(errorCodes['ERR_NOSUCHCHANNEL']) + " " + channel + " :No such channel"
				self.sendMessage(client, message, True)

	#-----------------------------------------------------------------------------------------



	#Used to alter the topic of a channel #NEED TO ADD ERROR CHECKING FOR CHANNEL NAME
	def handleTopic(self, sentLines, client):

		numberOfLines = len(sentLines)
		channelName = sentLines[1]
		channel = self.getChannel(channelName)

		#if channel is not empty
		if channel:

			#Shows the topic of certain a channel
			if numberOfLines == 2:
				if not channel.topic:
					self.checkTopicError("RPL_NOTOPIC", client, channel)
				else:
					self.checkTopicError("RPL_TOPIC", client, channel)
					
			#Clears the topic of a certain channel
			elif numberOfLines == 3:
				print(sentLines[2])
				if sentLines[2] == "::":
					channel.topic = ""
				
					self.checkTopicError("RPL_NOTOPIC", client, channel)

			#Replaces the topic of a certain channel
			elif numberOfLines == 4:
				if sentLines[2] == "::another":
					newTopic = sentLines[3]
					channel.topic = newTopic

					self.checkTopicError("RPL_TOPIC", client, channel)
				else:
					message = str(errorCodes['ERR_UNKNOWNCOMMAND']) + " " + sentLines[2] + " :Unknown command"
					self.sendMessage(client, message, False)
		else:	
			self.checkTopicError("ERR_NEEDMOREPARAMS", client, channel)
		

	#Deals sending reply/error messages for topics
	def checkTopicError(self, anyError, client, channel):

		if anyError == "RPL_TOPIC":
			msg = str(replyCodes["RPL_TOPIC"]) + " " + channel.name + " :" + channel.topic 
			self.sendMessage(client, msg, True)

		if anyError == "RPL_NOTOPIC":
			msg = str(replyCodes["RPL_NOTOPIC"]) + " " + channel.name + " :No topic is set"
			self.sendMessage(client, msg, True)
		
		#Quite redundant as similar message will be sent later
		if anyError == "ERR_NEEDMOREPARAMS":
			message = str(errorCodes["ERR_NEEDMOREPARAMS"]) + " " + "TOPIC" + " :Not enought parameters"
			self.sendMessage(client, message, False)

	#-----------------------------------------------------------------------------------------

	#Called when the JOIN command is used, should make the switch easier to read
	def join(self, newChannel, client):
		anyError = self.handleChannels(newChannel, client)

		if anyError == "NO_ERROR":
			self.addClientChannel(newChannel, client)
		else:
			self.checkChannelError(anyError, client, newChannel)

	#Called when the NICK command is used, should make the switch easier to read
	def nick(self, newNick, client):
		anyError = self.handleNick(newNick) 
		
		if anyError == "NO_ERROR":
			self.setNick(newNick, client)
		else:
			self.checkNickError(anyError, client, newNick)

	#Called when the LUSER command is used, should make the switch easier to read
	def lUser(self, client):
		noChannels = 0
		for channels in channelList:
			noChannels+=1

		#Sends the number of users in channel reply
		msg = str(replyCodes["RPL_LUSERCHANNELS"]) + " " + str(noChannels) + " :channels formed"
		self.sendMessage(client, msg, True)

	#-----------------------------------------------------------------------------------------

	#Determines what command has been entered by the client
	def checkCommands(self, command, client):
	
		#for the number of lines in list
		for lines in command:

			#Splits up all the lines to be readable
			sentLine = lines.split(" ")
			tempCommand = sentLine[0]

			#Ignores white spaces or "CAP" - whatever that means
			if tempCommand == "" or tempCommand == "CAP":
				break

			#Command used to create/join a channel
			if tempCommand == "JOIN":
				newChannel = sentLine[1]
				self.join(newChannel, client)
			
			#Command used to set/change the nick
			elif tempCommand == "NICK": 
				newNick = sentLine[1]
				self.nick(newNick, client)

			#Command used to set the username
			elif tempCommand == "USER":
				self.setUsername(sentLine[1], client) #Changes the username of client

			#LUSER commands
			elif tempCommand == "LUSER":
				if len(sentLine) == 2:
					self.lUser(client)
				else:
					#probably some error here
					pass
			
			#TOPIC commands
			elif tempCommand == "TOPIC":
				self.handleTopic(sentLine, client)

			#Command used to quit server
			elif tempCommand == "QUIT":
				pass

			else: #Message is not known to the server
				message = str(errorCodes['ERR_UNKNOWNCOMMAND']) + " " + tempCommand + " :Unknown command"
				self.sendMessage(client, message, False)

	#-----------------------------------------------------------------------------------------

	#This function deals with whatever the client does
	def newClient(self, conn, client_address):

		clientWelcomed = False #Only used to welcome the client
		print("NEW THREAD")

		while True:
			data = conn.recv(self.ircMessagesLength)
			
			#Decodes the data to make it more readable and splits it by line
			msg = data.decode("utf-8")
			line = msg.split("\r\n")
		
			#Splits the client's address
			clientAddress = str(client_address).split(" ")
			clientAddressSubbed  = re.sub(',', '', clientAddress[1]) #gets rid of the ','

			#creates a new client
			self.createClient(conn, clientAddressSubbed)
			newClient = self.getClient(clientAddressSubbed) #gets the new client for later use

			#checks if/what command has been used
			self.checkCommands(line, newClient)
			
			#Makes sure that this fucntion is ran once and registers the client
			if not clientWelcomed:
				clientWelcomed = self.registerClient(newClient)

			#If no data being send and connection closed.
			if not data:			
				break
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