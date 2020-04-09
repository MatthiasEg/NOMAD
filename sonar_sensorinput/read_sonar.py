# Libraries
import Jetson.GPIO as GPIO
import time

# GPIO Mode sets pin addressing scheme
GPIO.setmode(GPIO.BOARD)

# set GPIO Pins
GPIO_TRIGGER_A = 12
GPIO_ECHO_A = 16
GPIO_TRIGGER_B = 18
GPIO_ECHO_B = 22

# set GPIO direction
GPIO.setup(GPIO_TRIGGER_A, GPIO.OUT)
GPIO.setup(GPIO_ECHO_A, GPIO.IN)
GPIO.setup(GPIO_TRIGGER_B, GPIO.OUT)
GPIO.setup(GPIO_ECHO_B, GPIO.IN)


class ReadSonar:
    @staticmethod
    def getDistance():
        # set TriggerA to HIGH
        GPIO.output(GPIO_TRIGGER_A, True)

        # set TriggerA after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(GPIO_TRIGGER_A, False)

        start_time = time.time()
        stop_time = time.time()

        # save start_time
        while GPIO.input(GPIO_ECHO_A) == 0:
            start_time = time.time()

        # save time of arrival
        while GPIO.input(GPIO_ECHO_A) == 1:
            stop_time = time.time()

        # time difference between start and arrival
        time_elapsed = stop_time - start_time
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance_a = (time_elapsed * 34300) / 2

        # set TriggerB to HIGH
        GPIO.output(GPIO_TRIGGER_B, True)

        # set TriggerB after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(GPIO_TRIGGER_B, False)

        # save start_time
        while GPIO.input(GPIO_ECHO_B) == 0:
            start_time = time.time()

        # save time of arrival
        while GPIO.input(GPIO_ECHO_B) == 1:
            stop_time = time.time()

        # time difference between start and arrival
        time_elapsed = stop_time - start_time
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance_b = (time_elapsed * 34300) / 2

        return distance_a, distance_b
