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
        State(name=States.DestinationPylonUnknown.name, on_enter='clear_danger_zone', on_exit='on_exit_DestinationPylonUnknown'),
        State(name=States.PylonTargeted.name),
        State(name=States.TransitEndangered.name, on_exit='clear_danger_zone'),
        State(name=States.ObstacleDetected.name, on_exit='on_exit_ObstacleDetected'),
        State(name=States.OrbitTargeted.name, on_exit='on_exit_OrbitTargeted'),
        State(name=States.OrbitEntered.name, on_exit='on_exit_OrbitEntered')
    ]

    @property
    def states(self):
        return self._states
