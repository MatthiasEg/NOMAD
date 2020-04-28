import cv2

from camera_sensorinput.fake_data_reader import FakeDataReader


class SonarData:

    def __init__(self, contact_top: bool, distance_top: float, contact_bottom: bool, distance_bottom: float):
        self._contact_top = contact_top
        self._distance_top = distance_top
        self._contact_bottom = contact_bottom
        self._distance_bottom = distance_bottom

    @property
    def contact_top(self) -> bool:
        return self._contact_top

    @property
    def distance_top(self) -> float:
        return self._distance_top

    @property
    def contact_bottom(self) -> bool:
        return self._contact_bottom

    @property
    def distance_bottom(self) -> float:
        return self._distance_bottom


class ReadSonar:

    def __init__(self):
        self.fake_data_reader: FakeDataReader = FakeDataReader("sonardata")

    def get_Data(self) -> SonarData:
        file_path = self.fake_data_reader.getNextFilePath()
        file = open(file_path, "r")
        values = file.readline().replace(',', '').split(' ')
        return SonarData(False, float(values[0]), True, float(values[1]))

    def close(self):
        self.cap.release()
