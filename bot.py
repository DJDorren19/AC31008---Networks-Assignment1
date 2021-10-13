#!/usr/bin/python3import socket
import socket

server ="127.0.0.1"
port = 6667
channel =""
botnick = "group_11"

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Connecting to " + server)
ircsock.connect((server, port))
