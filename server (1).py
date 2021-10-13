#!/usr/bin/python3import socket

import socket
import string

####TO DO####
#Allow clients to connect & choose userName and realName
#Allow clients to join channel
#Allow cluents to talk to other users in channel
#Allow clients to talk to eachother in private


####NOTES ON 'PHEUDOCODE'####
#I have now started converting these functions from pheudocode into python
#
#I am still looking into using sockets so haven't fully implemented this yet
#therefor I have labeled the socket sections of the funtions with #SOCKET#

channels = {}       #channel[realName]
users = {}          #user{userName}
connections = {}    #connections[userName]


HOST = '10.0.42.17'
PORT = 6667

    def main():
        test()


    def test():
        print('test')


    def addUser(userName, connection):
        if userName in users:
            print('Username taken')
            #send message to server
            #SOCKET#
            return False

        #add users
        user[userName] = []
        connections[userName] = connections
        return True

        #connect to channel??


    def removeUser():
        if userName in users:
            if users[userName]:
                for channel in users[userName]:
                    disconnectFromChannel(userName, channel)
            del(users[userName])
            del(connections[userName])


    def connectToChannel(userName, realName):
        if userName in users and realName in channels:
            #check if connected
            #else add user to channel
            if (not (userName in channels[realName] and realName in user[userName])):
                users[userName].append(realName)
                channels[realName].append(userName)
                print('connected')

                return True

            else:
                #SOCKET#
                print('failed to connect')



    def disconnectFromChannel():
        #disconect from channel
