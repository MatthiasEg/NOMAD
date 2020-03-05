import statemachine.statemachine as Context
from abc import ABC, abstractmethod


class State(ABC):


    def __init__(self) -> None:
        self._context = Context


    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    @abstractmethod
    def handle1(self) -> None:
        pass

    @abstractmethod
    def handle2(self) -> None:
        pass
