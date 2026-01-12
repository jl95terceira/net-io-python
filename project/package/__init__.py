import abc as _abc
import typing as _typing

class Managed[T](_typing.Protocol):

    @_abc.abstractmethod
    def do(self, handler:_typing.Callable[[T],None]): ...

class FunctionalManaged[T](Managed[T]):

    def __init__(self, function:_typing.Callable[[_typing.Callable[[T],None]],None]):

        self._function = function

    @_typing.override
    def do(self, handler:_typing.Callable[[T],None]): 

        self._function(handler)


class InputStream(_typing.Protocol):

    @_abc.abstractmethod
    def recv(self, n:int) -> bytes: ...


class FunctionalInputStream(InputStream):

    def __init__(self, function:_typing.Callable[[int],bytes]):

        self._function = function

    @_typing.override
    def recv(self, n:int):

        return self._function(n)


class SimpleManagedInputStream(Managed[InputStream]):

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

    def __init__(self, ins:Managed[InputStream]):

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
                content_parts_list.append(content_frame[:content_size])
            if not continue_loop: break

    @_typing.override
    def recv_while(self, handler:_typing.Callable[[bytes],bool]):

        self._ins.do(lambda ins: self._recv_managed(ins, handler))


class OutputStream(_typing.Protocol):

    @_abc.abstractmethod
    def send(self, data:bytes): ...


class FunctionalOutputStream(OutputStream):

    def __init__(self, function:_typing.Callable[[bytes],None]):

        self._function = function

    @_typing.override
    def send(self, data:bytes):

        self._function(data)


class SimpleManagedOutputStream(Managed[OutputStream]):

    def __init__(self, outs:OutputStream):

        self._outs = outs

    @_typing.override
    def do(self, handler:_typing.Callable[[OutputStream],None]):

        handler(self._outs)


class SenderIf[T](_typing.Protocol):

    @_abc.abstractmethod
    def send(self, data:T): ...


class Sender(SenderIf[bytes]):

    def __init__(self, outs:Managed[OutputStream]):

        self._outs = outs

    def _send_managed(self, outs:OutputStream, data:bytes):

        outs.send(_constants.CONTENT_AHEAD_SIGNAL)
        if len(data) > 0:
            N = (len(data) - 1) // _constants.CONTENT_FRAME_SIZE + 1
            for i in range(N-1):
                size_frame    = _constants.SIZE_FRAME_FOR_FULL_CONTENT_FRAME
                content_frame = data[i* _constants.CONTENT_FRAME_SIZE:(1+i)*_constants.CONTENT_FRAME_SIZE]
                outs.send(_constants.CONTENT_AHEAD_SIGNAL)
                outs.send(size_frame)
                outs.send(content_frame)

            last_frame_content_size = len(data) - (N-1)* _constants.CONTENT_FRAME_SIZE
            last_frame_content_size_as_bytes = _util.int_to_bytes(last_frame_content_size)
            size_frame = (_constants.SIZE_FRAME_SIZE - len(last_frame_content_size_as_bytes))*bytes([0]) + last_frame_content_size_as_bytes
            content_frame = data[len(data)-last_frame_content_size:] + (_constants.CONTENT_FRAME_SIZE-last_frame_content_size)*bytes([0])
            outs.send(size_frame)
            outs.send(content_frame)
        else:
            outs.send(_constants.SIZE_FRAME_FOR_EMPTY_CONTENT_FRAME)
            outs.send(_constants.EMPTY_CONTENT_FRAME)
        outs.send(_constants.NO_CONTENT_SIGNAL)


    @_typing.override
    def send(self, data:bytes):

        self._outs.do(lambda outs: self._send_managed(outs, data))

from . import constants as _constants
from . import util as _util
from . import collections, util