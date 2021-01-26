from socket import *
import sys #傳arg

tcpSocket = socket(AF_INET,SOCK_STREAM)
tcpSocket.connect((host,port))
tcpSocket.send(sendBuf.encode('utf-8'))
recBuf = tcpSocket.recv(1024).decode('utf-8')