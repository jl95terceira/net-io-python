import abc as _abc
import typing as _typing

from .. import (Managed as _Managed)
from .. import constants as _constants
from .. import util as _util

class InputStream(_typing.Protocol):

    @_abc.abstractmethod
    def recv(self, n:int) -> bytes: ...

class FunctionalInputStream(InputStream):

    def __init__(self, function:_typing.Callable[[int],bytes]):

        self._function = function

    @_typing.override
    def recv(self, n:int):

        return self._function(n)

class SimpleManagedInputStream(_Managed[InputStream]):

    def __init__(self, ins:InputStream):

        self._ins = ins

    @_typing.override
    def do(self, handler:_typing.Callable[[InputStream],None]):

        handler(self._ins)

class ReceiverIf[T](_typing.Protocol):

    @_abc.abstractmethod
    def recv_while(self, handler:_typing.Callable[[T],bool]): ...

    def _handle_and_continue(self, handler:_typing.Callable[[T],None], data:T):

        handler(data)
        return True

    def recv(self, handler:_typing.Callable[[T],None]):

        return self.recv_while(lambda data: self._handle_and_continue(handler, data))

class Receiver(ReceiverIf[bytes]):

    def __init__(self, ins:_Managed[InputStream]):

        self._ins = ins

    def _recv_managed(self, ins:InputStream, handler:_typing.Callable[[bytes],bool]):

        continue_loop = True
        while True:
            data = None
            content_parts_list:list[bytes] = []
            while True:
                signal = ins.recv(1)
                if signal != _constants.CONTENT_AHEAD_SIGNAL:
                    if content_parts_list:
                        data = b''.join(content_parts_list)
                        content_parts_list = []
                        continue_loop = handler(data)
                        if not continue_loop: break
                    continue
                size_frame = ins.recv(_constants.SIZE_FRAME_SIZE)
                content_size = _util.bytes_to_int(size_frame)
                content_frame = ins.recv(_constants.CONTENT_FRAME_SIZE)
                if content_size > 0:
                    content_parts_list.append(content_frame[:content_size])
            if not continue_loop: break

    @_typing.override
    def recv_while(self, handler:_typing.Callable[[bytes],bool]):

        self._ins.do(lambda ins: self._recv_managed(ins, handler))

from . import collections, util
