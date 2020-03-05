from multiprocessing import Process
from object_detection.pylon_detector.pylon_detector import PylonDetector
from object_detection.object_detector.object_detector import ObjectDetector
from object_detection.obstacle_detector.obstacle_detector import ObstacleDetector
import logging
import sys

# Config Logging
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


def main():
    logger = logging.getLogger("STARTUP")
    logger.info("starting server...")

    obstacle_detector_process = Process(target=startObstacleDetection, args=())
    obstacle_detector_process.start()

    pylon_detector_process = Process(target=startPylonDetection, args=())
    pylon_detector_process.start()

    object_detection_process = Process(target=startObjectDetection, args=())
    object_detection_process.start()


def __start_state_machine():
    pass


if __name__ == '__main__':
    main()
    __start_state_machine()
