import logging
import time

from communication.sender import Sender
from object_detection.object_detector.object_detector_result import ObjectDetectorResult, DetectedObject
from statemachine.danger_zone import DangerZone
from statemachine.states_nomad import States
from statemachine.steering_command_generator_result import SteeringCommandGeneratorResult, DrivingDirection
from statemachine.transitions_nomad import Transitions
from util.pixel_grid_nomad import PixelGridNomad


class Nomad:
    """
    Model for the StateMachine

    All internal state callbacks (with name prefix '__process_state_') which are executed whenever a new ObjectDetectorResult was received.
    Which callback is executed is depending on the current state (_state) of the state machine.
    """
    _sender: Sender
    _data: ObjectDetectorResult
    _targeted_pylon: DetectedObject
    _pixel_grid: PixelGridNomad = PixelGridNomad()
    _state = None
    _logger = logging.getLogger("NomadModel")

    def _process_state_Start(self):
        """
        State: Start
        :return:
        """
        self._logger.debug("Starting State Machine...")
        self._drive_fictitious_pylon_orbit()
        self.trigger(Transitions.Start_to_DestinationPylonUnknown.name)

    def _process_state_DestinationPylonUnknown(self):
        """
        State: DestinationPylonUnknown
        :return:
        """
        self._scan_for_pylons()

    def _process_state_PylonTargeted(self):
        """
        State: PylonTargeted
        :return:
        """
        self.is_pylon_in_danger_zone()

    def _process_state_TransitEndangered(self):
        """
        State: TransitEndangered
        :return:
        """
        self._drive_towards_targeted_pylon()

    def _process_state_OrbitTargeted(self):
        """
        State: OrbitTargeted
        :return:
        """
        self._drive_towards_targeted_pylon()

    def _process_state_OrbitEntered(self):
        """
        State: OrbitEntered
        :return:
        """
        self._drive_orbit()

    def _process_state_ObstacleDetected(self):
        """
        State: ObstacleDetected
        :return:
        """
        self._align_horizontal_to_obstacle()

    def _scan_for_pylons(self):
        """
        State: DestinationPylonUnknown
        :return:
        """
        if self._data.has_pylons():
            most_right_pylon = self._data.get_most_right_pylon()
            if self._pixel_grid.is_pylon_in_centered_area(most_right_pylon):
                self._logger.debug('Pylon in center found! Initiating transition..')
                self._drive_straight(velocity=2)
                self._targeted_pylon = most_right_pylon
                self.trigger(Transitions.DestinationPylonUnknown_to_PylonTargeted.name)
            else:
                self._logger.debug(
                    f'Pylon detected which should be to the left of the center. Pylon center: {most_right_pylon.bounding_box.center()}.'
                    f'Keep driving on orbit.')
                self._sender.send(py_object=SteeringCommandGeneratorResult(velocity_meters_per_second=1, curve_radius_centimeters=100,
                                                                           driving_direction=DrivingDirection.LEFT))

    def _drive_towards_targeted_pylon(self):
        """
        State: OrbitTargeted, TransitEndangered
        :return:
        """
        # if in state
        self._logger.debug("DRIVING towards targeted pylon....")

        # create thread that contantly checks for the position of the pylon and creates steering command
        # in a way to center the pylon as good as possible

        # another thread (maybe main thread) is checking the distance of the pylon

        if self.state == States.OrbitTargeted.name:
            # drive towards pylon and measure distance
            # watch out for pylons on right side of targeted pylon

            pass
        elif self.state == States.TransitEndangered.name:
            # drive towards pylon
            # measure distance to horizontal axis of pylon in danger zone
            # if obstacle in front of nomad detected and distance < 0.5m
            self.trigger(Transitions.TransitEndangered_to_ObstacleDetected.name)

            # if distance to horizontal axis of pylon in danger zone <=1m do drive_fictitious_pylon_orbit
            if False:
                self._drive_fictitious_pylon_orbit()
                self.trigger(Transitions.TransitEndangered_to_DestinationPylonUnknown.name)
            pass

    def _drive_fictitious_pylon_orbit(self):
        """
        :return:
        """
        self._logger.debug("Driving fictitious pylon orbit")
        self._sender.send(py_object=SteeringCommandGeneratorResult(velocity_meters_per_second=1, curve_radius_centimeters=50,
                                                                   driving_direction=DrivingDirection.RIGHT))
        time.sleep(1)  # TODO: need to figure out how exactly we want to wait until the bigger radius is started. IMU Data? Encoder?
        self._sender.send(py_object=SteeringCommandGeneratorResult(velocity_meters_per_second=1, curve_radius_centimeters=100,
                                                                   driving_direction=DrivingDirection.LEFT))

    def _drive_orbit(self, radius: int):
        """
        State: OrbitEntered
        :return:
        """
        # drive orbit with radius of 1 meter or 0.5 meter depending of measured distance
        # scan for pylon while driving, if one is detected keep driving until it is centered
        # then drive towards pylon
        self.trigger(Transitions.OrbitEntered_to_PylonTargeted.name)
        # if obstacle is detected in front of nomad, goto state obstacle detected
        self.trigger(Transitions.OrbitEntered_to_ObstacleDetected.name)
        # if in next frames pylon to the right side is detected drive fi
        self._drive_fictitious_pylon_orbit()
        self.trigger(Transitions.OrbitEntered_to_DestinationPylonUnknown)
        pass

    def _slow_down(self):
        """
        State: ObstacleDetected
        After detecting an Obstacle Nomad should slow down to a defined speed. Only slow down if
        the max velocity is not already reached.
        :return:
        """
        pass

    def _align_horizontal_to_obstacle(self):
        pass

    def is_pylon_in_danger_zone(self):
        """

        :return:
        """
        # if in danger zone switch to
        self._logger.debug("Is Pylon in danger zone?")
        danger_zone = DangerZone()
        if danger_zone.is_relevant():
            self.trigger(Transitions.PylonTargeted_to_TransitEndangered.name)
        else:
            self.trigger(Transitions.PylonTargeted_to_OrbitTargeted.name)

    def _measure_distance_to_pylon(self):
        """
        State:
        :return:
        """
        # measure distance to pylon
        #
        pass

    def _drive_straight(self, velocity: int):
        self._sender.send(py_object=SteeringCommandGeneratorResult(velocity_meters_per_second=velocity, curve_radius_centimeters=0,
                                                                   driving_direction=DrivingDirection.STRAIGHT))


    @property
    def data(self) -> ObjectDetectorResult:
        return self._data

    @data.setter
    def data(self, current_result: ObjectDetectorResult):
        self._data = current_result

    @property
    def sender(self) -> Sender:
        return self._sender

    @sender.setter
    def sender(self, new_sender: Sender):
        self._sender = new_sender

    @property
    def state(self):
        return self._state

