"""
    Multi-Threaded Server
    Python 3
    Usage: python3 Server.py SERVER_PORT number-of-allowed-failed-consecutive-attempt
    coding: utf-8
    
"""
import json
from socket import *
from datetime import datetime
from threading import Thread
import sys, select

# acquire server host and port from command line parameter
if len(sys.argv) != 3:
    print("\n===== Error usage, python3 Server.py SERVER_PORT number-of-allowed-failed-consecutive-attempt ======\n")
    exit(0)

serverName = gethostname()
serverHost = gethostbyname(serverName)
print("server IP: " + serverHost)
serverPort = int(sys.argv[1])
allowedFail = int(sys.argv[2])

if not isinstance(serverPort,int):
    print("\n===== SERVER_PORT invalid =====\n")
    exit(0)

if not isinstance(allowedFail,int) or int(sys.argv[2]) not in range(1,6):
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
userLog = {}
messageLog = {}
open('userlog.txt', 'w').close()
open('messagelog.txt', 'w').close()

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
            
            
            # handle message from the client
            if message['requestType'] == 'login':
                print(f"[recv] New login request from {message['username']}")
                self.process_login(message)
            elif message['requestType'] == 'BCM':
                print(f"[recv] Broadcast Message request from {message['username']}")
                self.process_bcm(message)
            elif message['requestType'] == 'ATU':
                print(f"[recv] Download Active Users request from {message['username']}")
                self.process_atu(message)
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
        clientUDPport = message['udpPortNum']
        
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
        
        if reply == "Login success":
            userLog[enteredUsername] = dict({'logTimestamp': datetime.now(), 'clientIPaddress': clientAddress[0], 'clientUDPport': clientUDPport})
            userLogFile = open("userlog.txt", 'a')
            numLogs = len(userLog)
            logTimestamp = userLog[enteredUsername].get('logTimestamp').strftime("%d %b %Y %H:%M:%S")
            newLogLine = "{}; {}; {}; {}; {}\n".format(numLogs, logTimestamp,enteredUsername,clientAddress[0],clientUDPport)
            userLogFile.write(newLogLine)
            userLogFile.close()

        print('[send] ' + reply)
        self.clientSocket.send(reply.encode('utf-8'))

    """
    logic for processing BCM command

    """
    def process_bcm(self, message):

        bcm_message = message['message_content']
        enteredUsername = message['username']

        numLogs = len(messageLog)
        messageLog[numLogs] = dict({'logTimestamp': datetime.now(), 'bcm_user': enteredUsername, 'bcm_message': bcm_message})

        messageLogFile = open("messagelog.txt", 'a')
        logTimestamp = messageLog[numLogs].get('logTimestamp').strftime("%d %b %Y %H:%M:%S")
        newLogLine = "{}; {}; {}; {}\n".format(numLogs + 1, logTimestamp,enteredUsername,bcm_message)
        messageLogFile.write(newLogLine)
        messageLogFile.close()

        print_response = "{} broadcasted BCM #{} \"{}\" at {}.".format(enteredUsername, numLogs + 1, bcm_message, logTimestamp)
        print(print_response)

        reply = "Broadcast message, #{} broadcast at {}.".format(numLogs + 1, logTimestamp)
        print('[send] ' + reply)
        self.clientSocket.send(reply.encode('utf-8'))

    """
    logic for processing BCM command

    """
    def process_atu(self, message):

        enteredUsername = message['username']
        print("{} issued ATU command".format(enteredUsername))

        print("Return active user list: ")
        allReply = ""
        for key in userLog:
            if key != enteredUsername:
                activeUser = userLog[key]
                allReply += "{}, {}, {}, active since {}.\n".format(key, activeUser.get('clientIPaddress'), activeUser.get('clientUDPport'), activeUser.get('logTimestamp').strftime("%d %b %Y %H:%M:%S"))

        if allReply == "":
            allReply = "no other active user"  
        print(allReply)

        self.clientSocket.send(allReply.encode('utf-8'))



        



print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")


while True:
    serverSocket.listen()
    clientSocket, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSocket)
    clientThread.start()
