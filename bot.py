import socket
import time
import datetime
import random
import argparse

ircsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
# server = "fc00:1337::17"
server = "::1"
port = 6667
channel = "#test"
botnick = "Bot-Tom"
exit = "See you later" + botnick
users = []
file = 'randomfacts.txt'

#Command line arguements so users can enter own details
parser = argparse.ArgumentParser(description='Command line parameters')
parser.add_argument("--hostname", help="Please enter the IP address of the server", required=False, default=server)
parser.add_argument("--portnumber", type=int, help="Please enter the port number", required=False, default=port)
parser.add_argument("--channelname", help="Please enter the name of the channel", required=False, default=channel)
parser.add_argument("--botname", help="Please enter the name of the Bot",required=False, default=botnick)

arg = parser.parse_args()
server = arg.hostname
port = arg.portnumber
channel = arg.channelname
botnick = arg.botname

def connect():
    ircsock.connect((server, port))
    ircsock.send(bytes("USER " + botnick + "\r\n", "UTF-8"))
    ircsock.send(bytes("NICK " + botnick + "\r\n", "UTF-8"))
    confirm = ircsock.recv(2048).decode("UTF-8")
    print("connected: " + confirm)


def joinchan(chan):
	print("Joining channel: " + chan)
	ircsock.send(bytes("JOIN " + chan + "\r\n", "UTF-8"))
	confirmJoin = ircsock.recv(2048).decode("UTF-8")
	print("joined: " + confirmJoin)


def ping():  # function that responds to server pongs to help maintain connection to server
    ircsock.send(bytes("PONG :pingisn", "UTF-8"))
    print("Server PONGED")


def sendmsg(msg, target):
    ircsock.send(bytes("PRIVMSG " + target + msg + "\r\n", "UTF-8"))

def randomusr():
    rndusr = random.choice(users)
    return rndusr

def rndfacts(filename):
    line = open(filename).read().splitlines()
    return random.choice(line)


def main():
    connect()
    joinchan(channel)
    while 1:  # effectively infinite while loop to maintain connection
        name = ""
        msg = ""
        org = ""
        
        
        ircmsg = ircsock.recv(2048).decode("UTF-8")
        
        print("MESSAGE: " + ircmsg)
        ircmsg = ircmsg.strip('\r\n')
        print(ircmsg)

        if ircmsg.find("PRIVMSG") !=-1:
          name = ircmsg.split('!')[0][1:]
          msg = ircmsg.split('PRIVMSG', 1)[1].split(':', 1)[1]
          org = ircmsg.split('PRIVMSG', 1)[1].split(' ', 1)[0]
          print(name,org,msg)

        if len(name) < 17:

            if org.lower() == channel.lower():
            
                if msg == "!hello":

                    now = datetime.datetime.now().strftime('%d-%m-%y %H:%M')
                    sendmsg("Hello " + name + " the date and time is" + now+  " ", channel)

            if msg == "!slap":
                slapusr = randomusr()
                sendmsg(" " + slapusr + " was slapped by a trout", channel)

                if msg[:5].find('!tell') != -1:
                	target = msg.split(' ', 1)[1]
                	if target.find(' ') !=-1:
                		msg = target.split(' ',1)[1]
                		target = target.split(' ')[0]

                		sendmsg(msg,target)

            if msg.rstrip() == exit:
                  sendmsg("Quitting bot",channel)
                  ircsock.send(bytes("QUIT \r\n", "UTF-8"))

        if org.lower() == botnick.lower():
            if msg != -1:
                fact = rndfacts(file)
                sendmsg(fact, name)

                if msg.find("PING :") != -1:
                    ping()



main()
