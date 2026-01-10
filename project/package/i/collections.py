import socket as _socket
import typing as _typing

from . import *

class SimpleSocketInputStream(InputStream):
    
    def __init__(self, sock:_socket.socket):

        self._sock = sock

    @_typing.override
    def recv(self, n:int):

        return self._sock.recv(n)
