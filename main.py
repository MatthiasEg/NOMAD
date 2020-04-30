from multiprocessing import Process

from object_detection.object_detector.fake_object_detector import FakeObjectDetector
from object_detection.object_detector.testing.object_detector_visualizer import ObjectDetectorVisualizer
import logging

# Config Logging
from statemachine.steering_command_generator import SteeringCommandGenerator
from uart_connector.uart_connector import UartConnector

logging.basicConfig(
    format='%(asctime)s - %(name)s - [%(threadName)s] - %(message)s',
    handlers=[logging.StreamHandler()],
    level=logging.DEBUG
)


def startFakeObjectDetection():
    fakeObjectDetection = FakeObjectDetector()
    fakeObjectDetection.start()

def startVisualizerObjectDetection():
    visualizerObjectDetection = ObjectDetectorVisualizer()
    visualizerObjectDetection.start()


def startSteeringCommandGenerator():
    steering_command_generator = SteeringCommandGenerator()
    steering_command_generator.start()


def startUartConnector():
    uart_connector = UartConnector()
    uart_connector.start()


def main():
    logger = logging.getLogger("STARTUP")
    logger.info("starting server...")

    fake_object_detection_process = Process(target=startFakeObjectDetection, args=())
    fake_object_detection_process.start()

    visualizer_object_detection_process = Process(target=startVisualizerObjectDetection, args=())
    visualizer_object_detection_process.start()

    #steering_command_generator_process = Process(target=startSteeringCommandGenerator, args=())
    #steering_command_generator_process.start()

    #uart_connector_process = Process(target=startUartConnector(), args=())
    #uart_connector_process.start()


if __name__ == '__main__':
    main()
