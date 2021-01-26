from socket import *
import sys
port = 8700
host = '127.0.0.1'

while True:
		#輸入要發送的訊息
		sendBuf = input('$ ')
		udpSocket = socket(AF_INET,SOCK_DGRAM)
		udpSocket.sendto(sendBuf.encode('utf-8'), (host,port))
		recBuf, address = udpSocket.recvfrom(1024)
		recBuf = recBuf.decode('utf-8')
		print(recBuf, address)
		udpSocket.close()