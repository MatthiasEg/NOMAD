import cv2


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

    def get_Data(self) -> SonarData:
        return SonarData(False, 4.0, True, 2.0)

    def close(self):
        self.cap.release()
