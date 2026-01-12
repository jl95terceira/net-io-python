import socket

from project.package import i

server = socket.socket()
server.bind(("127.0.0.1",4242,))
print('Bound')
server.listen(1)
sock,addr = server.accept()
server.close()
print('Accepted')
recv = i.util.receiver_from_socket(sock)
def handler(data:bytes):
    print(f'<<< {data.decode('utf-8')}')
recv.recv(handler)
