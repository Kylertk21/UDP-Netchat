from socket import socket, AF_INET, SOCK_DGRAM

SERVER_ADDR = 'server'
SERVER_PORT = 4321
MESSAGE = b'TEST'

client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.sendto(MESSAGE, (SERVER_ADDR, SERVER_PORT))
print("sent!")
