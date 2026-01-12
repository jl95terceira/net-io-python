import socket

from project.package import o

sock = socket.socket()
sock.connect(("127.0.0.1",4242,))
print('Connected')
sender = o.util.sender_from_socket(sock)
n_empty = [0]
while True:
    msg = input('>>> ')
    if not msg:
        n_empty[0] += 1
        if (n_empty[0] >= 2):
            break
        continue
    n_empty[0] = 0
    sender.send(msg.encode('utf-8'))
sock.close()
print('Done')
