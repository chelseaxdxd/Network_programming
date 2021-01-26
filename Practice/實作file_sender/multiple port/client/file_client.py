from socket import *
import sys
import os
import time

host = sys.argv[1]
port = int(sys.argv[2])
filename = sys.argv[3]
udpSocket = socket(AF_INET,SOCK_DGRAM)
udpSocket.sendto(filename.encode('utf-8'), (host,port))#先傳file name

f = open(filename, 'rb')
data = f.read(1024)
while(data):
	if(udpSocket.sendto(data, (host,port))):
		data = f.read(1024)
		time.sleep(0.02) # Give receiver a bit time to save
udpSocket.sendto(('').encode('utf-8'), (host,port))
f.close		
udpSocket.close()


