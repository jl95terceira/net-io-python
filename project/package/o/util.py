import socket as _socket

from . import (SenderIf as _SenderIf,
               Sender as _Sender,
               SimpleManagedOutputStream as _SimpleManagedOutputStream)
from . import collections as _collections

def sender_from_socket(sock: _socket.socket):

    return  _Sender(
        _SimpleManagedOutputStream((
            _collections.SimpleSocketOutputStream(sock))))