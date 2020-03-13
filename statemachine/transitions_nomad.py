from enum import Enum
from typing import List

from statemachine.states_nomad import States


class Transitions(Enum):
    Start_to_DestinationPylonUnknown = 1
    DestinationPylonUnknown_to_PylonTargeted = 2
    DestinationPylonUnknown_to_ObstacleDetected = 3
    PylonTargeted_to_OrbitTargeted = 4
    PylonTargeted_to_TransitEndangered = 5
    TransitEndangered_to_ObstacleDetected = 6
    TransitEndangered_to_DestinationPylonUnknown = 7
    OrbitTargeted_to_OrbitEntered = 8
    OrbitTargeted_to_DestinationPylonUnknown = 9
    OrbitTargeted_to_ObstacleDetected = 10
    OrbitEntered_to_DestinationPylonUnknown = 11
    OrbitEntered_to_ObstacleDetected = 12
    OrbitEntered_to_PylonTargeted = 13

    # internals
    internal_Start = 14
    internal_DestinationPylonUnknown = 15
    internal_PylonTargeted = 16
    internal_TransitEndangered = 17
    internal_OrbitTargeted = 18
    internal_OrbitEntered = 19


class TransitionsNomad:
    _transitions = [
        {
            'trigger': Transitions.Start_to_DestinationPylonUnknown.name,
            'source': States.Start.name,
            'dest': States.DestinationPylonUnknown.name,
            'conditions': 'is_object_detection_data_available'
        },
        {
            'trigger': Transitions.DestinationPylonUnknown_to_PylonTargeted.name,
            'source': States.DestinationPylonUnknown.name,
            'dest': States.PylonTargeted.name
        },
        {
            'trigger': Transitions.DestinationPylonUnknown_to_ObstacleDetected.name,
            'source': States.DestinationPylonUnknown.name,
            'dest': States.ObstacleDetected.name
        },
        {
            'trigger': Transitions.PylonTargeted_to_OrbitTargeted.name,
            'source': States.PylonTargeted.name,
            'dest': States.OrbitTargeted.name
        },
        {
            'trigger': Transitions.PylonTargeted_to_TransitEndangered.name,
            'source': States.PylonTargeted.name,
            'dest': States.TransitEndangered.name
        },
        {
            'trigger': Transitions.TransitEndangered_to_ObstacleDetected.name,
            'source': States.TransitEndangered.name,
            'dest': States.ObstacleDetected.name
        },
        {
            'trigger': Transitions.TransitEndangered_to_DestinationPylonUnknown.name,
            'source': States.TransitEndangered.name,
            'dest': States.DestinationPylonUnknown.name
        },
        {
            'trigger': Transitions.OrbitTargeted_to_OrbitEntered.name,
            'source': States.OrbitTargeted.name,
            'dest': States.OrbitEntered.name
        },
        {
            'trigger': Transitions.OrbitTargeted_to_DestinationPylonUnknown.name,
            'source': States.OrbitTargeted.name,
            'dest': States.DestinationPylonUnknown.name
        },
        {
            'trigger': Transitions.OrbitTargeted_to_ObstacleDetected.name,
            'source': States.OrbitTargeted.name,
            'dest': States.ObstacleDetected.name
        },
        {
            'trigger': Transitions.OrbitEntered_to_DestinationPylonUnknown.name,
            'source': States.OrbitEntered.name,
            'dest': States.DestinationPylonUnknown.name
        },
        {
            'trigger': Transitions.OrbitEntered_to_ObstacleDetected.name,
            'source': States.OrbitEntered.name,
            'dest': States.ObstacleDetected.name
        },
        {
            'trigger': Transitions.OrbitEntered_to_PylonTargeted.name,
            'source': States.OrbitEntered.name,
            'dest': States.PylonTargeted.name
        },
        # internal transitions (no real transition happening)
        # NOTE: trigger have prefix 'internal_'
        {
            'trigger': Transitions.internal_Start.name,
            'source': States.Start.name,
            'dest': None,
            'after': 'start_state_machine'
        },
        {
            'trigger': Transitions.internal_DestinationPylonUnknown.name,
            'source': States.DestinationPylonUnknown.name,
            'dest': None,
            'after': 'scan_for_pylons'
        },
        {
            'trigger': Transitions.internal_PylonTargeted.name,
            'source': States.PylonTargeted.name,
            'dest': None,
            'after': 'is_pylon_in_danger_zone'
        },
        {
            'trigger': Transitions.internal_TransitEndangered.name,
            'source': States.TransitEndangered.name,
            'dest': None,
            'after': 'drive_towards_targeted_pylon'
        },
        {
            'trigger': Transitions.internal_OrbitTargeted.name,
            'source': States.OrbitTargeted.name,
            'dest': None,
            'after': 'drive_towards_targeted_pylon'
        },
        {
            'trigger': Transitions.internal_OrbitEntered.name,
            'source': States.OrbitEntered.name,
            'dest': None,
            'after': 'drive_orbit'
        }
    ]

    @property
    def transitions(self):
        return self._transitions