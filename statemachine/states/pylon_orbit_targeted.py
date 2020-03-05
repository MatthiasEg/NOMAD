from statemachine.state import State
from statemachine.states.pylon_orbit_entered import PylonOrbitEntered


class PylonOrbitTargeted(State):

    def handle1(self) -> None:
        print("ConcreteStateA handles request1.")
        print("ConcreteStateA wants to change the state of the context.")
        self.context.transition_to(PylonOrbitEntered())

    def handle2(self) -> None:
        print("ConcreteStateA handles request2.")
