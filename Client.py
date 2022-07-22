"""
    Python 3
    Usage: python3 Client.py SERVER_IP SERVER_PORT UDP_PORT
    coding: utf-8

"""
import json
from socket import *
import sys

#Server would be running on the same host as Client
if len(sys.argv) != 4:
    print("\n===== Error usage, python3 Client.py SERVER_IP SERVER_PORT UDP_PORT ======\n")
    exit(0)
serverHost = sys.argv[1]
serverPort = int(sys.argv[2])
udpPort = int(sys.argv[3])
serverAddress = (serverHost, serverPort)

# define a socket for the client side, it would be used to communicate with the server
clientSocket = socket(AF_INET, SOCK_STREAM)

# establish a TCP connection with the server and send message to it
clientSocket.connect(serverAddress)

while True:
    # execute the user authentication process
    print("\n===== Connection built, please proceed to login: =====\n")
    # user input the username and password
    username = input("username: ")
    password = input("password: ")
    logged_in = False
    # authentication message is turned to dict structure
    auth_message = json.dumps(dict({'requestType': 'login', 'username': username,'password': password}))
    
    clientSocket.sendall(auth_message.encode('utf-8'))

    # receive response from the server
    # 1024 is a suggested packet size, you can specify it as 2048 or others
    data = clientSocket.recv(1024)
    login_response = data.decode('utf-8')

    # parse the message received from server and take corresponding actions
    while not logged_in:
        if login_response == "":
            print("[recv] Message from server is empty!")
        elif login_response == "Login success":
            print("[recv] Welcome to TOOM!")
            logged_in = True
        elif login_response == "Account blocked":
            print("[recv] Invalid Password. Your account has been blocked. Please try again later")
            exit()
        elif login_response == "Account still blocked":
            print("[recv] Your account is blocked due to multiple login failures. Please try again later")
            exit()
        elif login_response == "Invalid Password":
            print("[recv] Invalid Password. Please try again!")
            password = input("password: ")
            auth_message = json.dumps(dict({'requestType': 'login', 'username': username,'password': password}))
            clientSocket.sendall(auth_message.encode('utf-8'))

            data = clientSocket.recv(1024)
            login_response = data.decode('utf-8')
        elif login_response == "Username invalid":
            print("[recv] Username invalid. Please try again!")
            username = input("username: ")
            password = input("password: ")
            auth_message = json.dumps(dict({'requestType': 'login', 'username': username,'password': password}))
            clientSocket.sendall(auth_message.encode('utf-8'))

            data = clientSocket.recv(1024)
            login_response = data.decode('utf-8')
        else:
            print("[recv] Message makes no sense")
        
    ans = input('\nDo you want to continue(y/n) :')
    if ans == 'y':
        continue
    else:
        break

# close the socket
clientSocket.close()
