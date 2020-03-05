from statemachine.state import State
from statemachine.states.pylon_targeted import PylonTargeted


class DestinationPylonUnknown(State):

    def handle1(self) -> None:
        print("ConcreteStateA handles request1.")
        print("ConcreteStateA wants to change the state of the context.")
        self.context.transition_to(PylonTargeted())

    def handle2(self) -> None:
        print("ConcreteStateA handles request2.")
