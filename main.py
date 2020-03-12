from multiprocessing import Process
from object_detection.pylon_detector.pylon_detector import PylonDetector
from object_detection.object_detector.object_detector import ObjectDetector
from object_detection.obstacle_detector.obstacle_detector import ObstacleDetector
import logging
import sys

# Config Logging
from statemachine.steering_command_generator import SteeringCommandGenerator

logging.basicConfig(
    format='%(asctime)s - %(name)s - [%(threadName)s] - %(message)s',
    handlers=[logging.StreamHandler()],
    level=logging.DEBUG
)


def startObstacleDetection():
    obstacle_detector = ObstacleDetector()
    obstacle_detector.start()


def startObjectDetection():
    object_detector = ObjectDetector()
    object_detector.start()


def startPylonDetection():
    pylon_detector = PylonDetector()
    pylon_detector.start()


def startSteeringCommandGenerator():
    steering_command_generator = SteeringCommandGenerator()
    steering_command_generator.start()


def main():
    logger = logging.getLogger("STARTUP")
    logger.info("starting server...")

    # obstacle_detector_process = Process(target=startObstacleDetection, args=())
    # obstacle_detector_process.start()
    #
    # pylon_detector_process = Process(target=startPylonDetection, args=())
    # pylon_detector_process.start()
    #
    # object_detection_process = Process(target=startObjectDetection, args=())
    # object_detection_process.start()

    # steering_command_generator_process = Process(target=startSteeringCommandGenerator, args=())
    # steering_command_generator_process.start()

    startSteeringCommandGenerator()


if __name__ == '__main__':
    main()
