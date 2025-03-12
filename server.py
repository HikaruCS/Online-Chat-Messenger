# TODO: ステージ2に取り掛かる

import socket
import time

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