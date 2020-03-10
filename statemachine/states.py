from enum import Enum


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
