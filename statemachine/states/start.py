from statemachine.state import State
from statemachine.states.destination_pylon_unknown import DestinationPylonUnknown


class Start(State):

    def handle1(self) -> None:
        print("ConcreteStateA handles request1.")
        print("ConcreteStateA wants to change the state of the context.")
        self.context.transition_to(DestinationPylonUnknown())

    def handle2(self) -> None:
        print("ConcreteStateA handles request2.")
