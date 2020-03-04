from multiprocessing import Process
from object_detection.pylon_detector.pylon_detector import PylonDetector
from object_detection.object_detector.object_detector import ObjectDetector
from object_detection.obstacle_detector.obstacle_detector import ObstacleDetector
import logging
import sys

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

if __name__ == '__main__':
    main()