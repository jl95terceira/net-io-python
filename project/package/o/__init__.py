import abc as _abc
import typing as _typing

from .. import (Managed as _Managed, 
                FunctionalManaged as _FunctionalManaged)
from .. import constants as _constants
from .. import util as _util

class OutputStream(_typing.Protocol):

    @_abc.abstractmethod
    def send(self, data:bytes): ...

class FunctionalOutputStream(OutputStream):

    def __init__(self, function:_typing.Callable[[bytes],None]):

        self._function = function

    @_typing.override
    def send(self, data:bytes):

        self._function(data)

class SimpleManagedOutputStream(_Managed[OutputStream]):

    def __init__(self, outs:OutputStream):

        self._outs = outs

    @_typing.override
    def do(self, handler:_typing.Callable[[OutputStream],None]):

        handler.do(self._outs)

class SenderIf[T](_typing.Protocol):

    @_abc.abstractmethod
    def send(self, data:T): ...

class Sender(SenderIf[bytes]):

    def __init__(self, outs:_Managed[OutputStream]):

        self._outs = outs

    def _send_managed(self, outs:OutputStream, data:bytes):

        if len(data) > 0:
            N = (len(data) - 1) // _constants.CONTENT_FRAME_SIZE + 1
            for i in range(N-1):
                sizeFrame    = _constants.SIZE_FRAME_FOR_FULL_CONTENT_FRAME
                contentFrame = data[i* _constants.CONTENT_FRAME_SIZE:(1+i)*_constants.CONTENT_FRAME_SIZE]
                outs.send(_constants.CONTENT_AHEAD_SIGNAL)
                outs.send(sizeFrame)
                outs.send(contentFrame)
            
            lastFrameContentSize = len(data) - (N-1)* _constants.CONTENT_FRAME_SIZE
            lastFrameContentSizeAsBytes = _util.int_to_bytes(lastFrameContentSize)
            sizeFrame = (_constants.SIZE_FRAME_SIZE - len(lastFrameContentSizeAsBytes))*bytes([0]) + lastFrameContentSizeAsBytes
            contentFrame = data[len(data)-lastFrameContentSize:] + (_constants.CONTENT_FRAME_SIZE-lastFrameContentSize)*bytes([0])
            outs.send(_constants.CONTENT_AHEAD_SIGNAL)
            outs.send(sizeFrame)
            outs.send(contentFrame)
            outs.send(_constants.NO_CONTENT_SIGNAL)
        
        else:
            outs.send(_constants.NO_CONTENT_SIGNAL)
        

    @_typing.override
    def send(self, data:bytes):

        self._outs.do(_FunctionalManaged(lambda outs: self._send_managed(outs, data)))

from . import collections
