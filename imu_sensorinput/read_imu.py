"""
    Read Gyro and Accelerometer by Interfacing Raspberry Pi with MPU6050 using Python
    http://www.electronicwings.com
"""
# Libraries
from smbus2 import SMBus  # import SMBus2 module since original smbus module is incompatible with python3.8
from time import sleep

# set MPU6050 registers and their address
Device_Address = 0x68  # MPU6050 device address
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47


class ReadIMU:
    # create class instance as singleton to prevent multiple I2C initialization attempts
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self.bus = SMBus(1)  # select I2C bus 1 (pin 3 & 5)
        self.MPU_Init()

    def MPU_Init(self):
        # write to sample rate register
        self.bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)

        # write to power management register
        self.bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)

        # write to Configuration register
        self.bus.write_byte_data(Device_Address, CONFIG, 0)

        # write to Gyro configuration register
        self.bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)

        # write to interrupt enable register
        self.bus.write_byte_data(Device_Address, INT_ENABLE, 1)

    def read_raw_data(self, addr):
        # accelerometer and gyroscope values are 16-bit
        high = self.bus.read_byte_data(Device_Address, addr)
        low = self.bus.read_byte_data(Device_Address, addr + 1)

        # concatenate higher and lower value
        value = ((high << 8) | low)

        # to get signed value from mpu6050
        if value > 32768:
            value = value - 65536
        return value

    # read accelerometer value
    def get_accel(self):
        acc_x = self.read_raw_data(ACCEL_XOUT_H) / 16384.0
        acc_y = self.read_raw_data(ACCEL_YOUT_H) / 16384.0
        acc_z = self.read_raw_data(ACCEL_ZOUT_H) / 16384.0
        return acc_x, acc_y, acc_z

    # read gyroscope value
    def get_gyro(self):
        gyro_x = self.read_raw_data(GYRO_XOUT_H) / 131.0
        gyro_y = self.read_raw_data(GYRO_YOUT_H) / 131.0
        gyro_z = self.read_raw_data(GYRO_ZOUT_H) / 131.0
        return gyro_x, gyro_y, gyro_z
