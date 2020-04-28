from camera_sensorinput.fake_data_reader import FakeDataReader
from camera_sensorinput.read_fake_camera import ReadCamera
from communication.receiver import Receiver
from communication.node import Node
from sonar_sensorinput.read_fake_sonar import ReadSonar
import pickle


class ObjectDetectorRecorder(Node):
    _node_config_section = "RECORDER"

    def __init__(self):
        super().__init__(self._node_config_section)
        self._sensor_input_camera = ReadCamera()

    def _start_up(self):
        self.fake_data_reader: FakeDataReader = FakeDataReader("jpg")
        self._object_detector_receiver = Receiver("OBJECT_DETECTOR")
        self._fake_sonar = ReadSonar()

    def _progress(self):
        object_detector_result = self._object_detector_receiver.receive()
        print("SAVED NEW")
        filenamePath = "/home/manuel/PREN/workspaces/informatik/object_detection/darknet/fakedata"
        filename = filenamePath + '/' + self.fake_data_reader.getNextTimestamp() + ".objectresult"
        pickle_out = open(filename, "wb")
        pickle.dump(object_detector_result, pickle_out)
        pickle_out.close()

    def _shut_down(self):
        self._object_detector_receiver.close()
