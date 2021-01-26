from socket import *
import sys
import sqlite3
from sqlite3 import Error
import _thread

port = 8700
host = '127.0.0.1'

def tcpThread(childSocket, addr,uid):
    while True:
        sendBuf=''
        recBuf = childSocket.recv(1024).decode('utf-8')#傳送的訊息是byte，要換成string
        ##list-users
        if recBuf.startswith("list-users"):
            #連接DB
            conn = sqlite3.connect('store.db')
            c = conn.cursor()
            cursor = c.execute("SELECT Username FROM USERS where login != -1").fetchall()
            for row in cursor:
                sendBuf = sendBuf+ "user"+str(row[0])+"\n"
            childSocket.send(sendBuf.encode('utf-8'))
        ##get-ip
        elif recBuf.startswith("get-ip"):
            sendBuf = "IP: "+addr[0]+':' +str(addr[1])
            childSocket.send(sendBuf.encode('utf-8'))

        ##exit
        elif recBuf.startswith("exit"):
            sendBuf = 'Bye, user' +str(uid) +'.'
            print('disconnected')
            childSocket.send(sendBuf.encode('utf-8'))
            childSocket.close()
            break




#initial db

conn = sqlite3.connect('store.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS USERS("  \
        "Username INTEGER NOT NULL,"\
        "IP TEXT NOT NULL,"\
        "Port INTEGER NOT NULL,"\
        "login INTEGER NOT NULL)")
conn.commit()
conn.close()

#inital port
port = int(sys.argv[1])


#create tcp socket
tcpSocket = socket(AF_INET, SOCK_STREAM)
tcpSocket.bind((host, port))
tcpSocket.listen(10)
userTag = 1
while True:
    childSocket,addr = tcpSocket.accept()
    welcome = 'New connection from '+ addr[0]+':' +str(addr[1]) +' user'+str(userTag)
    print (welcome)
    
    #連接DB
    conn = sqlite3.connect('store.db')
    c = conn.cursor()
    cursor = c.execute('INSERT INTO USERS ("Username", "IP", "Port","login") VALUES (?, ?, ?,0)', (userTag , addr[0], addr[1]))
    conn.commit()
    conn.close()
    
    sendBuf = 'Welcome, you are user' +str(userTag) +'.'
    childSocket.send(sendBuf.encode('utf-8'))

    _thread.start_new_thread(tcpThread, (childSocket, addr, userTag))
    userTag = userTag + 1


    


