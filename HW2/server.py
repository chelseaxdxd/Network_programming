from socket import *
import sys
import select
import _thread
import sqlite3
from sqlite3 import Error
from random import seed
from random import randint

def tcpThread(childSocket, addr):
	# Initialize
	login = 0 ## check login
	name = None
	while True:
		recBuf = childSocket.recv(1024).decode('utf-8')#傳送的訊息是byte，要換成string
		recBuf_split = recBuf.split()

		##login
		if recBuf.startswith("login"):
			if len(recBuf_split) != 3:
				sendBuf = 'Usage: login <username> <password>'
				childSocket.send(sendBuf.encode('utf-8'))
			elif login == 1:
				sendBuf = 'Please logout first.'
				childSocket.send(sendBuf.encode('utf-8'))
			elif len(recBuf_split) == 3:
				name = recBuf_split[1]
				password = recBuf_split[2]
				#連接DB 看user是否存在
				conn = sqlite3.connect('store.db')
				c = conn.cursor()
				cursor = c.execute("SELECT * FROM USERS WHERE username= ?",(name,))
				found = cursor.fetchone()

				if found == None:
					sendBuf = 'Login failed.'
					childSocket.send(sendBuf.encode('utf-8'))
				else:
					if found[1]==name and found[3]==password:
						# seed random number generator
						#seed(1)						
						random = randint(1, 100000)
						cursor = c.execute('UPDATE USERS set RanNum = ? where Username = ?', (random, name))
						conn.commit()
						conn.close()
						login = 1
						sendBuf = 'Welcome, '+ name + ' '+ str(random)
						print(sendBuf)
						childSocket.send(sendBuf.encode('utf-8'))
					else:
						sendBuf = 'Login failed.'
						childSocket.send(sendBuf.encode('utf-8'))
			else: 
				print('error?????')						

		##logout
		if recBuf.startswith("logout"):
			if login == 0:
				sendBuf = 'Please login first.'
				childSocket.send(sendBuf.encode('utf-8'))
			else:
				#連接DB
				conn = sqlite3.connect('store.db')
				c = conn.cursor()
				cursor = c.execute('UPDATE USERS set RanNum = -1 where Username = ?', (name,))
				conn.commit()
				conn.close()
				sendBuf = 'Bye, ' + name
				childSocket.send(sendBuf.encode('utf-8'))
				login = 0
				name = None


		##list-user
		if recBuf.startswith("list-user"):
			#連接DB
			conn = sqlite3.connect('store.db')
			c = conn.cursor()
			cursor = c.execute("SELECT Username, Email FROM USERS").fetchall()
			sendBuf = "{:<20} {:<20} \r\n".format("Name", "Email")
			for row in cursor:
				sendBuf = sendBuf+ "{:<20} {:<20}\r\n".format(row[0], row[1])
			childSocket.send(sendBuf.encode('utf-8'))	

		##create-board
		if recBuf.startswith("create-board"):
			if len(recBuf_split) != 2:
				sendBuf = 'Usage: create-board <name> '
				childSocket.send(sendBuf.encode('utf-8'))
			elif login == 0:
				sendBuf = 'Please login first.'
				childSocket.send(sendBuf.encode('utf-8'))
			else:
				boardname = recBuf_split[1]
				#連接DB
				conn = sqlite3.connect('store.db')
				c = conn.cursor()
				cursor = c.execute("SELECT * FROM BOARDS WHERE Bname = ?",(boardname,))
				found = cursor.fetchone()
				#若不存在此 user name
				if found == None:
					print("here bname = ",boardname,"username = ",name)
					cursor = c.execute('INSERT INTO BOARDS ("Bname", "Username") VALUES (?, ?)', (boardname, name))
					conn.commit()
					conn.close()
					sendBuf = 'Create board successfully.'
					childSocket.send(sendBuf.encode('utf-8'))
				else:
					print("found[0] = ",found[0])
					sendBuf = 'Board already exists.'
					childSocket.send(sendBuf.encode('utf-8'))
					conn.commit()
					conn.close()

		##create-post 
		if recBuf.startswith("create-post"):
			if login == 0:
				sendBuf = 'Please login first.'
				childSocket.send(sendBuf.encode('utf-8'))
			elif len(recBuf_split) > 5 and TITLE in recBuf and CONTENT in recBuf:
				bname = recBuf_split[1]
				post = recBuf.replace("create-post ", "").replace(bname,"").replace(" --title ","")
				post_split = post.split(" --content ")
				title = post_split[0]
				content = post_split[1]

		##exit
		if recBuf.startswith("exit"):
			sendBuf = 'end'
			childSocket.send(sendBuf.encode('utf-8'))
			childSocket.close()
			break
	
#initial
TITLE = " --title "
CONTENT = " --content "

#initial db

conn = sqlite3.connect('store.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS USERS("  \
	  "UID INTEGER PRIMARY KEY AUTOINCREMENT,"\
	  "Username TEXT NOT NULL UNIQUE,"\
	  "Email TEXT NOT NULL,"\
	  "Password TEXT NOT NULL,"\
	  "RanNum INTEGER NOT NULL)")
c.execute("CREATE TABLE IF NOT EXISTS BOARDS("  \
	  "Bname TEXT NOT NULL UNIQUE,"\
	  "Username TEXT NOT NULL)")



conn.commit()
conn.close()

#inital port
port = int(sys.argv[1])

#create tcp socket
tcpSocket = socket(AF_INET, SOCK_STREAM)
tcpSocket.bind(('127.0.0.1', port))
tcpSocket.listen(10)

#create udp socket
udpSocket = socket(AF_INET, SOCK_DGRAM)
udpSocket.bind(('127.0.0.1', port))

input = [tcpSocket,udpSocket]

while True:
	inputready,_,_ = select.select(input,[],[])
	for sck in inputready:
		if sck is tcpSocket:
			childSocket,addr = tcpSocket.accept()
			print ('New connection :', addr)
			_thread.start_new_thread(tcpThread, (childSocket, addr))
		elif sck is udpSocket:
			recBuf,addr = udpSocket.recvfrom(1024)
			recBuf=recBuf.decode('utf-8')
			print('client addr is:', addr)
			print ('Recv UDP:', recBuf )
			

			recBuf_split = recBuf.split()
			

			##register
			if recBuf.startswith("register"):
				print("TEST:",recBuf)
				if len(recBuf_split) == 4:
					#連接DB
					conn = sqlite3.connect('store.db')
					c = conn.cursor()
					cursor = c.execute("SELECT * FROM USERS WHERE username= ?",(recBuf_split[1],))
					found = cursor.fetchone()

					#若不存在此 user name
					if found == None:
						cursor = c.execute('INSERT INTO USERS ("Username", "Email", "Password", "RanNum") VALUES (?, ?, ?, -1)', (recBuf_split[1], recBuf_split[2], recBuf_split[3]))
						conn.commit()
						conn.close()
						sendBuf = 'Register successfully.'
						udpSocket.sendto(sendBuf.encode('utf-8'), addr)
					else:
						sendBuf = 'Username is already used.'
						udpSocket.sendto(sendBuf.encode('utf-8'), addr)
				else:
					sendBuf = 'Usage: register <username> <email> <password>'
					udpSocket.sendto(sendBuf.encode('utf-8'), addr)

			##whoami
			elif recBuf.startswith("whoami"):
				if len(recBuf_split) == 2:
					if recBuf_split[1] == str(-1):
						sendBuf = 'Please login first.'
						udpSocket.sendto(sendBuf.encode('utf-8'), addr)
					else:
						random = recBuf_split[1]
						#連接DB
						conn = sqlite3.connect('store.db')
						c = conn.cursor()
						cursor = c.execute("SELECT username FROM USERS WHERE RanNum= ?",(random,))
						found = cursor.fetchone()
						conn.commit()
						conn.close()
						sendBuf = found[0]
						udpSocket.sendto(sendBuf.encode('utf-8'), addr)
		