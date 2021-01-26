from socket import *
import sys #傳arg


def main(host, port):
	
	tcp_connect = 0 #TCP是否還連著
	Num = -1
	#print welcome message
	welcome = '********************************\n'+\
	'** Welcome to the BBS server. **\n'+\
	'********************************'
	print(welcome)
	while True:
		#輸入要發送的訊息
		sendBuf = input('$ ')

		#UDP else TCP
		if sendBuf.startswith("register") or sendBuf.startswith("whoami"):
			if sendBuf.startswith("whoami"):
				sendBuf = ("whoami "+str(Num))

			udpSocket = socket(AF_INET,SOCK_DGRAM)
			udpSocket.sendto(sendBuf.encode('utf-8'), (host,port))
			recBuf,_ = udpSocket.recvfrom(1024)
			recBuf = recBuf.decode('utf-8')
			print(recBuf)
			udpSocket.close()
		else:
			#新連線 重新建立socket
			if(tcp_connect == 0):		
				tcpSocket = socket(AF_INET,SOCK_STREAM)
				tcpSocket.connect((host,port))
				tcp_connect = 1

			#傳接訊息
			tcpSocket.send(sendBuf.encode('utf-8'))
			recBuf = tcpSocket.recv(1024).decode('utf-8')
			if recBuf.startswith("end"):
				tcpSocket.close()
				exit()
			elif recBuf.startswith("Welcome"):
				recBuf_split = recBuf.split()
				Num = recBuf_split[2]
				print(recBuf_split[0],recBuf_split[1])
			else:
				print(recBuf)



if __name__ == '__main__':
	main(str(sys.argv[1]), int(sys.argv[2]))