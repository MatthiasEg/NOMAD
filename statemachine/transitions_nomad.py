from enum import Enum

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
    ObstacleDetected_to_DestinationPylonUnknown = 14
    ObstacleDetected_to_OrbitEntered = 15

    # internals starting value 50 upwards
    internal_Start = 50
    internal_DestinationPylonUnknown = 51
    internal_PylonTargeted = 52
    internal_TransitEndangered = 53
    internal_OrbitTargeted = 54
    internal_OrbitEntered = 55
    internal_ObstacleDetected = 56


class TransitionsNomad:
    _transitions = [
        {
            'trigger': Transitions.Start_to_DestinationPylonUnknown.name,
            'source': States.Start.name,
            'dest': States.DestinationPylonUnknown.name
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
            'trigger': Transitions.TransitEndangered_to_DestinationPylonUnknown.name,
            'source': States.TransitEndangered.name,
            'dest': States.DestinationPylonUnknown.name
        },
        {
            'trigger': Transitions.TransitEndangered_to_ObstacleDetected.name,
            'source': States.TransitEndangered.name,
            'dest': States.ObstacleDetected.name
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
        {
            'trigger': Transitions.OrbitEntered_to_PylonTargeted.name,
            'source': States.OrbitEntered.name,
            'dest': States.PylonTargeted.name
        },
        {
            'trigger': Transitions.ObstacleDetected_to_DestinationPylonUnknown.name,
            'source': States.ObstacleDetected.name,
            'dest': States.DestinationPylonUnknown.name
        },
        {
            'trigger': Transitions.ObstacleDetected_to_OrbitEntered.name,
            'source': States.ObstacleDetected.name,
            'dest': States.OrbitEntered.name
        },

        # internal transitions (no real transition happening)
        # NOTE: trigger have prefix 'internal_'
        {
            'trigger': Transitions.internal_Start.name,
            'source': States.Start.name,
            'dest': None,
            'after': '_process_state_Start'
        },
        {
            'trigger': Transitions.internal_DestinationPylonUnknown.name,
            'source': States.DestinationPylonUnknown.name,
            'dest': None,
            'after': '_process_state_DestinationPylonUnknown'
        },
        {
            'trigger': Transitions.internal_PylonTargeted.name,
            'source': States.PylonTargeted.name,
            'dest': None,
            'after': '_process_state_PylonTargeted'
        },
        {
            'trigger': Transitions.internal_TransitEndangered.name,
            'source': States.TransitEndangered.name,
            'dest': None,
            'after': '_process_state_TransitEndangered'
        },
        {
            'trigger': Transitions.internal_OrbitTargeted.name,
            'source': States.OrbitTargeted.name,
            'dest': None,
            'after': '_process_state_OrbitTargeted'
        },
        {
            'trigger': Transitions.internal_OrbitEntered.name,
            'source': States.OrbitEntered.name,
            'dest': None,
            'after': '_process_state_OrbitEntered'
        },
        {
            'trigger': Transitions.internal_ObstacleDetected.name,
            'source': States.ObstacleDetected.name,
            'dest': None,
            'before': '_slow_down',
            'after': '_process_state_ObstacleDetected'
        }
    ]

    @property
    def transitions(self):
        return self._transitions
