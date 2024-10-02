"""
this is the main module
"""
import platform

isWindows = True
if platform.system() == "Linux":
    isWindows = False
    from spidev import SpiDev
    import smbus
    import RPi.GPIO as GPIO
import robotsystem.debug
import robotsystem.bus

# CONST
LL = 1
L = 2
M = 3
R = 4
RR = 5
LG = 6
RG = 7


def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


class Robot:

    def __init__(self):
        self.threshold = [0, 2350, 2350, 2350, 2350, 2350, 3900, 3900]
        self.Debug = robotsystem.debug.Debug
        self.distances = [None, -1, -1, -1, -1]
        self.grayscale = -1
        if not isWindows:
            self.MCP3008 = robotsystem.bus.MCP3008()
            self.IO = robotsystem.bus.IO()
            self.bus = robotsystem.bus.I2C(self.IO)

    def terminate(self):
        """
        terminates the whole process correctly
        :return:
        """
        self.IO.cleanup()
        return

    def update(self):
        """
        updates some robot data. Executed at the end of loop
        :return:
        """
        self.bus.update_tof()
        self.distances = self.bus.distances
        self.grayscale = self.MCP3008.get_greyscale(self.threshold)

    def set_threshold(self, pin: int, value: int) -> None:
        """
        set the thresholds of the sensors
        :param pin: the pin of the sensor (LL, L, M, ...)
        :param value: the threshold value, use function test example?
        :return:
        """
        if pin < 1 or pin > 7:
            raise Exception(str(pin) + " is not a valid PIN")
        if pin < 0 or pin > 4096:
            raise Exception(str(value) + " is not a valid VALUE")
        self.threshold[pin] = value

    def get_distance(self, pin: int) -> int:
        """
        get and await the distance of the TOF sensor
        :param pin: with the pin of 1-4
        :return: returns the distance
        """
        return self.bus.read_tof(pin)

    def get_grayscale(self, pin: int) -> int:
        """
        get the grayscale data of one sensor
        :param pin: the pin of the sensor (LL, L, M, ...)
        :return: returns the value
        """
        return self.MCP3008.get_one(pin)

    def move(self, motor_a: float, motor_b: float, motor_c: float, motor_d: float) -> None:
        """
        set the individual motor direction and speed (-100 bis 100)
        :param motor_a: for motor A
        :param motor_b: for motor B
        :param motor_c: for motor C
        :param motor_d: for motor D
        :return:
        """
        motor_a = map_range(motor_a, -100, 100, 0, 4090)





