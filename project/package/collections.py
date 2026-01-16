from . import IStream, OStream

import socket as _socket
import typing as _typing


class SimpleSocketIStream(IStream):

    def __init__(self, sock:_socket.socket):

        self._sock = sock

    @_typing.override
    def recv(self, n:int):

        return self._sock.recv(n)
    
    @_typing.override
    def close(self):

        self._sock.close()

class SimpleSocketOStream(OStream):

    def __init__(self, sock:_socket.socket):

        self._sock = sock

    @_typing.override
    def send(self, data:bytes):

        self._sock.sendall(data)
    
    @_typing.override
    def close(self):

        self._sock.close()
