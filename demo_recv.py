import socket

from project.package import i

server = socket.socket()
server.bind(("127.0.0.1",4242,))
print('Bound')
server.listen(1)
sock,addr = server.accept()
server.close()
print('Accepted')
recver = i.Receiver(
    i.SimpleManagedInputStream((
        i.collections.SimpleSocketInputStream(sock))))
def handler(data:bytes):
    print(f'<<< {data.decode('utf-8')}')
recver.recv(handler)
