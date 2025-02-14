import socket
import time

# AF_INETを使って、UDPソケットを作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '0.0.0.0'
server_port = 9001
print('starting up on port {}'.format(server_port))

sock.bind((server_address, server_port))

clients = {}

def cleanup_clients():
    TIMEOUT = 300

    now = time.time()
    to_remove = [address for address, last_active in clients.items() if now - last_active > TIMEOUT]

    for address in to_remove:
        del clients[address]

last_cleanup = time.time()
CLEANUP_INTERVAL = 10 # 10秒ごとにクリーンアップ

while True:
    try:
        data, address = sock.recvfrom(4096)

        if len(data) < 2 or len(data) < 1 + data[0]:
            print('Received malformed packet from {}'.format(address))

        usernamelen = data[0]
        username_bytes = data[1: 1+ usernamelen]
        message_bytes = data[1+ usernamelen:]

        username = username_bytes.decode()
        message = message_bytes.decode()

        clients[address] = time.time()

        print('[{}] {}'.format(username, message))

        for client_address in clients:
            if client_address != address:
                sock.sendto(data, client_address)

        if time.time() - last_cleanup > CLEANUP_INTERVAL:
            cleanup_clients()
            last_cleanup = time.time()
    
    except KeyboardInterrupt:
        print('\nServer shutting down')
        break

sock.close()