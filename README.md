Zoom and Microsoft Teams are widely used as a method for large groups of people to hold online 
virtual meetings. A good example is the online Zoom lectures used for various courses at UNSW. In
this assignment, you will have the opportunity to implement your own version of an online video
conferencing and messaging application. Your application is based on a client-server model 
consisting of one server and multiple clients communicating concurrently. The text messages should
be communicated using TCP for the reason of reliability, while the video (you will use video files
instead of capturing the live video streams from cameras and microphones) should be communicated
using UDP for the reason of low latency. Your application will support a range of functions that are 
typically found on videoconferencing including authentication, broadcasting text messages to all
participants, building a separate room for part of the participants, and uploading video streams (i.e., 
files in this assignment). You will be designing custom application protocols based on TCP and UDP.

1.1 Learning Objectives
On completing this assignment, you will gain sufficient expertise in the following skills:
1. Detailed understanding of how client-server and client-client interactions work.
2. Expertise in socket programming.
3. Insights into designing and implementing an application layer protocol.

Implement the client and server programs of a video 
conference application, similar in many ways to the Zoom application that we use for this course. The 
difference is that your application won’t capture and display live videos; instead, it will transmit and
receive video files. The text messages must communicate over TCP to the server, while the clients 
communicate video files in UDP themselves. Your application will support a range of operations
including authenticating a user, posting a message to the server, sending a private message to another
particular participant, reading messages from the server, reading active users’ information, and
uploading video files from one user to another user. You will implement the
application protocol to implement these functions. The server will listen on a port specified as the 
command line argument and will wait for a client to connect. The client program will initiate a TCP 
connection with the server. Upon connection establishment, the user will initiate the authentication 
process. The client will interact with the user through the command-line interface. Following
successful authentication, the user will initiate one of the available commands. All commands require 
a simple request-response interaction between the client and server or two clients. The user may execute a series of commands (one after the other) and eventually quit. Both the
client and server MUST print meaningful messages at the command prompt that capture the specific
interactions taking place. You are free to choose the precise text that is displayed.
