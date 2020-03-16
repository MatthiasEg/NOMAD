#Libraries
import Jetson.GPIO as GPIO
import time
 
#GPIO Mode sets pin addressing scheme
GPIO.setmode(GPIO.BOARD)
 
#set GPIO Pins
GPIO_TRIGGER_A = 12
GPIO_ECHO_A = 16
GPIO_TRIGGER_B = 18
GPIO_ECHO_B = 22
 
#set GPIO direction
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
    
        StartTime = time.time()
        StopTime = time.time()
    
        # save StartTime
        while GPIO.input(GPIO_ECHO_A) == 0:
            StartTime = time.time()
    
        # save time of arrival
        while GPIO.input(GPIO_ECHO_A) == 1:
            StopTime = time.time()
    
        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance_A = (TimeElapsed * 34300) / 2
    
        # set TriggerB to HIGH
        GPIO.output(GPIO_TRIGGER_B, True)
    
        # set TriggerB after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(GPIO_TRIGGER_B, False)
    
        # save StartTime
        while GPIO.input(GPIO_ECHO_B) == 0:
            StartTime = time.time()
    
        # save time of arrival
        while GPIO.input(GPIO_ECHO_B) == 1:
            StopTime = time.time()
    
        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance_B = (TimeElapsed * 34300) / 2
    
        GPIO.cleanup()
        
        return distance_A, distance_B
