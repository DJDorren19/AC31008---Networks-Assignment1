
import socket
import os
from _thread import *
import threading
import re
from datetime import datetime
import sys


#Map used to store all the error codes
errorCodes = {

	'ERR_NOSUCHNICK': 401,
	'ERR_NOSUCHCHANNEL': 403,
	'ERR_TOOMANYCHANNELS': 405,
	'ERR_TOOMANYTARGETS': 407, #NOT IMPLAMENTED
	"ERR_NORECIPIENT": 411,
	"ERR_NOTEXTTOSEND": 412,
	"ERR_UNKNOWNCOMMAND": 421,
	'ERR_NONICKNAMEGIVEN': 431,
	'ERR_ERRONEUSNICKNAME' : 432,
	'ERR_NICKNAMEINUSE': 433, 

	'ERR_NOTONCHANNEL': 442,
	'ERR_NOTREGISTERED': 451,

	'ERR_NEEDMOREPARAMS': 461,
	'ERR_ALREADYREGISTERED': 462,
	'ERR_CHANNELISFULL': 471
}

#Map used to store all the reply codes
replyCodes = {

	'RPL_WELCOME': "001",
	'RPL_LUSERCHANNELS': 254,
	'RPL_NOTOPIC': 331,
	'RPL_TOPIC': 332,
	'RPL_NAMERPLY': 353,
	'RPL_ENDOFNAMES': 366

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

			self.printToServer(client, "Moving client to channel: " + newChannel)

		else:
			self.printToServer(client, "Client already in channel: " + newChannel)

	#Removes the client from the channel list
	def partClientFromChannel(self, newChannel, client):

		channel = self.getChannel(newChannel)
		if client in channel.clientList:
			client.connectedChannels.remove(channel)
			channel.clientList.remove(client)
			
			#This allows hexchat to know that the user has joined the channel
			message = ":" + client.nick + "!" + client.userName + "@" + client.host + " PART " + newChannel
			message = message +"\r\n"
			client.connection.send(message.encode('utf-8'))

			print("Removing client from: " + newChannel)
		else:
			print("Client not in" + newChannel)

	#Makese sure the client is registered
	def registerClient(self, client):
		if client in clientList:
			if client.nick and client.userName:

				#Registers the client and sends welcome message being sent to the user
				client.registered = True

				#Message sent to the terminal
				self.printToServer(client, "Registered Client " + "")
				
				msg = str(replyCodes["RPL_WELCOME"]) + " " +"Welcome to the Internet Relay Network\n" + \
					client.nick + "!" + client.userName + "@" + client.host
				self.sendMessage(client, msg, "Server", False)

				return client.registered

	#-----------------------------------------------------------------------------------------
	
	#Used to send messages to the client
	def sendMessage(self, client, message, senderName, privateMsg):

		connection = client.connection

		#Private messages the client
		if privateMsg:
			#Sets up the message to be sent, JACK should be the sender's name, which could be another user or server 
			msg = ":" + senderName + "!" + str(client.userName) + "@" + str(client.host) + " PRIVMSG " + client.nick
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

		if anyError == "ERR_NICKNAMEINUSE":
			message = str(errorCodes['ERR_NICKNAMEINUSE']) + " " + nick + " :Nickname is already in use"
			self.sendMessage(client, message, "Server", True)

		if anyError == "ERR_NONICKNAMEGIVEN":
			message = str(errorCodes['ERR_NONICKNAMEGIVEN']) + " :No nickname given"
			self.sendMessage(client, message, "Server", True)

		if anyError == "ERR_ERRONEUSNICKNAME":
			 message = str(errorCodes['ERR_ERRONEUSNICKNAME']) + " " + nick + " :Erroneus nickname"
			 self.sendMessage(client, message, "Server", True)

		if anyError == "ERR_NOSUCHNICK":
			 message = str(errorCodes['ERR_NOSUCHNICK']) + " " + nick + " :No such nick"
			 self.sendMessage(client, message, "Server", True)

	#-----------------------------------------------------------------------------------------

	#Deals with the changing of username
	def user(self, client, username):
		if not client.userName:
			self.setUsername(username, client) #Changes the username of client
		else:
			message = str(errorCodes["ERR_ALREADYREGISTERED"]) + "" + "" + " :You may not register"
			self.sendMessage(client, message, "Server", True)

	#-----------------------------------------------------------------------------------------

	#Creates a new channel if does not exists, otherwise moves player to channel
	def handleChannels(self, newName, client, newTopic):
		
		channels = len(client.connectedChannels) #number of channels client is connected to
		inList = False #used to see if channel already exists
		newChannel = {}
	
		#checks if channel already exists
		if channelList:
			for items in channelList:
				if newName == items.name:
					inList = True

		#checks if client can join anymore channels
		if channels >= self.maxChannels and newTopic != "parting":
			return "ERR_TOOMANYCHANNELS"

		#channel name invalid. ADD MORE INVALID CHARACTERS
		if newName[0] != "#":
			return "ERR_NOSUCHCHANNEL"

		#if it does not exits, create it and add to list of channels
		if not inList:
			newChannel = Channel(newName)
			channelList.append(newChannel)
			newChannel.topic = ""

		#No errors occured
		return "NO_ERROR"


	#Checks what channel error it is and sends the correspoding message
	def checkChannelError(self, anyError, client, channel):
		if channel:
			if anyError == "ERR_TOOMANYCHANNELS":
				message = str(errorCodes['ERR_TOOMANYCHANNELS']) + " " + channel + " :You have joined too many channels"
				self.sendMessage(client, message, "Server", True)

			if anyError == "ERR_NOSUCHCHANNEL":
				message = str(errorCodes['ERR_NOSUCHCHANNEL']) + " " + channel + " :No such channel"
				self.sendMessage(client, message, "Server", True)

	#-----------------------------------------------------------------------------------------

	#Used to alter the topic of a channel #NEED TO ADD ERROR CHECKING FOR CHANNEL NAME
	def handleTopic(self, sentLines, client):

		numberOfLines = len(sentLines)
		channelName = sentLines[1]
		channel = self.getChannel(channelName)
		newTopic = ""

		#if channel is not empty
		if channel and client in channelList:

			#Shows the topic of certain a channel
			if numberOfLines == 2:
				if not channel.topic:
					self.checkTopicError("RPL_NOTOPIC", client, channel, True)
				else:
					self.checkTopicError("RPL_TOPIC", client, channel, True)
					
			#Clears the topic of a certain channel
			elif numberOfLines == 3:
				if sentLines[2] == "::":
					channel.topic = newTopic
				
					self.checkTopicError("RPL_NOTOPIC", client, channel, True)

			#Replaces the topic of a certain channel
			elif numberOfLines >= 4:
				if sentLines[2] == "::another":

					for lines in sentLines[3:]:
						newTopic = newTopic + " " + lines

					channel.topic = newTopic

					self.checkTopicError("RPL_TOPIC", client, channel, True)
				else:
					message = str(errorCodes['ERR_UNKNOWNCOMMAND']) + " " + sentLines[2] + " :Unknown command"
					self.sendMessage(client, message, "Server", True)

		elif client not in channelList:
			message = str(errorCodes["ERR_NOTONCHANNEL"]) + " " + channel.name + " :You're not on that channel"
			self.sendMessage(client, message, "Server", True)	
		else:	
			self.checkTopicError("ERR_NEEDMOREPARAMS", client, channel, True)
		
	#Deals sending reply/error messages for topics
	def checkTopicError(self, anyError, client, channel, channelPrefix):

		if anyError == "RPL_TOPIC" or not channelPrefix:
			msg = str(replyCodes["RPL_TOPIC"]) + " " + channel.name + " :" + channel.topic 
			self.sendMessage(client, msg, "Server",True)

		if anyError == "RPL_NOTOPIC" and channelPrefix:
			msg = str(replyCodes["RPL_NOTOPIC"]) + " " + channel.name + " :No topic is set"
			self.sendMessage(client, msg, "Server", True)
		
		#Quite redundant as similar message will be sent later
		if anyError == "ERR_NEEDMOREPARAMS" and channelPrefix:
			message = str(errorCodes["ERR_NEEDMOREPARAMS"]) + " " + "TOPIC" + " :Not enought parameters"
			self.sendMessage(client, message, "Server", True)

	#-----------------------------------------------------------------------------------------

	#Called when the JOIN command is used, should make the switch easier to read
	def join(self, sentLines, client):

		newChannel = sentLines[1]
		anyError = self.handleChannels(newChannel, client, "")

		#Clients leaves all channels
		if newChannel == "0":

			print("Exiting all Channels")

			#Removes the client from all channels
			while len(client.connectedChannels) != 0:
				for channels in client.connectedChannels:
					self.partClientFromChannel(channels.name, client)
			
		else:
			#If there is no error with the channel name
			if anyError == "NO_ERROR":
				self.addClientChannel(newChannel, client)
			
				temp = self.getChannel(newChannel)
				self.checkTopicError("RPL_TOPIC", client, temp, False)

				#This allows hexchat to know that the user has joined the channel
				message = ":" + client.nick + "!" + client.userName + "@" + client.host + " JOIN " + newChannel
				message = message +"\r\n"
				client.connection.send(message.encode('utf-8'))

			else:
				self.checkChannelError(anyError, client, newChannel)

	#Called when the PART command is used, should make the switch easier to read
	def part(self, channelNames, client):

		storeChannels = channelNames.split(",")

		#for the number of channels the client wants to leave (all)
		for splitChannels in storeChannels:
			anyError = self.handleChannels(splitChannels, client, "parting")

			if anyError == "NO_ERROR":
				self.partClientFromChannel(splitChannels, client)
			else:
				self.checkChannelError(anyError, client, splitChannels)

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

	#Deals with printing the replies for NAMES
	def namesReplies(self, reply, client, tempList, channelName):

		if reply == "RPL_ENDOFNAMES":
			message =  str(replyCodes["RPL_ENDOFNAMES"]) + " " + tempList + " :End of /NAMES list" 
			self.sendMessage(client, message, "Server", True)
		
		elif reply == "RPL_NAMERPLY":
			message =  str(replyCodes["RPL_NAMERPLY"]) + " " + channelName+ " :" +  tempList
			self.sendMessage(client, message, "Server", True)

	#Called when the NAMES command is used, should make the switch easier to read
	def names(self, sentLines, client):
		
		#Locals
		splitLines = sentLines[1].split(",")
		linesLength = len(splitLines)
		tempList = ""

		#if only /NAMES is sent
		if linesLength == 1:

			#checks is param was given
			if splitLines[0][0] != "#":
				channelName = ""

				#if not then loops for the whole list of channels
				for channels in channelList:
					channelName = channels.name

					tempList = tempList + channelName + " :"

					for clinets in channels.clientList:
						tempList = tempList + "@" + clinets.nick

					tempList = tempList + "\n"
				
				self.namesReplies("RPL_ENDOFNAMES", client, tempList, "")

			else:
				thisChannel = self.getChannel(splitLines[0])
				#If the channel exists, print all the users in that channel
				if thisChannel:
					for clinets in thisChannel.clientList:
						tempList = tempList + " @" + clinets.nick

				self.namesReplies("RPL_NAMERPLY", client, tempList, splitLines[0])

		#if trying to get clients in specific channel
		elif linesLength > 1:

			temp = 0
			while temp < linesLength:

				channelName = splitLines[temp]
				tempList =""
				
				if channelName[0] == "#":
					#Gets the client list in the channel and then 
					thisChannel = self.getChannel(channelName)

				#If the channel exists, print all the users in that channel
				if thisChannel:
					for clinets in thisChannel.clientList:
						tempList = tempList + " @" + clinets.nick

					self.namesReplies("RPL_NAMERPLY", client, tempList, channelName)
			
				#If not then reply with end of names
				else:
					self.namesReplies("RPL_ENDOFNAMES", client, channelName, "")

				temp+=1

	#Used to message people on a specific channel
	def channelMessage(self, client, sentLine):
		try:
			#Sets up variables
			targetName = sentLine[1] #channel name
			message = sentLine[1:] #message to channel
			msg=""
			targetChannel = {} #will contain the channel

			#Concatenates the message into string
			for lines in message:
				msg= msg+ " " + lines

			targetChannel = self.getChannel(targetName)

			#If the channel exists, send all the users on that channel a message
			if targetChannel:
				if targetChannel in client.connectedChannels:
					for clients in targetChannel.clientList:
						if clients == client:
							pass
						else:
							self.sendMessage(clients, msg, client.nick, False)
				else:
					message = str(errorCodes["ERR_NOTONCHANNEL"]) + " " + targetChannel.name + " :You're not on that channel"
					self.sendMessage(client, message, "Server", True)						
		except:
			print("Error occured when sending msg to channel")

	#Deals with sending private messages to and from users
	def privateMessage(self, client, sentLine):
		
		try:
			#Sets up variables
			targetName = sentLine[1]
			message = sentLine[1:]
			msg=""
			targetClient = {}

			#determines if the messages are sent to channel or client
			if targetName[0] == "#":
				self.channelMessage(client, sentLine)
			else:
				#Concatenates the message into string
				for lines in message:
					msg= msg+ " " + lines

				#gets the client, Can't use the get method because we don't have host, oops
				for clients in clientList:
					if clients.nick == targetName:
						targetClient=  clients

				#Checks for error codes
				anyError = self.handleMessages(targetName, msg)

				#If the nick/receiver name is good
				if anyError == "NO_ERROR":
					if targetClient:
						self.sendMessage(targetClient, msg,  client.nick, True)
				else:
					self.messageErrors(anyError, client, targetName, "PRIVMSG")	

		except:
			self.printToServer(client, "Not enough params")
			anyError = self.handleMessages("", "")
			self.messageErrors(anyError, client, "", "PRIVMSG")		

	#Sends errors for messages
	def messageErrors(self, anyError, client, nick, command):

		#Nick was not given
		if anyError == "ERR_NOSUCHNICK":
			message = str(errorCodes["ERR_NOSUCHNICK"]) + " " + nick + " :No such nick/channel"
			self.sendMessage(client, message, "Server", True)

		#No nick was given
		if anyError == "ERR_NORECIPIENT":
			message = str(errorCodes["ERR_NORECIPIENT"]) + " " + nick + " :No recipient given (" + command + ")"
			self.sendMessage(client, message, "Server", True)
		
		#Client did not give any text to be sent
		if anyError == "ERR_NOTEXTTOSEND":
			message = str(errorCodes["ERR_NOTEXTTOSEND"]) + " " + ":No text to send"
			self.sendMessage(client, message, "Server", True)

		#Client gave too many other clients to access
		if anyError == "ERR_TOOMANYTARGETS":
			message = str(errorCodes["ERR_TOOMANYTARGETS"]) + " " + nick + " :407 recipients. Try again"
			self.sendMessage(client, message, "Server", True)

	#Used to determine the error code for messages
	def handleMessages(self, nick, msg):

		#If the user is trying to access a lot more recipients
		if "@" in nick or "," in nick:
			return "ERR_TOOMANYTARGETS"

		#If no nick given
		if nick == "":
			return "ERR_NORECIPIENT"

		tempClient = "" #used to check if client in list

		#Checks if the nick exists in the list
		for clients in clientList:
			if clients.nick == nick:
				tempClient = clients.nick

		#if not then sends error	
		if not tempClient:
			return "ERR_NOSUCHNICK"

		#If message is left blank
		temp = msg.split(" ")
		if len(temp) <= 2 :
			return "ERR_NOTEXTTOSEND"

		return "NO_ERROR"


	#Deals with disconnecting client from server
	def quit(self, client, message):

		temp = ""
		#quit message 
		for lines in message:
			temp = temp + " " + lines

		#Removes the client from client list
		if client in clientList:
			clientList.remove(client)
		
		#Removes the client from all channels
		for channels in channelList:
			if client in channels.clientList:
				channels.clientList.remove(client)

		self.printToServer(client, "Has quit the server")
		
		client.connection.shutdown(2)
		client.connection.close()

		sys.exit() #closes the thread

	#-----------------------------------------------------------------------------------------

	#Used to sent whatever the client does to the server
	def printToServer(self, client, message):
		time = datetime.now()
		currentTime = time.strftime("%H:%M:%S")
		print(currentTime, ": "+ str(client.nick) + " :" + str(client.userName) +"@" + str(client.host) + " :" + str(message))

	#-----------------------------------------------------------------------------------------

	#Determines what command has been entered by the client
	def checkCommands(self, command, client):
		
		clientRegistered = client.registered

		#for the number of lines in list
		for lines in command:

			#Splits up all the lines to be readable
			sentLine = lines.split(" ")
			tempCommand = sentLine[0]

			#Ignores white spaces or "CAP" - whatever that means
			if tempCommand == "" or tempCommand == "CAP":
				break
			
			#Command used to set/change the nick
			if tempCommand == "NICK": 
				newNick = sentLine[1]
				self.nick(newNick, client)

			#Command used to set the username
			elif tempCommand == "USER":
				#Bandaid fix to not let server crash
				try: 
					self.user(client, sentLine[1])
					self.setUsername(sentLine[1], client) #Changes the username of client
				except:
					pass

			#Command used to create/join a channel
			elif tempCommand == "JOIN" and clientRegistered:
				#Bandaid fix to not let server crash
				try:
					self.join(sentLine, client)
				except:
					pass	

			#Command used to leave a channel
			elif tempCommand == "PART" and clientRegistered:
				#Bandaid fix to not let server crash
				try:
					channelNames = sentLine[1]
					self.part(channelNames, client)
				except:
					pass	

			#LUSER commands
			elif tempCommand == "LUSER" and clientRegistered:
				if len(sentLine) == 2:
					self.lUser(client)
			
			#TOPIC commands
			elif tempCommand == "TOPIC" and clientRegistered:
				self.handleTopic(sentLine, client)

			#used to list visible channels/clients
			elif tempCommand == "NAMES" and clientRegistered:
				self.names(sentLine, client)

			#Command used to private message client
			elif tempCommand == "PRIVMSG" and clientRegistered:
				self.privateMessage(client, sentLine)
				
			#Command used to quit server
			elif tempCommand == "QUIT":
				self.quit(client, sentLine)
		
			#if the client is not registered and tries to use commands
			elif not clientRegistered:
				message = str(errorCodes["ERR_NOTREGISTERED"]) + "" + " " + ":You have not registered"
				self.sendMessage(client, message, "Server", True)

			else: #Message is not known to the server
				message = str(errorCodes['ERR_UNKNOWNCOMMAND']) + " " + tempCommand + " :Unknown command"
				self.sendMessage(client, message, "Server", True)
			
	#-----------------------------------------------------------------------------------------

	#This function deals with whatever the client does
	def newClient(self, conn, client_address):

		clientWelcomed = False #Only used to welcome the client
		createdClient = False

		while True:
			data = conn.recv(self.ircMessagesLength)
			
			#Decodes the data to make it more readable and splits it by line
			msg = data.decode("utf-8")
			line = msg.split("\r\n")
		
			#Splits the client's address
			clientAddress = str(client_address).split(" ")
			clientAddressSubbed  = re.sub(',', '', clientAddress[1]) #gets rid of the ','

			#creates a new client once for this address
			if not createdClient:
				self.createClient(conn, clientAddressSubbed)
				createdClient = True

			newClient = self.getClient(clientAddressSubbed) #gets the new client for later use
			self.printToServer(newClient, msg)

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