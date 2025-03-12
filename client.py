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