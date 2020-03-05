from statemachine.state import State
from abc import ABC


class StateMachine(ABC):
    _state = None

    def __init__(self, state: State) -> None:
        self.transition_to(state)

    def transition_to(self, state: State):
        """
        The Statemachine allows changing the State object at runtime.
        """

        print(f"Statemachine: Transition to {type(state).__name__}")
        self._state = state

    """
    The Statemachine delegates part of its behavior to the current State object.
    """

    def request1(self):
        self._state.handle1()

    def request2(self):
        self._state.handle2()
