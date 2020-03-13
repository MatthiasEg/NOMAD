from enum import Enum

from transitions import State


class States(Enum):
    # main states
    Start = 0
    DestinationPylonUnknown = 1
    PylonTargeted = 2
    OrbitTargeted = 3
    OrbitEntered = 4
    TransitEndangered = 5
    ObstacleDetected = 6

    # additional states
    RoadSideOrbitEntered = 7
    RoadSideObstacleDetected = 8
    RoadsideOrbitTargeted = 9


class StatesNomad:
    _states = [
        State(name=States.Start.name),
        State(name=States.DestinationPylonUnknown.name),
        State(name=States.PylonTargeted.name),
        State(name=States.TransitEndangered.name),
        State(name=States.ObstacleDetected.name),
        State(name=States.OrbitTargeted.name),
        State(name=States.OrbitEntered.name),
    ]

    @property
    def states(self):
        return self._states
