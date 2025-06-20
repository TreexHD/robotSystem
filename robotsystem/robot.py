"""
this is the main module
"""
import platform
import time
import os
import json

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
        self.pca_address = 0x60
        self.motor_driver = self.__move_l293
        self.motor_invert = [False, False, False, False]
        self.threshold = [None, 2350, 2350, 2350, 2350, 2350, 3900, 3900]
        self.Debug = robotsystem.debug.Debug()
        self.distances = [None, -1, -1, -1, -1]
        self.grayscale = -1
        if not isWindows:
            self.MCP3008 = robotsystem.bus.MCP3008()
            self.IO = robotsystem.bus.IO()
            self.bus = robotsystem.bus.I2C(self.IO)

    def delay(self, delay_in_ms: int) -> None:
        """
        wait milliseconds
        :param delay_in_ms:
        :return:
        """
        time.sleep(delay_in_ms/1000)

    def terminate(self) -> None:
        """
        terminates the whole process correctly
        :return:
        """
        try:
            self.move(0,0,0,0)
            self.IO.cleanup()
        except Exception as e:
            Debug.error_imp(None, str(e) + " --- Couldn't terminate clean!!!")
        return

    def init(self) -> None:
        """
        inits the robot data. Executed at the end of the setup
        :return:
        """
        self.bus.pca_address = self.pca_address
        self.bus.initialize_pca9685()

    def update(self) -> None:
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

    def set_motor_invert(self, motor1: bool, motor2: bool, motor3: bool, motor4: bool) -> None:
        """
        select the motors where the value should be inverted with true
        :return:
        """
        self.motor_invert = [motor1, motor2, motor3, motor4]

    def set_pca_address(self, address: hex) -> None:
        """
        change the address of the pca9685 ic. use(hex value)
        :return:
        """
        self.pca_address = address

    def set_motor_driver(self, l293: bool) -> None:
        """
        select the motor driver type l293 or tc1508a
        :param l293: is l293
        """
        if l293:
            self.motor_driver = self.__move_l293
            Debug.info(None,"Selected L293 Motor Driver")
        else:
            self.motor_driver = self.__move_tc1508a
            Debug.info(None, "Selected tc1508a Motor Driver")

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

    def set_sensor_leds(self, colour: int) -> None:
        """
        set the colour of the sensor leds
        :param colour: 0=off 1=red 2=green
        :return:
        """
        self.IO.set_sensor_leds(colour)

    def set_servo_degree(self, pin: int, degree: int) -> None:
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

    def set_mode_led_on(self, on: bool=True) -> None:
        """
        set the mode led, to on or off
        :param on: led on
        :return:
        """
        if on:
            self.IO.set(23, 1)
        else:
            self.IO.set(23, 0)

    def set_digital(self, pin: int, value: int) -> None:
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


    def set_restart_callback(self, func) -> None:
        """
        set the callback function on reset button press
        :param func: the function name
        :return:
        """
        self.IO.func_callback = func

    def set_mode_callback(self, func) -> None:
        """
        set the callback function on mode button press
        :param func: the function name
        :return:
        """
        self.IO.mde_callback = func

    def load_calibration(self) -> None:
        """
        load the threshold values from the data.json file
        :return:
        """
        try:
            with open('data.json') as f:
                d = json.load(f)
        except Exception as e:
            Debug.error(None, "can't read data.json: " + str(e))
        try:
            self.set_threshold(LL, int(d['sensor']['LL']))
            self.set_threshold(L, int(d['sensor']['L']))
            self.set_threshold(M, int(d['sensor']['M']))
            self.set_threshold(R, int(d['sensor']['R']))
            self.set_threshold(RR, int(d['sensor']['RR']))
            Debug.msg(None, str(d['sensor']))
            Debug.okblue(None, "Data loaded successfully!")
        except Exception as e:
            Debug.error(None, "can't process data (wrong formatting): " + str(e))

    def start_calibration(self) -> None:
        """
        start the sensor calibration sequenz
        :return:
        """
        white_value = [0,0]
        black_value = [0,0]
        middle_value = [0,0,0,0,0]

        self.Debug.info("All white!")
        self.delay(3500)
        for i in range(1, 6):
            pass
            #white_value.append(self.get_grayscale(i))
        self.Debug.info("All black!")
        self.delay(3500)
        for i in range(1, 6):
            pass
            #black_value.append(self.get_grayscale(i))
        for i in range(0, 5):
            pass
            #middle_value.append(int((black_value[i] - white_value[i]) / 2 + white_value[i]))
        self.Debug.info("Value for black: " + str(black_value))
        self.Debug.info("Value for white: " + str(white_value))
        self.Debug.info("Value for middle: " + str(middle_value))
        #print(os.getcwd())

        data = {'sensor': {
                    'LL': middle_value[0],
                    'L': middle_value[1],
                    'M': middle_value[2],
                    'R': middle_value[3],
                    'RR': middle_value[4],
        }}
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        self.Debug.info("Wrote file: data.json")


    def stop(self) -> None:
        """
        stop all movement of the robot
        :return:
        """
        self.move(0,0,0,0)

    def move(self, motor_1: int, motor_2: int, motor_3: int, motor_4: int) -> None:
        """
        move the motors, values from
        :param motor_1:
        :param motor_2:
        :param motor_3:
        :param motor_4:
        :return:
        """
        if self.motor_invert[0]:
            motor_1 = motor_1 * -1
        if self.motor_invert[1]:
            motor_2 = motor_2 * -1
        if self.motor_invert[2]:
            motor_3 = motor_3 * -1
        if self.motor_invert[3]:
            motor_4 = motor_4 * -1
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

        self.bus.set_pwm_pca9685(2, 0, m1a)
        self.bus.set_pwm_pca9685(6, 0, m1b)

        self.bus.set_pwm_pca9685(3, 0, m2a)
        self.bus.set_pwm_pca9685(7, 0, m2b)

        self.bus.set_pwm_pca9685(0, 0, m3a)
        self.bus.set_pwm_pca9685(4, 0, m3b)

        self.bus.set_pwm_pca9685(1, 0, m4a)
        self.bus.set_pwm_pca9685(5, 0, m4b)

    def __move_l293(self, motor_1: int, motor_2: int, motor_3: int, motor_4: int) -> None:
        """
        set the individual motor direction and speed (-4096 bis 4096)
        :param motor_1: for motor 1
        :param motor_2: for motor 2
        :param motor_3: for motor 3
        :param motor_4: for motor 4
        :return:
        """
        #Motor 3
        if motor_3 > 0:
            m1a = 4095
            m1b = motor_3
        else:
            m1a = 0
            m1b = motor_3 * -1
        # Motor 4
        if motor_4 > 0:
            m2a = 4095
            m2b = motor_4
        else:
            m2a = 0
            m2b = motor_4 * -1
        # Motor 1
        if motor_1 > 0:
            m3a = 4095
            m3b = motor_1
        else:
            m3a = 0
            m3b = motor_1 * -1
        # Motor 2
        if motor_2 > 0:
            m4a = 4095
            m4b = motor_2
        else:
            m4a = 0
            m4b = motor_2 * -1

        self.bus.set_pwm_pca9685(0, 0, m1a)
        self.bus.set_pwm_pca9685(4, 0, m1b) #ENA

        self.bus.set_pwm_pca9685(1, 0, m2a)
        self.bus.set_pwm_pca9685(5, 0, m2b) #ENB

        self.bus.set_pwm_pca9685(2, 0, m3a)
        self.bus.set_pwm_pca9685(6, 0, m3b) # ENC

        self.bus.set_pwm_pca9685(3, 0, m4a)
        self.bus.set_pwm_pca9685(7, 0, m4b) # END
