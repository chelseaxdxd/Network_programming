from socket import *
import sys

port = 8700
host = '127.0.0.1'

#create udp socket
udpSocket = socket(AF_INET, SOCK_DGRAM)
udpSocket.bind((host, port))

while True:
	recBuf,addr = udpSocket.recvfrom(1024)
	recBuf=recBuf.decode('utf-8')
	print('client addr is:', addr)
	print ('Recv UDP:', recBuf )