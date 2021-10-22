#!/usr/bin/python3import socket
import socket
import random
import datetime
import time
import argparse

ircsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

server = "127.0.0.1"
port = 6667
channel = '#test'

botnick = "Bot-Tom"
exitcode = "See you later!" +botnick
users = []
file= 'facts.txt'

parser =argparse.ArgumentParser(description='Bot command line parameters')
parser.add_argument("--hostname", help='Please enter the server the bot should connect to', required=False, default=server)
parser.add_argument("--port", type=int, help="Please enter the port you wish to connect to", required=False, default=port)
parser.add_argument("--name", help="Please enter the name you want to call the Bot", required=False, default=botnick)
parser.add_argument("--channel", help="Please enter the name of the channel you wish to join", required=False, default=channel)


def connect():
        try:
        ircsock.connect((server, port))
    except:
        print("Unable to connect to server. Quitting")
        quit()
    else:
        print("Connecting to server")

    ircsock.send(bytes("USER " + botnick + " " + botnick + " " + botnick + " : Hey there, I'm a bot :-)\r\n", "UTF-8"))
    ircsock.send(bytes("NICK " + botnick + "\r\n", "UTF-8"))
    ircsock.recv(2048, "UTF-8")

def joinchan(chan):
    ircsock.send(bytes("JOIN " + chan + "\r\n", "UTF-8"))
    ircmsg = ""
    ircmsg.find("End of /NAMES list") ==-1
    ircmsg = ircsock.recv(2048).decode("UTF-8")
    ircmsg = ircmsg.strip("\n\r")
    print(ircmsg)

def sendmsg(msg, target= channel):
    ircsock.send(bytes("PRIVMSG "+ target +" :"+msg+"\r\n", "UTF-8"))


def ping():
    ircsock.send(bytes("PONG :pingisn", "UTF-8"))


def fact(filename):
    line = open(filename).read().splitlines()
    return random.choice(line)

def main():
    connect()
    joinchan(channel)

    ircmsg = ircsock.recv(2048).decode("UTF-8")
    ircmsg = ircmsg.strip("\n\r")
    print(ircmsg)

    if ircmsg.find("PRIVMSG") != -1:
        name = ircmsg.strip('!', 1)[0][1:]
        message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]

        if len(name) <17:
            if message.find('!hello') !=-1:
                today = datetime.date.today()
                sendmsg("Hey", name, "the date and time today is: ", today)




