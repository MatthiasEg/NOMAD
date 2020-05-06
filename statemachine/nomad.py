import datetime
import logging
import time
from threading import Thread
from typing import List

from communication.sender import Sender
from imu_sensorinput.read_fake_imu import ReadIMU, IMUData
from object_detection.object_detector.object_detector_result import ObjectDetectorResult, DetectedObject
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
    _IMU_data: IMUData
    _pixel_grid: PixelGridNomad = PixelGridNomad()
    _obstacle_overcome_thread: Thread
    _danger_zone: DangerZone = DangerZone(_pixel_grid)
    _steering_communicator: SteeringCommunicator = SteeringCommunicator()
    _state = None
    _logger = logging.getLogger("NomadModel")
    _targeted_pylon: DetectedObject

    # Start variables
    _start_time = 0
    _start_scene_completed = False
    _fictitious_pylon_orbit_waiting_time_right_curve = 5  # seconds

    # DestinationPylonUnknown variables
    _should_drive_fictitious_pylon_orbit = False

    # OrbitTargeted variables
    _orbit_targeted_time_first_command = 0
    _last_distance_targeted_pylon = 0

    # OrbitEntered variables
    _orbit_entered_enter_time = 0

    # ObstacleDetected variables
    _pitch_down_noticed: bool = False
    _pitch_up_noticed: bool = False
    _straight_gyro_x_values: List[float] = []

    def _process_state_Start(self):
        """
        State: Start
        :return:
        """
        self._logger.debug("Starting State Machine...")
        self._drive_fictitious_pylon_orbit()
        self._start_time = time.time()
        self.trigger(Transitions.Start_to_DestinationPylonUnknown.name)

    def _process_state_DestinationPylonUnknown(self):
        """
        State: DestinationPylonUnknown
        :return:
        """
        # Hack to drive fictitious pylon orbit correctly at the beginning
        if not self._start_scene_completed:
            current_time = time.time()
            if current_time < self._start_time + self._fictitious_pylon_orbit_waiting_time_right_curve:
                self._steering_communicator.resend_last_steering_command(new_state=self._state)
                return
            else:
                self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=100,
                                                 driving_direction=DrivingDirection.LEFT, state_nomad=self._state)
                self._start_scene_completed = True
                return

        if self._check_for_square_timber_in_front(distance_in_centimeters=50):
            self.trigger(Transitions.DestinationPylonUnknown_to_ObstacleDetected.name)
            return

        if self._data.has_pylons():
            self._logger.debug('Pylon detected! Checking for position..')
            most_right_pylon = self._pixel_grid.get_most_right_pylon(self.data.get_pylons_only())
            if self._pixel_grid.is_pylon_in_centered_area(most_right_pylon):
                self._logger.debug('Pylon in center found! Initiating transition..')
                self._drive_straight(velocity=2)
                self.targeted_pylon = most_right_pylon
                self.trigger(Transitions.DestinationPylonUnknown_to_PylonTargeted.name)
            else:
                side: PylonSide = self._pixel_grid.side_of_pylon(most_right_pylon)
                if side == PylonSide.LEFT:
                    self._logger.debug(
                        f'Most right pylon with center \'{most_right_pylon.bounding_box.center()}\' was detected to the left of the center.'
                        f'Keep driving on orbit.')
                    # Following steering command maybe not needed, as we already drive on orbit.
                    if self._steering_communicator.last_sent_curve_radius() == 50 and not self._should_drive_fictitious_pylon_orbit:
                        self._steering_communicator.send(velocity_meters_per_second=1,
                                                         curve_radius_centimeters=50,
                                                         driving_direction=DrivingDirection.LEFT,
                                                         state_nomad=self._state)
                    else:
                        self._steering_communicator.send(velocity_meters_per_second=1,
                                                         curve_radius_centimeters=100,
                                                         driving_direction=DrivingDirection.LEFT,
                                                         state_nomad=self._state)
                else:
                    self._logger.debug(
                        f'Most right pylon with center \'{most_right_pylon.bounding_box.center()}\' was detected to the right of the center.'
                        f'This should actually not be possible with our orbit approach.'
                        f'Initiating fictitious pylon orbit..')
                    self._drive_fictitious_pylon_orbit()
        else:
            self._logger.debug('No pylons seen! '
                               'Remain in State DestinationPylonUnknown..')
            self._steering_communicator.resend_last_steering_command(new_state=self._state)

    def _process_state_PylonTargeted(self):
        """
        State: PylonTargeted
        :return:
        """
        self._update_targeted_pylon()
        self._danger_zone.evaluate_dangerous_pylons(all_pylons=self._data.get_pylons_only(), targeted_pylon=self._targeted_pylon)
        if self._danger_zone.has_dangerous_pylons():
            self._logger.debug("Pylon in Danger Zone!!!")
            self._steering_communicator.send(velocity_meters_per_second=1,
                                             state_nomad=self._state)
            self.trigger(Transitions.PylonTargeted_to_TransitEndangered.name)
        else:
            self._logger.debug("No Pylon in danger zone, transition to OrbitTargeted..")
            self._steering_communicator.resend_last_steering_command(new_state=self._state)
            self.trigger(Transitions.PylonTargeted_to_OrbitTargeted.name)

    def _process_state_OrbitTargeted(self):
        """
        State: OrbitTargeted
        :return:
        """
        self._logger.debug("DRIVING towards targeted pylon....")

        if self._check_for_square_timber_in_front(distance_in_centimeters=50):
            self.trigger(Transitions.OrbitTargeted_to_ObstacleDetected.name)
            return

        # Update targeted pylon
        self._update_targeted_pylon()

        # Check if other pylon is available to the right of the targeted pylon
        if self._pixel_grid.has_other_pylons_to_the_right(targeted_pylon=self._targeted_pylon, pylons=self.data.get_pylons_only()):
            self._logger.debug('Found other pylons to the right, while driving towards targeted pylon.'
                               'Starting fictitious pylon orbit and start transition to DestinationPylonUnknown!')
            self._drive_fictitious_pylon_orbit()
            self.trigger(Transitions.OrbitTargeted_to_DestinationPylonUnknown.name)
            return

        # Hack to make sure steering commands are sent to visualizer all the time during OrbitTargeted to ensure good looking visualization
        time_to_drive_right_curve = 2  # seconds
        if self._orbit_targeted_time_first_command != 0:
            current_time = time.time()
            if current_time < (self._orbit_targeted_time_first_command + time_to_drive_right_curve):
                self._steering_communicator.resend_last_steering_command(new_state=self._state)
                return
            else:
                if 141 <= self._last_distance_targeted_pylon <= 150:
                    self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=100,
                                                     driving_direction=DrivingDirection.LEFT,
                                                     state_nomad=self._state)
                    self.trigger(Transitions.OrbitTargeted_to_OrbitEntered.name)
                    return

                else:
                    self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=50,
                                                     driving_direction=DrivingDirection.LEFT,
                                                     state_nomad=self._state)
                    self.trigger(Transitions.OrbitTargeted_to_OrbitEntered.name)
                    return

        # Check for distance to targeted pylon
        distance_to_targeted_pylon = self._targeted_pylon.distance.value

        if distance_to_targeted_pylon > 150:
            # check next frame for distance
            self._logger.debug(f"Targeted Pylon with distance '{distance_to_targeted_pylon}' is to far way."
                               f" Keep driving straight towards it.")
            self._steering_communicator.resend_last_steering_command(new_state=self.state)
            self._last_distance_targeted_pylon = distance_to_targeted_pylon
        elif 141 <= distance_to_targeted_pylon <= 150:
            self._logger.debug(f"Initiating bigger orbit radius of 100cm, because distance to targeted pylon is: '{distance_to_targeted_pylon}'")
            if self._orbit_targeted_time_first_command == 0:
                self._orbit_targeted_time_first_command = time.time()

            self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=50, driving_direction=DrivingDirection.RIGHT,
                                             state_nomad=self._state)
            self._last_distance_targeted_pylon = distance_to_targeted_pylon
        elif 91 <= distance_to_targeted_pylon <= 100:
            self._logger.debug(f"Initiating smaller orbit radius of 50cm, because distance to targeted pylon is: '{distance_to_targeted_pylon}'")
            if self._orbit_targeted_time_first_command == 0:
                self._orbit_targeted_time_first_command = time.time()
            self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=50, driving_direction=DrivingDirection.RIGHT,
                                             state_nomad=self._state)
            self._last_distance_targeted_pylon = distance_to_targeted_pylon

        elif distance_to_targeted_pylon < 91:
            self._logger.debug(f"Distance: '{distance_to_targeted_pylon}' to targeted pylon already to small to drive correct 50cm/100cm orbits!"
                               f" Trying to drive 50cm Orbit anyway!")
            if self._orbit_targeted_time_first_command == 0:
                self._orbit_targeted_time_first_command = time.time()
            self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=50, driving_direction=DrivingDirection.RIGHT,
                                             state_nomad=self._state)
            self._last_distance_targeted_pylon = distance_to_targeted_pylon
        else:
            # 100 < Value < 141
            # Just keep driving and take the smaller 50cm orbit
            self._steering_communicator.resend_last_steering_command(new_state=self.state)

    def _process_state_OrbitEntered(self):
        """
        State: OrbitEntered
        In this State NOMAD should already be driving with a left curve around the orbit.
        :return:
        """
        # noinspection PyTypeChecker
        self._targeted_pylon = None
        self._logger.debug("Orbit entered. Driving on orbit..")
        time_to_stay_in_OrbitEntered = 0.5  # seconds
        if self._orbit_entered_enter_time == 0:
            self._orbit_entered_enter_time = time.time()
            self._steering_communicator.send(velocity_meters_per_second=1, state_nomad=self._state)
        else:
            if time.time() < self._orbit_entered_enter_time + time_to_stay_in_OrbitEntered:
                self._steering_communicator.resend_last_steering_command(new_state=self.state)
            else:
                self.trigger(Transitions.OrbitEntered_to_DestinationPylonUnknown.name)

    def _process_state_TransitEndangered(self):
        """
        State: TransitEndangered
        :return:
        """
        self._steering_communicator.resend_last_steering_command(new_state=self._state)

        if self._check_for_square_timber_in_front(distance_in_centimeters=50):
            self.trigger(Transitions.TransitEndangered_to_ObstacleDetected.name)
            return

        self._update_targeted_pylon()

        if self._danger_zone.number_of_evaluations >= 2:
            # not the first time we entered TransitEndangered without other states in between
            percentage_distance_decrease = self._danger_zone.percentage_distance_decrease_between_first_and_last_evaluation()

            if percentage_distance_decrease >= 0.6 or self._danger_zone.number_of_evaluations >= 13:
                self._drive_fictitious_pylon_orbit()
                self._fictitious_pylon_orbit_waiting_time_right_curve = 1
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
        if self._obstacle_overcome_movement_noticed():
            self.trigger(Transitions.ObstacleDetected_to_DestinationPylonUnknown.name)
        else:
            self._steering_communicator.resend_last_steering_command(new_state=self.state)

    def _update_targeted_pylon(self):
        """
        Update targeted pylon according to new data so make sure it's possible to find the targeted pylon in all pylons.
        After declaring a pylon as targeted pylon, we always move straight forward. Means the targeted pylon should still remain in the center.
        :return:
        """
        pylons_of_current_frame: List[DetectedObject] = self.data.get_pylons_only()
        if len(pylons_of_current_frame) != 0:
            self.targeted_pylon = self._pixel_grid.most_centered_pylon(pylons_of_current_frame)

    def _check_for_square_timber_in_front(self, distance_in_centimeters: float) -> bool:
        if self.data.has_measured_square_timbers():
            if self.data.nearest_square_timber().distance.value < distance_in_centimeters:
                self._logger.debug('Close square timber detected. Transition to ObstacleDetected..')
                return True
            else:
                return False
        else:
            return False

    def _drive_fictitious_pylon_orbit(self):
        """
        NOTE: This Method got changes in order to fit the simulation needs which appeared due to COVID-19!
        :return:
        """
        self._logger.debug("Driving fictitious pylon orbit")
        self._steering_communicator.send(velocity_meters_per_second=1, curve_radius_centimeters=50,
                                         driving_direction=DrivingDirection.RIGHT, state_nomad=self._state)
        self._should_drive_fictitious_pylon_orbit = True

    def _set_velocity(self, new_velocity_meters_per_second: float):
        """
        Sets the velocity of NOMAD to a specific value. Steering angle and drive direction remains the same.
        """
        self._steering_communicator.send(velocity_meters_per_second=new_velocity_meters_per_second, state_nomad=self._state)

    def _get_velocity(self) -> float:
        return self._steering_communicator.last_sent_velocity()

    def _obstacle_overcome_movement_noticed(self) -> bool:
        self._logger.info("Gyro Thread started")

        if self._pitch_down_noticed is False:
            if self._pitch_up_noticed is False:
                gyro_x = self._IMU_data.gyro_x
                if gyro_x <= -500:
                    self._pitch_up_noticed = True
                    self._logger.info('Pitch up noticed!')
                    return False
                else:
                    return False

            gyro_x = self._IMU_data.gyro_x
            if gyro_x >= 200:
                self._pitch_down_noticed = True
                self._logger.info('Pitch down noticed!')
                return False
            else:
                return False

        # Pitch up and down noticed, now check if gyro values remain stable (NOMAD in more or less straight position)

        if len(self._straight_gyro_x_values) < 5:
            gyro_x = self._IMU_data.gyro_x
            if -50 < gyro_x < 50:
                self._straight_gyro_x_values.append(gyro_x)
                return False
        else:
            self._logger.info('NOMADs x axis remained straight for 5 times. The obstacle seems to have been overcome.')
            return True

    def clear_danger_zone(self):
        """
        Is executed when State 'TransitEndangered' is left by transition.
        :return:
        """
        self._danger_zone.reset()

    def on_exit_DestinationPylonUnknown(self):
        """
        Resets the variables used in DestinationPylonUnknown when state is left
        :return:
        """
        self._should_drive_fictitious_pylon_orbit = False

    def on_exit_OrbitTargeted(self):
        """
        Resets the timer used in OrbitTargeted when State OrbitTargeted is left
        :return:
        """
        self._logger.debug('OrbitTargeted timer reset')
        self._orbit_targeted_time_first_command = 0
        self._last_distance_targeted_pylon = 0

    def on_exit_OrbitEntered(self):
        """
        Resets the timer used in OrbitEntered when State OrbitTargeted is left
        :return:
        """
        self._logger.debug('OrbitEntered timer reset')
        self._orbit_entered_enter_time = 0

    def on_exit_ObstacleDetected(self):
        """
        Resets all variables of state ObstacleDetected
        :return:
        """
        self._pitch_down_noticed = False
        self._pitch_up_noticed = False
        self._straight_gyro_x_values = []

    def _drive_straight(self, velocity: int):
        self._steering_communicator.send(velocity_meters_per_second=velocity, curve_radius_centimeters=0, driving_direction=DrivingDirection.STRAIGHT,
                                         state_nomad=self._state)

    @property
    def data(self) -> ObjectDetectorResult:
        return self._data

    @data.setter
    def data(self, current_result: ObjectDetectorResult):
        self._data = current_result

    @property
    def imu_data(self) -> IMUData:
        return self._IMU_data

    @imu_data.setter
    def imu_data(self, current_imu_data: IMUData):
        self._IMU_data = current_imu_data

    def set_sender(self, new_sender: Sender):
        self._steering_communicator.sender = new_sender

    @property
    def state(self):
        return self._state

    @property
    def targeted_pylon(self):
        return self._targeted_pylon

    @targeted_pylon.setter
    def targeted_pylon(self, new_targeted_pylon: DetectedObject):
        self._logger.debug(f'New Targeted Pylon: {new_targeted_pylon}')
        self._targeted_pylon = new_targeted_pylon
