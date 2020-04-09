import logging
import time
from threading import Thread
from typing import List

from communication.sender import Sender
from object_detection.object_detector.object_detector_result import ObjectDetectorResult, DetectedObject
from sensors.imu import Imu
from sensors.sonar import Sonar
from statemachine.danger_zone import DangerZone
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
    _pixel_grid: PixelGridNomad = PixelGridNomad()
    _imu: Imu = Imu()
    _obstacle_overcome_thread: Thread
    _sonar: Sonar = Sonar()
    _danger_zone: DangerZone = DangerZone(_pixel_grid)
    _steering_communicator: SteeringCommunicator = SteeringCommunicator()
    _state = None
    _logger = logging.getLogger("NomadModel")

    _targeted_pylon: DetectedObject

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
        self._danger_zone.evaluate_dangerous_pylons(all_pylons=self._data.get_pylons_only(), targeted_pylon=self._targeted_pylon)
        if self._danger_zone.has_dangerous_pylons():
            self._logger.debug("Pylon in Danger Zone!!! Slowing down + transition to TransitEndangered..")
            self._set_velocity(0.5)
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
        self._logger.debug("DRIVING towards targeted pylon....")
        if self._check_for_square_timber_in_front(distance_in_meters=0.5):
            self.trigger(Transitions.OrbitTargeted_to_ObstacleDetected)
            return

        self._update_targeted_pylon()

        if self._danger_zone.number_of_evaluations >= 2:
            # not the first time we entered TransitEndangered without other states in between
            percentage_distance_decrease = self._danger_zone.percentage_distance_decrease_between_first_and_last_evaluation()

            if percentage_distance_decrease >= 0.6:
                self._drive_fictitious_pylon_orbit()
                self.trigger(Transitions.TransitEndangered_to_DestinationPylonUnknown.name)
                return
            elif self._danger_zone.number_of_evaluations > 5:
                self._drive_fictitious_pylon_orbit()
                self.trigger(Transitions.TransitEndangered_to_DestinationPylonUnknown.name)
                return
            else:
                self._danger_zone.evaluate_dangerous_pylons(all_pylons=self.data.get_pylons_only(), targeted_pylon=self._targeted_pylon)
        else:
            self._danger_zone.evaluate_dangerous_pylons(all_pylons=self.data.get_pylons_only(), targeted_pylon=self._targeted_pylon)

    def _process_state_ObstacleDetected(self):
        """
        State: ObstacleDetected
        :return:
        """
        # Only scenario 1 of obstacle handling is implemented for corona situation purposes
        if not self._obstacle_overcome_thread.is_alive():
            # Drive left curve first
            self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=50,
                                             driving_direction=DrivingDirection.RIGHT)
            self.trigger(Transitions.TransitEndangered_to_DestinationPylonUnknown.name)

    def _update_targeted_pylon(self):
        """
        Update targeted pylon according to new data so make sure it's possible to find the targeted pylon in all pylons.
        After declaring a pylon as targeted pylon, we always move straight forward. Means the targeted pylon should still remain in the center.
        :return:
        """
        self._targeted_pylon = self._pixel_grid.most_centered_pylon(self.data.get_pylons_only())

    def _check_for_square_timber_in_front(self, distance_in_meters: float) -> bool:
        if self.data.has_measured_square_timbers():
            if self.data.nearest_square_timber().distance.value < distance_in_meters:
                self._logger.debug('Close square timber detected. Transition to ObstacleDetected..')
                return True
            else:
                return False
        else:
            return False

    def _correct_straight_driving_path(self):
        """
        This method is meant to slightly adjust where NOMAD is driving, when driving towards a pylon which should
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
        pylon_orbit_speed_meters_per_second: float = 1
        distance_to_drive_right_curve_in_meters = 0.61
        self._steering_communicator.send(velocity_meters_per_second=pylon_orbit_speed_meters_per_second, curve_radius_centimeters=50,
                                         driving_direction=DrivingDirection.RIGHT)
        time.sleep(distance_to_drive_right_curve_in_meters/pylon_orbit_speed_meters_per_second)
        self._steering_communicator.send(velocity_meters_per_second=pylon_orbit_speed_meters_per_second, curve_radius_centimeters=100,
                                         driving_direction=DrivingDirection.LEFT)

    def _set_velocity(self, new_velocity_meters_per_second: float):
        """
        State: ObstacleDetected
        After detecting an Obstacle Nomad should slow down to a defined speed. Only slow down if
        the max velocity is not already reached.
        :return:
        """
        self._steering_communicator.send(velocity_meters_per_second=new_velocity_meters_per_second)

    def _get_velocity(self) -> float:
        return self._steering_communicator.last_sent_velocity()

    def before_obstacle(self):
        """
        Is used in 'on_enter' State 'ObstacleDetected'
        :return:
        """
        self._logger.debug('Slowing down before obstacle and setting up gyro checker thread..')
        self._set_velocity(new_velocity_meters_per_second=0.1)
        self._obstacle_overcome_thread = Thread(target=self._check_obstacle_overcome_movement)
        self._obstacle_overcome_thread.setDaemon(True)
        self._obstacle_overcome_thread.start()

    def _check_obstacle_overcome_movement(self):
        self._logger.info("Gyro Thread started")
        pitch_down_noticed: bool = False
        pitch_up_noticed: bool = False

        while pitch_down_noticed is False:
            while pitch_up_noticed:
                gyro_x, _, _ = self._imu.get_gyro()
                if gyro_x >= 10:
                    pitch_up_noticed = True
                    self._logger.info('Pitch up noticed!')
            gyro_x, _, _ = self._imu.get_gyro()
            if gyro_x <= -10:
                pitch_down_noticed = True
                self._logger.info('Pitch down noticed!')

        # Pitch up and down noticed, now check if gyro values remain stable (NOMAD in more or less straight position)
        straight_gyro_x_values: List[float] = []
        while len(straight_gyro_x_values) < 5:
            gyro_x, _, _ = self._imu.get_gyro()
            if -1.5 < gyro_x < 1.5:
                straight_gyro_x_values.append(gyro_x)
        self._logger.info('NOMADs x axis remained straight for 5 times. The obstacle seems to have been overcome.')

    def clear_danger_zone(self):
        """
        Is executed when State 'TransitEndangered' is left by transition.
        :return:
        """
        self._danger_zone.reset()

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
