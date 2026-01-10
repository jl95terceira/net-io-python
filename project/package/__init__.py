import abc as _abc
import typing as _typing

class Managed[T](_typing.Protocol):

    @_abc.abstractmethod
    def do(self, handler:_typing.Callable[[T],None]): ...

class FunctionalManaged[T](_typing.Protocol):

    def __init__(self, function:_typing.Callable[[_typing.Callable[[T],None]],None]):

        self._function = function

    @_typing.override
    def do(self, handler:_typing.Callable[[T],None]): 

        self._function(handler)

