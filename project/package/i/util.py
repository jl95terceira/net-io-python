import socket as _socket

from . import (ReceiverIf as _ReceiverIf,
               Receiver as _Receiver,
               SimpleManagedInputStream as _SimpleManagedInputStream)
from . import collections as _collections

def receiver_from_socket(sock: _socket.socket):

    return  _Receiver(
        _SimpleManagedInputStream((
            _collections.SimpleSocketInputStream(sock))))
