from . import InputStream, OutputStream

import socket as _socket
import typing as _typing


class SimpleSocketInputStream(InputStream):

    def __init__(self, sock:_socket.socket):

        self._sock = sock

    @_typing.override
    def recv(self, n:int):

        return self._sock.recv(n)


class SimpleSocketOutputStream(OutputStream):

    def __init__(self, sock:_socket.socket):

        self._sock = sock

    @_typing.override
    def send(self, data:bytes):

        self._sock.sendall(data)