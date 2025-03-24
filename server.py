# TODO: UDPサーバの実装

import socket
import time
import secrets

# socketを作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '0.0.0.0'
server_port = 9001

sock.bind((server_address, server_port))

# clientのアドレス(key)とその最新メッセージ送信時刻(value)を保存するディクショナリ
clients = {}

def cleanup_client():
    INTERVAL = 30
    current_time = time.time()

    to_remove = [address for address, last_active in clients.items() if current_time - last_active > INTERVAL]

    for address in to_remove:
        del clients[address]

last_cleanup = time.time()
CLENUP_INTERVAL = 10

while True:
    try:
        data, address = sock.recvfrom(4096)

        usernamelen = data[0]
        username_bytes = data[1:1 + usernamelen]
        message_bytes = data[1 + usernamelen:]

        username = username_bytes.decode('utf-8')
        message = message_bytes.decode('utf-8')

        clients[address] = time.time()

        print('[{}] {}'.format(username, message))

        for client_address in clients:
            if client_address != address:
                sock.sendto(data, client_address)

        if time.time() - last_cleanup > CLENUP_INTERVAL:
            cleanup_client()
            last_cleanup = time.time()
    
    except KeyboardInterrupt:
        print("\nServer shutting down...")
        break

sock.close()


class TCPServer:

    room_members_map = {}  # {room_name:[token, token, token.....]}
    clients_map = {}  # {token:[client_address, room_name, palyload(username), isHost(True or False)]}

    # コンストラクタ
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.server_address, self.server_port))
        self.MAX_HEADER_SIZE = 32
        self.MAX_TOKEN_SIZE = 255

    def tcp_main(self):
        self.sock.listen()

        try:
            while True:
                connection, client_address = self.sock.accept()
                print('connection from ', client_address)

                data = connection.recev(4096)  # header + body

                # header部分
                header = connection.recv(self.MAX_HEADER_SIZE)
                room_name_size = int.to_bytes(header[:1], 'big')
                operation = int.to_bytes(header[1:2], 'big')
                state = int.to_bytes(header[2:3], 'big')
                operation_payload_size = int.to_bytes(header[3:], 'big')

                # body部分
                body = data[self.MAX_HEADER_SIZE:]
                room_name = body[:room_name_size].decode('utf-8')
                username = body[room_name_size:room_name_size + operation_payload_size].decode('utf-8')

                print('room name: ', room_name)
                print('user name: ', username)

                token = secrets.token_bytes(self.MAX_TOKEN_SIZE)

                # 新しいチャットルームを作成()
                if operation == 1:
                    isHost = True
                    state = 1
                    success_response = (room_name + ' is successfully created.').encode('utf-8')
                    connection.send(success_response)
                    token_response = ('Your token for this room is:').encode('utf-8')
                    connection.send(token_response)
                    connection.send(token)
                    self.room_members_map[room_name] = [token]
                    state = 2
                    print('Create a new chat room (Host: {})'.format(username))
                # 既存のルームに参加
                elif operation == 2:
                    isHost = False
                    state = 1
                    success_response = ('You can enter the room by the token below:')
                    connection.send(success_response)
                    print("This client's room: ", room_name)
                    self.room_members_map[room_name].append(token)
                    connection.send(token)
                    state = 2
                    print('Join the existed room')
        except Exception as e:
            print('Error: ' + str(e))
        finally:
            self.clients_map[token] = [client_address, room_name, username, isHost]

    def tcp_start(self):
        self.tcp_main()

# ここからUDPサーバ
class UDPServer:
    def __init__(self):
        pass