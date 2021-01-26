from socket import *
import sys
import select
class Package:
	def __init__(self, port,fname, udpSocket):
		self.port = port
		self.f = None
		self.fname = fname
		self.udpSocket = udpSocket


host = '127.0.0.1'
CONNECTION_LIST = []
packages = []
num = int(sys.argv[1])
port = int(sys.argv[2])

#create udp socket
for i in range(num):
	udpSocket = socket(AF_INET, SOCK_DGRAM)
	udpSocket.bind((host, port+i))
	CONNECTION_LIST.append(udpSocket)
	file_name = 'temp'
	packages.append(Package(port+i, file_name, udpSocket))




while True:
	read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
	for sock in read_sockets:
		for pack in packages:
			if pack.udpSocket == sock:
				if pack.fname == 'temp':
					recBuf , addr =  sock.recvfrom(1024)
					pack.fname = recBuf.decode('utf-8')
					#f = open(pack.fname, 'wb')
					print(pack.fname)
					
				else:
					recBuf , addr =  sock.recvfrom(1024)
					if recBuf:
						recBuf = recBuf
						f = open(pack.fname, 'wb')
						f.write(recBuf)
						
					else:
						print ("%s Finish!" % pack.fname)
						f.close()


