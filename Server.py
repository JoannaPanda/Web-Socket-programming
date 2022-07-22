"""
    Multi-Threaded Server
    Python 3
    Usage: python3 server3.py SERVER_PORT number-of-allowed-failed-consecutive-attempt
    coding: utf-8
    
"""
import json
from socket import *
import string
from datetime import datetime
from threading import Thread
import sys, select
import time

# acquire server host and port from command line parameter
if len(sys.argv) != 3:
    print("\n===== Error usage, python3 Server.py SERVER_PORT number-of-allowed-failed-consecutive-attempt ======\n")
    exit(0)

serverHost = "127.0.0.1"
serverPort = int(sys.argv[1])
allowedFail = int(sys.argv[2])

if not isinstance(serverPort,int):
    print("\n===== SERVER_PORT invalid =====\n")
    exit(0)

if not isinstance(allowedFail,int) or int(sys.argv[2]) not in range(1,5):
    print("\n===== Invalid number of allowed failed consecutive attempt. The valid value of argument number is an integer between 1 and 5 ======\n")
    exit(0)

serverPort = int(sys.argv[1])
allowedFail = int(sys.argv[2])

serverAddress = (serverHost, serverPort)

# define socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)

validCredentials = {}
blockRecord = {}

"""
    Define multi-thread class for client
    This class would be used to define the instance for each connection from each client
    For example, client-1 makes a connection request to the server, the server will call
    class (ClientThread) to define a thread for client-1, and when client-2 make a connection
    request to the server, the server will call class (ClientThread) again and create a thread
    for client-2. Each client will be running in a separate thread, which is the multi-threading
"""
class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False
        
        print("===== New connection created for: ", clientAddress)
        self.clientAlive = True
        
    def run(self):
        message = ''
        
        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.clientSocket.recv(1024)
            message = json.loads(data.decode('utf-8'))
            
            # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            if message == '':
                self.clientAlive = False
                print("===== the user disconnected - ", clientAddress)
                break
            
            # handle message from the client
            if message['requestType'] == 'login':
                print("[recv] New login request")
                self.process_login(message)
            elif message['requestType'] == 'download':
                print("[recv] Download request")
                message = 'download filename'
                print("[send] " + message)
                self.clientSocket.send(message.encode())
            else:
                print("[recv] " + message)
                print("[send] Cannot understand this message")
                message = 'Cannot understand this message'
                self.clientSocket.send(message.encode())
    
    """
    logic for processing user authentication

    """
    def process_login(self, message):

        with open('credentials.txt') as f:
            for line in f.readlines():
                try:
                    (username, password) = line.split(' ')
                    validCredentials[username] = password.strip()
                except:pass

        enteredUsername = message['username']
        enteredPassword = message['password']
        
        # check if entered username is in credentials.txt
        if enteredUsername in validCredentials:
            if enteredUsername in blockRecord:
                currBlock = blockRecord[enteredUsername]
                timeDelta = datetime.now() - currBlock.get('blockTime')
                currBlockNum = currBlock.get('blockNum')
                if currBlockNum >= allowedFail and timeDelta.total_seconds() <= 10:
                    reply = 'Account still blocked'
                    self.clientAlive = False
                elif currBlockNum >= allowedFail and timeDelta.total_seconds() > 10:
                    blockRecord.pop(enteredUsername)
                    if enteredPassword == validCredentials[enteredUsername]:
                        reply = 'Login success'
                    else:
                        reply = 'Invalid Password'
                        blockRecord[enteredUsername] = dict({'blockNum': 1, 'blockTime': datetime.now()})
                elif currBlockNum < allowedFail:
                    reply = 'Invalid Password'
                    blockRecord[enteredUsername] = dict({'blockNum': currBlockNum + 1, 'blockTime': datetime.now()})
                    if currBlockNum + 1 == allowedFail:
                        reply = 'Account blocked'
                        self.clientAlive = False
                    if enteredPassword == validCredentials[enteredUsername]:
                        reply = 'Login success'
                        blockRecord.pop(enteredUsername)
            else:
                if enteredPassword == validCredentials[enteredUsername]:
                        reply = 'Login success'
                else:
                    reply = 'Invalid Password'
                    blockRecord[enteredUsername] = dict({'blockNum': 1, 'blockTime': datetime.now()})
        else:
            reply = 'Username invalid'
        
        
        print('[send] ' + reply)
        self.clientSocket.send(reply.encode('utf-8'))



print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")


while True:
    serverSocket.listen()
    clientSocket, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSocket)
    clientThread.start()
