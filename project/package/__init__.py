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


class IStream(_typing.Protocol):

    @_abc.abstractmethod
    def recv(self, n:int) -> bytes: ...


class FunctionalIStream(IStream):

    def __init__(self, function:_typing.Callable[[int],bytes]):

        self._function = function

    @_typing.override
    def recv(self, n:int):

        return self._function(n)


class SimpleManagedIStream(Managed[IStream]):

    def __init__(self, ins:IStream):

        self._ins = ins

    @_typing.override
    def do(self, handler:_typing.Callable[[IStream],None]):

        handler(self._ins)


class Receiver[T](_typing.Protocol):

    @_abc.abstractmethod
    def recv_while(self, handler:_typing.Callable[[T],bool]): ...

    def _handle_and_continue(self, handler:_typing.Callable[[T],None], data:T):

        handler(data)
        return True

    def recv(self, handler:_typing.Callable[[T],None]):

        return self.recv_while(lambda data: self._handle_and_continue(handler, data))

class IStreamReceiver[T](Receiver[T]):

    @_abc.abstractmethod
    def deserialize(self, data:bytes) -> T: ...

    def __init__(self, ins:Managed[IStream]):

        self._ins = ins

    def _recv_managed(self, ins:IStream, handler:_typing.Callable[[T],bool]):

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
                        continue_loop = handler(self.deserialize(data))
                        if not continue_loop: break
                    continue
                size_frame = ins.recv(_constants.SIZE_FRAME_SIZE)
                content_size = _util.bytes_to_int(size_frame)
                content_frame = ins.recv(_constants.CONTENT_FRAME_SIZE)
                content_parts_list.append(content_frame[:content_size])
            if not continue_loop: break

    @_typing.override
    def recv_while(self, handler:_typing.Callable[[T],bool]):

        self._ins.do(lambda ins: self._recv_managed(ins, handler))

    def adapted[U](self, f:_typing.Callable[[T],U]) -> 'IStreamReceiver[U]':

        parent = self

        class AdaptedReceiver(IStreamReceiver[U]):

            @_typing.override
            def deserialize(self, data:bytes) -> U:

                return f(parent.deserialize(data))

        return AdaptedReceiver(self._ins)

class BytesIStreamReceiver(IStreamReceiver[bytes]):

    @_typing.override
    def deserialize(self, data:bytes) -> bytes:

        return data # as-is

class OStream(_typing.Protocol):

    @_abc.abstractmethod
    def send(self, data:bytes): ...


class FunctionalOStream(OStream):

    def __init__(self, function:_typing.Callable[[bytes],None]):

        self._function = function

    @_typing.override
    def send(self, data:bytes):

        self._function(data)


class SimpleManagedOStream(Managed[OStream]):

    def __init__(self, outs:OStream):

        self._outs = outs

    @_typing.override
    def do(self, handler:_typing.Callable[[OStream],None]):

        handler(self._outs)


class Sender[T](_typing.Protocol):

    @_abc.abstractmethod
    def send(self, data:T): ...


class OStreamSender[T](Sender[T]):

    @_abc.abstractmethod
    def serialize(self, data:T) -> bytes: ...

    def __init__(self, outs:Managed[OStream]):

        self._outs = outs

    def _send_managed(self, outs:OStream, data_:T):
        
        data = self.serialize(data_)
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
            outs.send(_constants.CONTENT_AHEAD_SIGNAL)
            outs.send(size_frame)
            outs.send(content_frame)

        else:

            outs.send(_constants.CONTENT_AHEAD_SIGNAL)
            outs.send(_constants.SIZE_FRAME_FOR_EMPTY_CONTENT_FRAME)
            outs.send(_constants.EMPTY_CONTENT_FRAME)

        outs.send(_constants.NO_CONTENT_SIGNAL)

    @_typing.override
    def send(self, data:T):

        self._outs.do(lambda outs: self._send_managed(outs, data))

    def adapted[U](self, f:_typing.Callable[[U],T]) -> 'OStreamSender[U]':

        parent = self

        class AdaptedSender(OStreamSender[U]):

            @_typing.override
            def serialize(self, data:U) -> bytes:

                return parent.serialize(f(data))

        return AdaptedSender(self._outs)

class BytesOStreamSender(OStreamSender[bytes]):

    @_typing.override
    def serialize(self, data:bytes) -> bytes:

        return data # as-is

from . import constants as _constants
from . import util as _util
from . import collections, util