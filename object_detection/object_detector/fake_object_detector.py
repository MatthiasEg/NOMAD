from camera_sensorinput.fake_data_reader import FakeDataReader
from communication.sender import Sender
from communication.node import Node
import pickle

from object_detection.object_detector.object_detector_result import ObjectDetectorResult


class FakeObjectDetector(Node):
    _node_config_section = "OBJECT_DETECTOR"

    def __init__(self):
        super().__init__(self._node_config_section)
        self.fake_data_reader: FakeDataReader = FakeDataReader("objectresult")

    # Node method implementations
    def _start_up(self):
        self._object_detector_sender = Sender(self._node_config_section)

    def _progress(self):
        pickle_in = open(self.fake_data_reader.getNextFilePath(), "rb")
        print("d")
        object_detector_result: ObjectDetectorResult = pickle.load(pickle_in)
        self._object_detector_sender.send(object_detector_result)

    def _shut_down(self):
        self._object_detector_sender.close()
