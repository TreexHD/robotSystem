"""
this is the main module
"""
import platform
import time

from robotsystem.debug import Debug

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


class Robot_:

    def __init__(self):
        self.motor_driver = self.__move_l293
        self.threshold = [None, 2350, 2350, 2350, 2350, 2350, 3900, 3900]
        self.Debug = robotsystem.debug.Debug()
        self.distances = [None, -1, -1, -1, -1]
        self.grayscale = -1
        if not isWindows:
            self.MCP3008 = robotsystem.bus.MCP3008()
            self.IO = robotsystem.bus.IO()
            self.bus = robotsystem.bus.I2C(self.IO)

    def delay(self, delay_in_ms: int):
        """
        wait milliseconds
        :param delay_in_ms:
        :return:
        """
        time.sleep(delay_in_ms/1000)

    def terminate(self):
        """
        terminates the whole process correctly
        :return:
        """
        try:
            self.IO.cleanup()
        except Exception as e:
            Debug.error_imp(str(e) + " --- Couldn't terminate clean!!!")
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

    def set_motor_driver(self, l293: bool) -> None:
        """
        select the motor driver type l293 or tc1508a
        :param l293: is l293
        """
        if l293:
            self.motor_driver = self.__move_l293
        else:
            self.motor_driver = self.__move_tc1508a

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

    def set_sensor_leds(self, colour: int):
        """
        set the colour of the sensor leds
        :param colour: 0=off 1=red 2=green
        :return:
        """
        self.IO.set_sensor_leds(colour)

    def set_servo_degree(self, pin: int, degree: int):
        """
        set the angle of a specific servo with the pin 0-4
        :param pin: the pin of the servo
        :param degree: angle in degree
        :return:
        """
        if pin < 0 or pin > 4:
            raise Exception(str(pin) + " is no a valid servo PIN")
        degree = map_range(degree, 0, 180, 0,4096)
        self.bus.set_pwm_pca9685(12-pin, 0, degree)

    def set_mode_led_on(self, on: bool=True):
        """
        set the mode led, to on or off
        :param on: led on
        :return:
        """
        if on:
            self.IO.set(23, 1)
        else:
            self.IO.set(23, 0)

    def set_digital(self, pin: int, value: int):
        """
        set the pwm value of D1-D3
        :param pin: pin 1-3
        :param value: 0-4096
        :return:
        """
        if pin < 1 or pin > 3:
            raise Exception(str(pin) + " is no a valid digital PIN")
        if value < 0 or value > 4096:
            raise Exception(str(value) + " is no a valid value")
        self.bus.set_pwm_pca9685(16-pin,0,value)

    def get_switch_value(self, sw_pin: int) -> int:
        """
        get the state of the switch
        :param sw_pin: pin number (3 or 4)
        :return:
        """
        if sw_pin == 3:
            return int(self.IO.read(24))
        if sw_pin == 4:
            return int(self.IO.read(25))
        raise Exception(str(sw_pin) + " is not a valid switch PIN")


    def set_restart_callback(self, func):
        """
        set the callback function on reset button press
        :param func: the function name
        :return:
        """
        self.IO.func_callback = func

    def set_mode_callback(self, func):
        """
        set the callback function on mode button press
        :param func: the function name
        :return:
        """
        self.IO.mde_callback = func

    def move(self, motor_1: int, motor_2: int, motor_3: int, motor_4: int) -> None:
        self.motor_driver(motor_1, motor_2, motor_3, motor_4)

    def __move_tc1508a(self, motor_1: int, motor_2: int, motor_3: int, motor_4: int) -> None:
        """
        set the individual motor direction and speed (-4096 bis 4096)
        :param motor_1: for motor 1
        :param motor_2: for motor 2
        :param motor_3: for motor 3
        :param motor_4: for motor 4
        :return:
        """
        #Motor 1
        if motor_1 > 0:
            m1a = motor_1
            m1b = 0
        else:
            m1a = 0
            m1b = motor_1 * -1
        # Motor 2
        if motor_2 > 0:
            m2a = motor_2
            m2b = 0
        else:
            m2a = 0
            m2b = motor_2 * -1
        # Motor 3
        if motor_3 > 0:
            m3a = motor_3
            m3b = 0
        else:
            m3a = 0
            m3b = motor_3 * -1
        # Motor 4
        if motor_4 > 0:
            m4a = motor_4
            m4b = 0
        else:
            m4a = 0
            m4b = motor_4 * -1

        self.bus.set_pwm_pca9685(0, 0, m1a)
        self.bus.set_pwm_pca9685(4, 0, m1b)

        self.bus.set_pwm_pca9685(1, 0, m2a)
        self.bus.set_pwm_pca9685(5, 0, m2b)

        self.bus.set_pwm_pca9685(2, 0, m3a)
        self.bus.set_pwm_pca9685(6, 0, m3b)

        self.bus.set_pwm_pca9685(3, 0, m4a)
        self.bus.set_pwm_pca9685(7, 0, m4b)

    def __move_l293(self, motor_1: int, motor_2: int, motor_3: int, motor_4: int) -> None:
        """
        set the individual motor direction and speed (-4096 bis 4096)
        :param motor_1: for motor 1
        :param motor_2: for motor 2
        :param motor_3: for motor 3
        :param motor_4: for motor 4
        :return:
        """
        #Motor 1
        if motor_1 > 0:
            m1a = 4096
            m1b = motor_1
        else:
            m1a = 0
            m1b = motor_1 * -1
        # Motor 2
        if motor_2 > 0:
            m2a = 4096
            m2b = motor_2
        else:
            m2a = 0
            m2b = motor_2 * -1
        # Motor 3
        if motor_3 > 0:
            m3a = 4096
            m3b = motor_3
        else:
            m3a = 0
            m3b = motor_3 * -1
        # Motor 4
        if motor_4 > 0:
            m4a = 4096
            m4b = motor_4
        else:
            m4a = 0
            m4b = motor_4 * -1

        self.bus.set_pwm_pca9685(0, 0, m1a)
        self.bus.set_pwm_pca9685(4, 0, m1b)

        self.bus.set_pwm_pca9685(1, 0, m2a)
        self.bus.set_pwm_pca9685(5, 0, m2b)

        self.bus.set_pwm_pca9685(2, 0, m3a)
        self.bus.set_pwm_pca9685(6, 0, m3b)

        self.bus.set_pwm_pca9685(3, 0, m4a)
        self.bus.set_pwm_pca9685(7, 0, m4b)

