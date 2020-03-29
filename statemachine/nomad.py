import logging
import time

from communication.sender import Sender
from object_detection.object_detector.object_detector_result import ObjectDetectorResult, DetectedObject
from statemachine.danger_zone import DangerZone
from statemachine.states_nomad import StatesNomad, States
from statemachine.steering_command_generator_result import DrivingDirection
from statemachine.steering_communicator import SteeringCommunicator
from statemachine.transitions_nomad import Transitions
from util.pixel_grid_nomad import PixelGridNomad, PylonSide


class Nomad:
    """
    Model for the StateMachine

    All internal state callbacks (with name prefix '__process_state_') which are executed whenever a new ObjectDetectorResult was received.
    Which callback is executed is depending on the current state (_state) of the state machine.
    """
    _data: ObjectDetectorResult
    _targeted_pylon: DetectedObject
    _pixel_grid: PixelGridNomad = PixelGridNomad()
    _danger_zone: DangerZone = DangerZone(_pixel_grid)
    _steering_communicator: SteeringCommunicator = SteeringCommunicator()
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

        if self._check_for_square_timber_in_front(0.5):
            self.trigger(Transitions.OrbitEntered_to_ObstacleDetected)
            return

        if self._data.has_pylons():
            most_right_pylon = self._pixel_grid.get_most_right_pylon(self.data.get_pylons_only())
            if self._pixel_grid.is_pylon_in_centered_area(most_right_pylon):
                self._logger.debug('Pylon in center found! Initiating transition..')
                self._drive_straight(velocity=2)
                self._targeted_pylon = most_right_pylon
                self.trigger(Transitions.DestinationPylonUnknown_to_PylonTargeted.name)
            else:
                side: PylonSide = self._pixel_grid.side_of_pylon(most_right_pylon)
                if side == PylonSide.LEFT:
                    self._logger.debug(
                        f'Most right pylon with center \'{most_right_pylon.bounding_box.center()}\' was detected to the left of the center.'
                        f'Keep driving on orbit.')
                    # Following steering command maybe not needed, as we already drive on orbit.
                    self._steering_communicator.send(velocity_meters_per_second=1,
                                                     curve_radius_centimeters=100,
                                                     driving_direction=DrivingDirection.LEFT)
                else:
                    self._logger.debug(
                        f'Most right pylon with center \'{most_right_pylon.bounding_box.center()}\' was detected to the right of the center.'
                        f'This should actually not be possible with our orbit approach.'
                        f'Initiating fictitious pylon orbit..')
                    self._drive_fictitious_pylon_orbit()

    def _process_state_PylonTargeted(self):
        """
        State: PylonTargeted
        :return:
        """
        if self._danger_zone.is_relevant(all_pylons=self._data.get_pylons_only(), targeted_pylon=self._targeted_pylon):
            self._logger.debug("Pylon in Danger Zone!!! Slowing down + transition to TransitEndangered..")
            self._slow_down()
            self.trigger(Transitions.PylonTargeted_to_TransitEndangered.name)
        else:
            self._logger.debug("No Pylon in danger zone, transition to OrbitTargeted..")
            self.trigger(Transitions.PylonTargeted_to_OrbitTargeted.name)

    def _process_state_OrbitTargeted(self):
        """
        State: OrbitTargeted
        :return:
        """
        self._logger.debug("DRIVING towards targeted pylon....")

        if self._check_for_square_timber_in_front(distance_in_meters=0.5):
            self.trigger(Transitions.OrbitTargeted_to_ObstacleDetected)
            return

            # Check if other pylon is available to the right of the targeted pylon
        if self._pixel_grid.has_other_pylons_to_the_right(targeted_pylon=self._targeted_pylon, pylons=self.data.get_pylons_only()):
            self._logger.debug('Found other pylons to the right, while driving towards targeted pylon.'
                               'Starting fictitious pylon orbit and start transition to DestinationPylonUnknown!')
            self._drive_fictitious_pylon_orbit()
            self.trigger(Transitions.OrbitTargeted_to_DestinationPylonUnknown.name)
            return

        # 1. correct driving path. This is quite hard to implement (requires a lot of calculation) and is maybe not needed, as the pylon should be centered already.
        # self._correct_straight_driving_path()

        # 2. check for distance to pylon
        distance_to_targeted_pylon = self._targeted_pylon.distance.value
        if distance_to_targeted_pylon > 150:
            # check next frame for distance
            self._logger.debug(f"Targeted Pylon with distance '{distance_to_targeted_pylon}' is to far way."
                               f" Keep driving straight towards it.")
            return
        elif 141 <= distance_to_targeted_pylon <= 150:
            self._logger.debug(f"Initiating bigger orbit radius of 100cm, because distance to targeted pylon is: '{distance_to_targeted_pylon}'")
            self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=50, driving_direction=DrivingDirection.RIGHT)
            time.sleep(1)  # TODO: Need to estimate how long it takes until the quarter right curve is driven. Race conditions with next frame?!
            self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=100, driving_direction=DrivingDirection.LEFT)
            self.trigger(Transitions.OrbitTargeted_to_OrbitEntered.name)
        elif 91 <= distance_to_targeted_pylon <= 100:
            self._logger.debug(f"Initiating smaller orbit radius of 50cm, because distance to targeted pylon is: '{distance_to_targeted_pylon}'")
            self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=50, driving_direction=DrivingDirection.RIGHT)
            time.sleep(1)  # TODO: Need to estimate how long it takes until the quarter right curve is driven. Race conditions with next frame?!
            self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=50, driving_direction=DrivingDirection.LEFT)
            self.trigger(Transitions.OrbitTargeted_to_OrbitEntered.name)
        else:
            self._logger.debug(f"Distance: '{distance_to_targeted_pylon}' to targeted pylon already to small to drive correct 50cm/100cm orbits!"
                               f" Trying to drive 50cm Orbit anyway!")
            self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=50, driving_direction=DrivingDirection.RIGHT)
            time.sleep(1)  # TODO: Need to estimate how long it takes until the quarter right curve is driven. Race conditions with next frame?!
            self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=50, driving_direction=DrivingDirection.LEFT)
            self.trigger(Transitions.OrbitTargeted_to_OrbitEntered.name)

    def _process_state_OrbitEntered(self):
        """
        State: OrbitEntered
        In this State NOMAD should already be driving with a left curve around the orbit.

        :return:
        """
        # noinspection PyTypeChecker
        self._targeted_pylon = None
        self._logger.debug("Orbit entered. Driving on orbit..")
        self.trigger(Transitions.OrbitEntered_to_DestinationPylonUnknown.name)

    def _process_state_TransitEndangered(self):
        """
        State: TransitEndangered
        :return:
        """
        self._drive_towards_targeted_pylon_endangered()

    def _process_state_ObstacleDetected(self):
        """
        State: ObstacleDetected
        :return:
        """
        self._align_horizontal_to_obstacle()

    def _check_for_square_timber_in_front(self, distance_in_meters: float) -> bool:
        if self.has_square_timbers_in_front_of_nomad():
            if self.data.nearest_square_timber().distance.value < distance_in_meters:
                self._logger.debug('Close square timber detected. Transition to ObstacleDetected..')
                return True
            else:
                return False
        else:
            return False

    def _drive_towards_targeted_pylon_endangered(self):
        # drive towards pylon
        # measure distance to horizontal axis of pylon in danger zone
        # if obstacle in front of nomad detected and distance < 0.5m
        self.trigger(Transitions.TransitEndangered_to_ObstacleDetected.name)

        # if distance to horizontal axis of pylon in danger zone <=1m do drive_fictitious_pylon_orbit
        if False:
            self._drive_fictitious_pylon_orbit()
            self.trigger(Transitions.TransitEndangered_to_DestinationPylonUnknown.name)
        pass

    def _correct_straight_driving_path(self):
        """
        This method is ment to slightely adjust where NOMAD is driving, when driving towards a pylon which should
        already be centered.
        :return:
        """
        x_distance_to_center, y_distance_to_center = self._pixel_grid.distances_to_center(self._targeted_pylon)

        if x_distance_to_center < 0:
            # drive to the right to center the pylon
            # we need some real good calculations to improve performance. Should be done with real world distance and not pixel distance
            if -10 < x_distance_to_center < 0:
                self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=2, driving_direction=DrivingDirection.RIGHT)
            else:
                pass
        else:
            # drive to the left to center the pylon
            # we need some real good calculations to improve performance. Should be done with real world distance and not pixel distance
            self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=2, driving_direction=DrivingDirection.LEFT)

            pass

    def _drive_fictitious_pylon_orbit(self):
        """
        :return:
        """
        self._logger.debug("Driving fictitious pylon orbit")
        self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=50,
                                         driving_direction=DrivingDirection.RIGHT)
        time.sleep(1)  # TODO: need to figure out how exactly we want to wait until the bigger radius is started. IMU Data? Encoder?
        self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=100,
                                         driving_direction=DrivingDirection.LEFT)

    def _slow_down(self):
        """
        State: ObstacleDetected
        After detecting an Obstacle Nomad should slow down to a defined speed. Only slow down if
        the max velocity is not already reached.
        :return:
        """
        self._steering_communicator.send(velocity_meters_per_second=0.5)

    def _align_horizontal_to_obstacle(self):
        pass

    def _drive_straight(self, velocity: int):
        self._steering_communicator.send(velocity_meters_per_second=velocity, curve_radius_centimeters=0, driving_direction=DrivingDirection.STRAIGHT)

    @property
    def data(self) -> ObjectDetectorResult:
        return self._data

    @data.setter
    def data(self, current_result: ObjectDetectorResult):
        self._data = current_result

    def set_sender(self, new_sender: Sender):
        self._steering_communicator.sender = new_sender

    @property
    def state(self):
        return self._state

    def has_square_timbers_in_front_of_nomad(self) -> bool:
        if self.data.has_square_timbers():
            objects_on_track = [square_timber for square_timber in self.data.get_square_timbers_only() if square_timber.distance.measured]
            return len(objects_on_track) != 0
        else:
            return False
