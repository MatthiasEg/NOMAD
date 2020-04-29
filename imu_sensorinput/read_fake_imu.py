

from camera_sensorinput.fake_data_reader import FakeDataReader


class IMUData:

    def __init__(self, accel_x: float, accel_y: float, accel_z: float,  gyros_x: float, gyros_y: float, gyros_z: float):
        self.accel_x = accel_x * 16384.0
        self.accel_y = accel_y * 16384.0
        self.accel_z = accel_z * 16384.0
        self.gyros_x = gyros_x * 131.0
        self.gyros_y = gyros_y * 131.0
        self.gyros_z = gyros_z * 131.0

    @property
    def acc_x(self) -> float:
        return self.accel_x

    @property
    def acc_y(self) -> float:
        return self.accel_y

    @property
    def acc_z(self) -> float:
        return self.accel_z

    @property
    def gyro_x(self) -> float:
        return self.gyros_x

    @property
    def gyro_y(self) -> float:
        return self.gyros_y

    @property
    def gyro_z(self) -> float:
        return self.gyros_z


class ReadIMU:

    def __init__(self):
        self.fake_data_reader: FakeDataReader = FakeDataReader("imudata")

    def get_Data(self) -> IMUData:
        file_path = self.fake_data_reader.getNextFilePath()
        file = open(file_path, "r")
        values = file.readline().replace(',', '').replace(' / ', ' ').split(' ')
        return IMUData(float(values[0]), float(values[1]), float(values[2]), float(values[3]),
                       float(values[4]), float(values[5]))

    def close(self):
        self.cap.release()
