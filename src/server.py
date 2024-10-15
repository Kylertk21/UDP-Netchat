'''
CS 3700 - Networking & Distributed Computing - Fall 2024
Instructor: Thyago Mota
Student(s):
Description: Project 1 - Multiuser Chat: Server
'''
import sys
from socket import *
from datetime import datetime

# "constants"
MCAST_ADDR  = '224.1.1.1'
MCAST_PORT  = 2241
SERVER_ADDR = '0.0.0.0'
SERVER_PORT = 4321
BUFFER      = 1024


def broadcast(sock, message, username, mcast_addr):
    sock.sendto(f"{MCAST_ADDR} | <- {message} | {username}".encode(), mcast_addr)
    print(f"Broadcasting: {message}")

if __name__ == '__main__': 
    
    # suggested dictionary to keep track of logged in users
    users = {}
    
    try:
    # TODO #1 create the 2 sockets: one to receive messages from the clients and another one to send messages to the clients (using the mcast group:port); make sure the socket that receives messages is bound to (SERVER_ADDR, SERVER_PORT)
        receive_socket = socket(AF_INET, SOCK_DGRAM)
        receive_socket.bind((SERVER_ADDR, SERVER_PORT))

        send_socket = socket(AF_INET, SOCK_DGRAM)
        send_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        send_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        multicast_addr = (MCAST_ADDR, MCAST_PORT)

        print(f"listening on {SERVER_ADDR}:{SERVER_PORT}")
    
    # TODO #2 implement the communication protocol
        while True:
            data, client_addr = receive_socket.recvfrom(BUFFER)
            message = data.decode()
            print(f"Received message from {client_addr}:{message}")
            command, *args = message.split(',')
            
            if command == 'login':
                username = args[0]
                users[client_addr] = username
                welcome_msg = f"welcome, {username}"
                broadcast(send_socket, welcome_msg, username, multicast_addr)

            elif command == 'list':
                if client_addr in users:
                    if users:
                        user_list = ','.join(users.values())
                        list_msg = f"User list: {user_list}"
                        broadcast(send_socket, list_msg, username, multicast_addr)
                    else:
                        list_msg = "User list empty!"
                        broadcast(send_socket, list_msg, username, multicast_addr)
                else:
                    broadcast(send_socket, f"{client_addr}, you are not logged in. use command login,<username> to log in", username, multicast_addr)

            elif command == 'exit':
                if client_addr in users:
                    username = users[client_addr]
                    del users[client_addr]
                    goodbye_msg = f"goodbye, {username}"
                    broadcast(send_socket, goodbye_msg, username, multicast_addr)
                else:
                    broadcast(send_socket, f"{client_addr}, you are not logged in. use command login,<username> to log in", username, multicast_addr)

            elif command == 'msg':
                if client_addr in users:
                    username = users[client_addr]
                    chat_msg = args[0]
                    broadcast(send_socket, chat_msg, username, multicast_addr)
                else:
                    broadcast(send_socket, f"{client_addr}, you are not logged in. use command login,<username> to log in", username, multicast_addr)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


