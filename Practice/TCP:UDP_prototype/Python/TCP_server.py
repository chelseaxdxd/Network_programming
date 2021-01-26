from socket import *
import sys

port = 8700
host = '127.0.0.1'

#create tcp socket
tcpSocket = socket(AF_INET, SOCK_STREAM)
tcpSocket.bind((host, port))
tcpSocket.listen(10)

childSocket,addr = tcpSocket.accept()
print ('New connection :', addr)
_thread.start_new_thread(tcpThread, (childSocket, addr))
recBuf = childSocket.recv(1024).decode('utf-8')
sendBuf = "hi this is TCP server"
childSocket.send(sendBuf.encode('utf-8'))