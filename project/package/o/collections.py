import socket as _socket
import typing as _typing

from . import *

class SimpleSocketOutputStream(OutputStream):
    
    def __init__(self, sock:_socket.socket):

        self._sock = sock

    @_typing.override
    def send(self, data:bytes):

        self._sock.sendall(data)
