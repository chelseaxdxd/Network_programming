from socket import *
import sys
import select
import threading,queue
import sqlite3
from sqlite3 import Error
from random import seed
from random import randint
import time
lock = threading.Lock()
class Post:
	def __init__(self, bname, pid, title, username, date, content):
		self.bname = bname
		self.pid = pid
		self.title = title
		self.username = username
		self.date = date
		self.content = content
		self.comments = []
	def add_new_comment(self,name,comment):
		self.comments.append((name,comment))
		#for comment in self.comments:
			#print(comment[0],comment[1])





def tcpThread(childSocket, addr,q,posts):
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
		##list-board
		if recBuf.startswith("list-board"):
			##Index Name Moderator
			conn = sqlite3.connect('store.db')
			c = conn.cursor()
			cursor = c.execute("SELECT * FROM BOARDS").fetchall()
			sendBuf = "{:^7} {:<20} {:<20} \r\n".format("Index", "Name", "Moderator")
			for i in range(len(cursor)):
				sendBuf = sendBuf+ "{:^7} {:<20} {:<20}\r\n".format(i,cursor[i][0], cursor[i][1])
			#i = 1
			#for row in cursor:
			#	sendBuf = sendBuf+ "{:^7} {:<20} {:<20}\r\n".format(i,row[0], row[1])
			#	i = i+1
			childSocket.send(sendBuf.encode('utf-8'))

		##create-post (pid, title, username, date, content)
		if recBuf.startswith("create-post"):
			if login == 0:
				sendBuf = 'Please login first.'
				childSocket.send(sendBuf.encode('utf-8'))
			elif len(recBuf_split) > 5 and TITLE in recBuf and CONTENT in recBuf:
				bname = recBuf_split[1]

				#連接DB
				conn = sqlite3.connect('store.db')
				c = conn.cursor()
				cursor = c.execute("SELECT * FROM BOARDS WHERE Bname = ?",(bname,))
				found = cursor.fetchone()
				#若不存在此 user name
				if found == None:
					sendBuf = 'Board does not exist.'
					childSocket.send(sendBuf.encode('utf-8'))
				else:
					post = recBuf.replace("create-post ", "").replace(bname,"").replace(" --title ","")
					post_split = post.split(" --content ")
					title = post_split[0]
					content = post_split[1]
					date = time.strftime("%m/%d", time.localtime()) ## is a string
					##share memory access
					lock.acquire()
		
					pid = q.get()
					posts.append(Post(bname, pid, title, name, date,content))
					pid=pid+1
					q.put(pid)
					lock.release()

					sendBuf = 'Create post successfully.'
					childSocket.send(sendBuf.encode('utf-8'))

		##list-post <board-name>
		if recBuf.startswith("list-post"):
			if next((post for post in posts if post.bname == recBuf_split[1]), None) == None: ##若沒有找到就回傳none
				sendBuf = 'Board does not exist.'
				childSocket.send(sendBuf.encode('utf-8'))
			else:
				sendBuf = "{:^7} {:^20} {:^20} {:^9}\r\n\r\n".format("S/N", "Title", "Author", "Date")
				for post in posts:
					if post.bname == recBuf_split[1]:
						sendBuf = sendBuf + "{:^7} {:^20} {:^20} {:^9}\r\n\r\n".format(post.pid,post.title, post.username, post.date)
				childSocket.send(sendBuf.encode('utf-8'))

		##read <post-S/N>
		if recBuf.startswith("read"):
			if next((post for post in posts if post.pid == int(recBuf_split[1])), None) == None: ##若沒有找到就回傳none
				sendBuf = 'Post does not exist.'
				childSocket.send(sendBuf.encode('utf-8'))
			else:
				for post in posts:
					if post.pid == int(recBuf_split[1]):
						post.content = post.content.replace("<br>", "\n")
						sendBuf = "Author: "+ post.username + "\nTitle: "+post.title+"\nDate: "+post.date +"\n--\n"+post.content + "\n--\n"
						for comment in post.comments:
							sendBuf = sendBuf + comment[0] + ': '+comment[1]+'\n'
						childSocket.send(sendBuf.encode('utf-8'))

		##comment <post-S/N> <comment> 
		if recBuf.startswith("comment"):
			if login == 0:
				sendBuf = 'Please login first.'
				childSocket.send(sendBuf.encode('utf-8'))
			elif next((post for post in posts if post.pid == int(recBuf_split[1])), None) == None: ##若沒有找到就回傳none
				sendBuf = 'Post does not exist.'
				childSocket.send(sendBuf.encode('utf-8'))
			else:
				for post in posts:
					if post.pid == int(recBuf_split[1]):
						comment = recBuf.replace("comment ", "").replace(str(post.pid)+' ',"")
						print("comment= ",comment)
						post.add_new_comment(name,comment)
						sendBuf = 'Comment successfully.'
						childSocket.send(sendBuf.encode('utf-8'))

		##update-post <post-S/N> --title/content<new>
		#update-post 1 --title NP HW_2
		#(pid, title, username, date, content)
		if recBuf.startswith("update-post"):
			if login == 0:
				sendBuf = 'Please login first.'
				childSocket.send(sendBuf.encode('utf-8'))
			elif next((post for post in posts if post.pid == int(recBuf_split[1])), None) == None: ##若沒有找到就回傳none
				sendBuf = 'Post does not exist.'
				childSocket.send(sendBuf.encode('utf-8'))
			elif next((post for post in posts if post.pid == int(recBuf_split[1]) and post.username == name), None) == None:
				sendBuf = 'Not the post owner.'
				childSocket.send(sendBuf.encode('utf-8'))
			else:
				for i in range(len(posts)):
					if posts[i].pid == int(recBuf_split[1]):
						if recBuf_split[2] == TITLE:
							lock.acquire()
							posts[i].title = recBuf.split("--title ")[1]
							lock.release()
							sendBuf = 'Update successfully'
							childSocket.send(sendBuf.encode('utf-8'))							
						elif recBuf_split[2] == CONTENT:
							lock.acquire()
							posts[i].content = recBuf.split("--content ")[1]
							lock.release()
							sendBuf = 'Update successfully'
							childSocket.send(sendBuf.encode('utf-8'))
						else:
							sendBuf = 'update-post <post-S/N> --title/content<new>'
							childSocket.send(sendBuf.encode('utf-8'))


		##delete-post <post-S/N>
		if recBuf.startswith("delete-post"):
			if login == 0:
				sendBuf = 'Please login first.'
				childSocket.send(sendBuf.encode('utf-8'))
			elif next((post for post in posts if post.pid == int(recBuf_split[1])), None) == None: ##若沒有找到就回傳none
				sendBuf = 'Post does not exist.'
				childSocket.send(sendBuf.encode('utf-8'))
			elif next((post for post in posts if post.pid == int(recBuf_split[1]) and post.username == name), None) == None:
				sendBuf = 'Not the post owner.'
				childSocket.send(sendBuf.encode('utf-8'))
			else:
				for i in range(len(posts)):
					if posts[i].pid == int(recBuf_split[1]):
						del posts[i]
						sendBuf = 'Delete successfully.'
						childSocket.send(sendBuf.encode('utf-8'))
						break
					
				

		##exit
		if recBuf.startswith("exit"):
			sendBuf = 'end'
			childSocket.send(sendBuf.encode('utf-8'))
			childSocket.close()
			break
	
#initial
TITLE = "--title"
CONTENT = "--content"


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
q = queue.Queue()
posts = []
q.put(1)
while True:
	inputready,_,_ = select.select(input,[],[])
	for sck in inputready:
		if sck is tcpSocket:
			childSocket,addr = tcpSocket.accept()
			print ('New connection :', addr)
			t = threading.Thread(target = tcpThread,args= (childSocket, addr,q,posts))
			t.start()
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
