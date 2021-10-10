#!/usr/bin/python3import socket
import socket

server ="10.0.42.17"
port = 6667
channel =""
botnick = "group_11"

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect(): #connects to the server
    print("Connecting to " + server)
    ircsock.connect((server, port))

def join(): #joins the server channel
    ircsock.send(bytes("JOIN " + channel + "\n", "UTF-8"))

def ping(): #respond to server pings
    ircsock.send(bytes("PONG :pingisin", "UTF-8"))