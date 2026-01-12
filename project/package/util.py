from collections import deque as _deque

_ZERO_AS_BYTES = bytes([0])
def int_to_bytes(x:int):

    if x < 0: raise NegativeNumberNotConvertibleToBytes()
    elif x == 0: return _ZERO_AS_BYTES
    bytes_list = _deque()
    n = x
    while n > 0:
        n,q = divmod(n, 256)
        bytes_list.appendleft(q)
    return bytes(bytes_list)

def bytes_to_int(bb:bytes):

    return sum(b*256**(len(bb)-1-i) for i,b in enumerate(bb))

from . import (Receiver as _Receiver, 
               Sender as _Sender, 
               SimpleManagedInputStream as _SimpleManagedInputStream, 
               SimpleManagedOutputStream as _SimpleManagedOutputStream, 
               collections as _collections)
import socket as _socket

class NegativeNumberNotConvertibleToBytes(Exception): pass

def receiver_from_socket(sock: _socket.socket):

    return  _Receiver(
        _SimpleManagedInputStream((
            _collections.SimpleSocketInputStream(sock))))


def sender_from_socket(sock: _socket.socket):

    return  _Sender(
        _SimpleManagedOutputStream((
            _collections.SimpleSocketOutputStream(sock))))
