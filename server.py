# TODO: UDPサーバの実装

import socket
import time
import secrets
import threading

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
                    success_response = ('Your request is successfully accepted. Your token is below:').encode('utf-8')
                    connection.send(success_response)
                    print("This client's room: ", room_name)
                    self.room_members_map[room_name].append(token)
                    connection.send(token)
                    state = 2
                    print('Joining the existed room')
        except Exception as e:
            print('Error: ' + str(e))
        finally:
            self.clients_map[token] = [client_address, room_name, username, isHost, None]
            print(self.clients_map)
            connection.close()

    def start(self):
        self.tcp_main()

# ここからUDPサーバ
class UDPServer:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.room_members_map = TCPServer.room_members_map  # {room_name:[token, token, token.....]}
        self.clients_map = TCPServer.clients_map  # {token:[client_address, room_name, palyload(username), isHost(True or False)]}
        self.sock.bind((self.server_address, self.server_port))

    def handle_message(self):
        while True:
            data, client_address = self.sock.recv(4096)
            header = data[:2]
            room_name_size = int.from_bytes(header[:1], 'big')
            token_size = int.from_bytes(header[1:2], 'big')

            body = data[2:]
            room_name = body[:room_name_size].decode('utf-8')
            token = body[room_name_size:room_name_size + token_size]

            if self.clients_map[token][0] != client_address:
                self.clients_map[token[0]] = client_address
            
            else:
                self.clients_map[token][-1] = time.time()  # クライアントの最終送信時刻を追跡
                username = self.clients_map[token][2]
                message = username + ': ' + body[room_name_size + token_size:].decode('utf-8')
                print('Room: {}, User: {}'.format(room_name, username))
                print(message, "\n")
                self.relay_message(room_name, message, token)


    def relay_message(self, room_name, message, token):
        members = self.room_members_map[room_name]

        for member_token in members:
            if token != member_token:
                member_address = self.clients_map[token][0]
                self.sock.sendto(message.encode(), member_address)

    def track_time(self):
        while True:
            time.sleep(60) # 1分ごとにチェック
            INTERVAL = 300  # 5分間アクティブじゃないユーザーは削除

            try:
                for client_token, client_information in self.clients_map.items():
                    if time.time() - client_information[-1] > INTERVAL:
                        belonging_room = client_information[1]
                        deleted_user = client_information[2]

                        # delted_userがホストの場合
                        if client_information[3] == True:
                            notice = 'The host {} left this room'.encode('utf-8')
                            self.relay_message(belonging_room, notice, client_token)
                            self.relay_message(belonging_room, 'Close this room!'.encode('utf-8'), client_token)
                            del self.room_members_map[belonging_room]
                        
                        # その他の場合
                        else:
                            notice = 'Your session is time out'.encode('utf-8')
                            self.sock.sendto(notice, client_information[0])
                            self.sock.sendto('You have to rejoin this room'.encode('utf-8'), client_information[0])
                            user_update_message = "{}'s session is time out and delted from the room".format(client_information[2]).encode('utf-8')
                            self.relay_message(belonging_room, user_update_message, client_token)
                            del self.clients_map[client_token]
            except Exception as e:
                pass

    def start(self):
        thread_main = threading.Thread(target=self.handle_message)
        thread_tracking = threading.Thread(target=self.track_time)
        thread_main.start()
        thread_tracking.start()
        thread_main.join()
        thread_tracking.join()
    
if __name__ == '__main__':
    server_address = '0.0.0.0'
    tcp_server_port = 9001
    udp_server_port = 9002

    tcp_server = TCPServer(server_address, tcp_server_port)
    udp_server = UDPServer(server_address, udp_server_port)

    thread_tcp = threading.Thread(target=tcp_server.start)
    thread_udp = threading.Thread(target=udp_server.start)

    thread_tcp.join()
    thread_udp.join()