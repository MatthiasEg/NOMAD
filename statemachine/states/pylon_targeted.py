from statemachine.state import State
from statemachine.states.pylon_orbit_targeted import PylonOrbitTargeted


class PylonTargeted(State):

    def handle1(self) -> None:
        print("ConcreteStateA handles request1.")
        print("ConcreteStateA wants to change the state of the context.")
        self.context.transition_to(PylonOrbitTargeted())

    def handle2(self) -> None:
        print("ConcreteStateA handles request2.")
