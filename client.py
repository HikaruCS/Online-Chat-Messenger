# TODO: UDPクライアントの実装

import socket
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '127.0.0.1'
server_port = 9001

# 最初にユーザーネームを入力させる
username = input('Enter your username >>> ').strip()  # 余計な空白文字を削除
username_bytes = username.encode('utf-8')
usernamelen = len(username_bytes).to_bytes(1, 'big')

def recieve_messages():
    while True:
        try:
            data, server = sock.recvfrom(4096)

            usernamelen = data[0]
            username_bytes = data[1:1 + usernamelen]
            message_bytes = data[1 + usernamelen:]

            sender_username = username_bytes.decode('utf-8')
            message = message_bytes.decode('utf-8')

            print('\n[{}] {}'.format(sender_username, message))
        except Exception as e:
            print('Error receiving message: {}'.format(e))
            break

# 受信用スレッドを開始
receive_thread = threading.Thread(target=recieve_messages)
receive_thread.start()

# メインスレッドで送信処理
try:
    while True:
        message = input()
        if message.strip().lower() == 'exit':
            break
        message_bytes = message.encode('utf-8')
        packet = usernamelen + username_bytes + message_bytes

        sock.sendto(packet, (server_address, server_port))
except KeyboardInterrupt:
    print('\nClient shutting down...')

sock.close()

class TCPClient:

    # コンストラクタ
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.MAX_ROOM_NAME_BYTE = 2 ** 8
        self.MAX_PAYLOAD_BYTE = 2 ** 29  # payloadはusernameのこと
        self.MAX_TOKEN_BYTE = 255

    # ヘッダ情報をフォーマットする関数
    def protocol_header(room_name, operation, state, operation_payload):
        room_name_size = len(room_name)
        payload_size = len(operation_payload)
        return room_name_size.to_bytes(1, 'big') + operation.to_bytes(1, 'big') + state.to_bytes(1, 'big') + payload_size.to_bytes(29, 'big')
    
    # ユーザー名入力
    def input_username(self):
        username = input('Enter your user name -> ')

        if len(username) > self.MAX_PAYLOAD_BYTE:
            print('User name should be not more than 2^29 bytes. Please try again.')
            self.input_username()
        elif len(username) == 0:
            self.input_username()
        else:
            return username

    # ルーム名を入力
    def input_room_name(self, operation):
        if operation == 1:
            room_name = input('Enter new room name -> ')
            if len(room_name) > self.MAX_ROOM_NAME_BYTE:
                print('Rooom name should be not more than 2^8 bytes. Please try again.')
                self.input_room_name()
            elif len(room_name) == 0:
                self.input_room_name()
            else:
                return room_name
        elif operation == 2:
            room_name = input('Enter a room name that you want to join -> ')
            if len(room_name) > self.MAX_ROOM_NAME_BYTE:
                print('Room name shoudlbe be not more than 2^8 bytes. Please try again.')
                self.input_room_name()
            elif len(room_name) == 0:
                self.input_room_name()
            else:
                return room_name
            
   
    # ここからtcp_main()
    def tcp_main(self):
        print('----- Online Chat Messenger -----')
        print('1. Create a new chat room')
        print('2. Join a chat room')
        operation = ''
        try:
            operation = input('Enter your choice in a number -> ')
        except:
            self.tcp_main()

        user_name = self.input_username()
        room_name = self.input_room_name(operation)
        state = 0

        header = self.protocol_header(room_name, operation, state, user_name)
        body = room_name.encode('utf-8') + user_name.encode('utf-8')
        data = header + body

        self.sock.send(data)
        
        self.sock.recv(4096)
        self.sock.recv(4096)

class UDPClient:
    def __init__(self):
        pass

if __name__ == '__name__':
    server_address = '127.0.0.1'
    tcp_server_port = 9001
    udp_server_port = 9002

    tcp_client = TCPClient(server_address, server_port)