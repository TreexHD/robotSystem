from robotsystem.debug import Debug
import platform
import time

isWindows = True
if platform.system() == "Linux":
    isWindows = False
    from spidev import SpiDev
    import smbus
    import RPi.GPIO as GPIO

# CONSTANTS
TOF1 = 17
TOF2 = 5
TOF3 = 6
TOF4 = 26
PCA9685_ADDRESS = 0x40
TOF_ADDRESS = 0x29

# Define VL53L0X registers
VL53L0X_REG_SYSRANGE_START = 0x00
VL53L0X_REG_RESULT_RANGE_STATUS = 0x14

#Registers of PCA9685
MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06

class I2C:  # NANO ADDRESS 0x08
    def __init__(self, io):
        self.pca_address = PCA9685_ADDRESS
        self.io = io
        self.bus = smbus.SMBus(1)
        self.distances = [None, -1, -1, -1, -1]  # The distances of the TOF sensors

        #locals
        self.__initialized_tofs = []

        #actions
        self.init_all_tofs()
        #self.initialize_pca9685() #moved to Robot.init()

        time.sleep(1)
        Debug.info(None, "SMBus ready (I2C)")

    def initialize_pca9685(self):
        # Initialize the PCA9685 chip
        try:
            self.bus.write_byte_data(self.pca_address, MODE1, 0x00)  # Normal mode
            self.set_pwm_freq_pca9685(100)  # Set frequency to 100Hz
        except Exception as e:
            Debug.error(None, "No connection to PCA9685 ")
            raise e

    def set_pwm_freq_pca9685(self, freq_hz):
        # Set the PWM frequency
        prescale_val = int(25000000.0 / (4096 * freq_hz) - 1)
        old_mode = self.bus.read_byte_data(self.pca_address, MODE1)
        new_mode = (old_mode & 0x7F) | 0x10  # Sleep
        self.bus.write_byte_data(self.pca_address, MODE1, new_mode)
        self.bus.write_byte_data(self.pca_address, PRESCALE, prescale_val)
        self.bus.write_byte_data(self.pca_address, MODE1, old_mode)
        time.sleep(0.005)
        self.bus.write_byte_data(self.pca_address, MODE1, old_mode | 0x80)

    def set_pwm_pca9685(self, channel: int, on: int, off: int):
        # Set the PWM value for a specific channel
        try:
            self.bus.write_byte_data(self.pca_address, LED0_ON_L + 4 * channel, on & 0xFF)
            self.bus.write_byte_data(self.pca_address, LED0_ON_L + 4 * channel + 1, on >> 8)
            self.bus.write_byte_data(self.pca_address, LED0_ON_L + 4 * channel + 2, off & 0xFF)
            self.bus.write_byte_data(self.pca_address, LED0_ON_L + 4 * channel + 3, off >> 8)
        except Exception as e:
            Debug.error(None, "No connection to PCA9685 ")
            raise e

    def write_data(self, address, first, second, third):
        data = [first, second, third]
        # Debug.msg("Sending data:" + str(data))
        try:
            self.bus.write_i2c_block_data(address, 0, data)
        except Exception as e:
            Debug.error(None, "Error sending I2C data: " + str(e))

    def init_all_tofs(self):
        self.io.set(TOF1, 0)
        self.io.set(TOF2, 0)
        self.io.set(TOF3, 0)
        self.io.set(TOF4, 0)
        for i in range(4):
            try:
                self.init_tof(i + 1)
            except:
                Debug.msg(None, "No TOF at PIN: " + str(i + 1))

    def init_tof(self, pin: int):
        """
        initialize a connected tof sensor
        :param pin: the pin number of the tof [1,2,3,4]
        """
        if pin not in [1, 2, 3, 4]:
            raise ValueError("Invalid value for 'pin'. Expected 1, 2, 3, or 4.")
        default_address = TOF_ADDRESS
        desired_address = TOF_ADDRESS + pin

        if pin == 1:
            self.io.set(TOF1, 1)
        elif pin == 2:
            self.io.set(TOF2, 1)
        elif pin == 3:
            self.io.set(TOF3, 1)
        elif pin == 4:
            self.io.set(TOF4, 1)

        time.sleep(0.01)

        try:

            # Change the I2C address of the VL53L0X
            self.bus.write_byte_data(default_address, 0x8A, desired_address)
            time.sleep(0.01)

            # Initialize the sensor
            self.bus.write_byte_data(desired_address, 0x88, 0x00)  # Set I2C standard mode
            self.bus.write_byte_data(desired_address, 0x80, 0x01)  # Set I2C fast mode
            self.bus.write_byte_data(desired_address, 0xFF, 0x01)  # Enter initialization mode
            self.bus.write_byte_data(desired_address, 0x00, 0x00)  # Set default settings
            self.bus.write_byte_data(desired_address, 0x91, 0x3C)  # Set specific calibration value
            self.bus.write_byte_data(desired_address, 0x00, 0x01)  # Start initialization
            self.bus.write_byte_data(desired_address, 0xFF, 0x00)  # Exit initialization mode
            self.bus.write_byte_data(desired_address, 0x80, 0x00)  # Set I2C standard mode
            time.sleep(0.01)

            self.__initialized_tofs.append(pin)
            Debug.info(None, "Initialized TOF" + str(pin))
        except Exception as e:
            Debug.warning(None, "Cant init TOF on pin " + str(pin) + " :" + str(e))

    def read_tof(self, pin: int) -> int:
        """
        read the distance of the tof sensor in mm
        :param pin: the pin number of the tof [1,2,3,4]
        :return: returns the distance
        """
        if pin not in [1, 2, 3, 4]:
            raise ValueError("Invalid value for 'pin'. Expected 1, 2, 3, or 4.")
        desired_address = TOF_ADDRESS + pin

        try:
            # Start a measurement
            self.bus.write_byte_data(desired_address , VL53L0X_REG_SYSRANGE_START, 0x01)
            time.sleep(0.01)

            # Read the distance
            """Read a word (2 bytes) of data from a specific register."""
            high = self.bus.read_byte_data(desired_address, VL53L0X_REG_RESULT_RANGE_STATUS + 10)
            low = self.bus.read_byte_data(desired_address, (VL53L0X_REG_RESULT_RANGE_STATUS + 10) + 1)
            return int((high << 8) + low)
        except Exception as e:
            Debug.error(None, "Cant read TOF on pin " + str(pin) + " :" + str(e))
            return -1

    def update_tof(self) -> None:
        """
        updates the tof distances without delay. The distance is delayed because of that
        :return:
        """
        desired_address = TOF_ADDRESS
        for i in self.__initialized_tofs:
            try:
                # Start a measurement
                self.bus.write_byte_data(desired_address + i, VL53L0X_REG_SYSRANGE_START, 0x01)

                # Read the distance
                """Read a word (2 bytes) of data from a specific register."""
                high = self.bus.read_byte_data(desired_address, VL53L0X_REG_RESULT_RANGE_STATUS + 10)
                low = self.bus.read_byte_data(desired_address, (VL53L0X_REG_RESULT_RANGE_STATUS + 10) + 1)

                self.distances[i + 1] = int((high << 8) + low)
            except Exception as e:
                Debug.error(None, "Cant read TOF on pin " + str(i) + " :" + str(e))


class IO:
    def __init__(self):
        self.func_callback = None
        self.mde_callback = None
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        #init inputs
        GPIO.setup(24, GPIO.IN)  # GPIO 24 Mode Button (SW3)
        GPIO.setup(25, GPIO.IN)  # GPIO 25 Restart Button (SW4)

        #interrupt
        GPIO.add_event_detect(25, GPIO.FALLING,
                              callback=self.restart_callback, bouncetime=100)
        GPIO.add_event_detect(24, GPIO.FALLING,
                              callback=self.mode_callback, bouncetime=100)

        # init GPIOs
        GPIO.setup(27, GPIO.OUT)  # GPIO 27 red light sensor
        GPIO.output(27, 0)
        GPIO.setup(22, GPIO.OUT)  # GPIO 22 green light sensor
        GPIO.output(22, 0)
        GPIO.setup(23, GPIO.OUT)  # GPIO 23 red status led
        GPIO.output(23, 0)
        #TOFS
        GPIO.setup(TOF1, GPIO.OUT)
        GPIO.output(TOF1, 1)
        GPIO.setup(TOF2, GPIO.OUT)
        GPIO.output(TOF2, 1)
        GPIO.setup(TOF3, GPIO.OUT)
        GPIO.output(TOF3, 1)
        GPIO.setup(TOF4, GPIO.OUT)
        GPIO.output(TOF4, 1)

    def restart_callback(self):
        Debug.okblue(None, "Restart Pressed")
        if self.func_callback is not None:
            self.func_callback()

    def mode_callback(self):
        Debug.okblue(None, "Mode Pressed")
        if self.mde_callback is not None:
            self.mde_callback()


    def set_sensor_leds(self, colour: int):
        """
        set the colour of the sensor leds
        :param colour: 0=off 1=red 2=green
        :return:
        """
        if colour==0 :
            GPIO.output(27, 0)
            GPIO.output(22, 0)
        elif colour == 1:
            GPIO.output(27, 1)
            GPIO.output(22, 0)
        elif colour == 2:
            GPIO.output(27, 0)
            GPIO.output(22, 1)
        else:
            Debug.warning(None, str(colour) + " is not a valid number for sensor colour!")


    def set(self, pin: int, state: int):
        GPIO.output(pin, state)

    def read(self, pin: int):
        return GPIO.input(pin)

    def cleanup(self):
        GPIO.cleanup()


class MCP3008:
    def __init__(self, bus=0, device=0):
        self.bus, self.device = bus, device
        self.spi = SpiDev()
        self.open()
        self.spi.max_speed_hz = 1000000  # 1MHz

    def open(self):
        self.spi.open(self.bus, self.device)
        self.spi.max_speed_hz = 1000000  # 1MHz

    def read(self, channel):
        channel = channel - 1
        cmd1 = 4 | 2 | ((channel & 4) >> 2)
        cmd2 = (channel & 3) << 6

        adc = self.spi.xfer2([cmd1, cmd2, 0])
        data = ((adc[1] & 15) << 8) + adc[2]
        return data

    def get_one(self, pin: int) -> int:
        """
        reads a specific sensor
        :return: returns the value
        """
        if isWindows:
            return -1
        return int(self.read(channel=pin))

    def get_greyscale(self, threshold: [int]) -> int:
        """
        reads all sensor datas
        :return: a 5 digit number, example: 11100 = BBBWW
        """
        if isWindows:
            return -1
        x = int(0)
        if int(self.read(channel=1)) > threshold[1]:
            x += 1  # RR
        if int(self.read(channel=2)) > threshold[2]:
            x += 10 # R
        if int(self.read(channel=3)) > threshold[3]:
            x += 100  # M
        if int(self.read(channel=4)) > threshold[4]:
            x += 1000  # L
        if int(self.read(channel=5)) > threshold[5]:
            x += 10000  # LL
        return x

    def close(self):
        self.spi.close()
