import socket

from project.package import util

server = socket.socket()
server.bind(("127.0.0.1",4242,))
print('Bound')
server.listen(1)
recv = util.receiver_from_socket(server.accept()[0])
print('Accepted')
server.close()
def handler(data:bytes):
    print(f'<<< {data.decode('utf-8')}')
try:
    recv.recv(handler)
except KeyboardInterrupt:
    pass
recv.close()
print('Done.')
