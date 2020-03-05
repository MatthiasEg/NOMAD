from multiprocessing import Process
from object_detection.pylon_detector.pylon_detector import PylonDetector
from object_detection.object_detector.object_detector import ObjectDetector
from object_detection.obstacle_detector.obstacle_detector import ObstacleDetector
import logging
import sys
from statemachine.statemachine import StateMachine
from statemachine.states.start import Start

#Config Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - [%(threadName)s] - %(message)s',     
    handlers=[logging.StreamHandler()],
    level=logging.DEBUG
)

def startObstacleDetection():
    obstacleDetector = ObstacleDetector()
    obstacleDetector.start()

def startObjectDetection():
    objectDetector = ObjectDetector()
    objectDetector.start()

def startPylonDetection():
    pylonDetector = PylonDetector()
    pylonDetector.start()

def main():
    logger = logging.getLogger("STARTUP")
    logger.info("starting server...")

    obstacleDetectorProcess = Process(target=startObstacleDetection, args=())
    obstacleDetectorProcess.start()

    pylonDetectorProcess = Process(target=startPylonDetection, args=())
    pylonDetectorProcess.start()
    
    objectDetectionProcess = Process(target=startObjectDetection, args=())
    objectDetectionProcess.start()


def __start_state_machine():
    state_machine = StateMachine(Start())
    state_machine.request1()
    state_machine.request2()

if __name__ == '__main__':
    main()
    __start_state_machine()
