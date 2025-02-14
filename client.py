# TODO: ChatGPTのアドバイスに従いながら、コードを書き進めていく

import socket

# AF_INETを使用し、UDPソケットを作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '192.168.0.38'
server_port = 9001

address = ''
port = 9050

sock.bind((address, port))

username = input('Enter your user name -> ')
message = input(username + ": ")

# ユーザー名とメッセージをバイト列に変換
username_bytes = username.encode('utf-8')
message_bytes = message.encode('utf-8')

usernamelen = len(username_bytes)
usernamelen_byte = usernamelen.to_bytes(1, 'big')

packet = usernamelen_byte + username_bytes + message_bytes

sock.sendto(packet, (server_address, server_port))


        