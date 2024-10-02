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

#Registers of PCA9685
MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06

class I2C:  # NANO ADDRESS 0x08
    def __init__(self, io):
        self.io = io
        self.bus = smbus.SMBus(1)
        self.distances = [None, -1, -1, -1, -1]  # The distances of the TOF sensors

        #locals
        self.__initialized_tofs = []

        #actions
        self.init_all_tofs()
        self.initialize_pca9685()

        time.sleep(1)
        Debug.info("SMBus ready (I2C)")

    def initialize_pca9685(self):
        # Initialize the PCA9685 chip
        self.bus.write_byte_data(PCA9685_ADDRESS, MODE1, 0x00)  # Normal mode
        self.set_pwm_freq_pca9685(50)  # Set frequency to 50Hz

    def set_pwm_freq_pca9685(self, freq_hz):
        # Set the PWM frequency
        prescale_val = int(25000000.0 / (4096 * freq_hz) - 1)
        old_mode = self.bus.read_byte_data(PCA9685_ADDRESS, MODE1)
        new_mode = (old_mode & 0x7F) | 0x10  # Sleep
        self.bus.write_byte_data(PCA9685_ADDRESS, MODE1, new_mode)
        self.bus.write_byte_data(PCA9685_ADDRESS, PRESCALE, prescale_val)
        self.bus.write_byte_data(PCA9685_ADDRESS, MODE1, old_mode)
        time.sleep(0.005)
        self.bus.write_byte_data(PCA9685_ADDRESS, MODE1, old_mode | 0x80)

    def set_pwm_pca9685(self, channel: int, on: int, off: int):
        # Set the PWM value for a specific channel
        self.bus.write_byte_data(PCA9685_ADDRESS, LED0_ON_L + 4 * channel, on & 0xFF)
        self.bus.write_byte_data(PCA9685_ADDRESS, LED0_ON_L + 4 * channel + 1, on >> 8)
        self.bus.write_byte_data(PCA9685_ADDRESS, LED0_ON_L + 4 * channel + 2, off & 0xFF)
        self.bus.write_byte_data(PCA9685_ADDRESS, LED0_ON_L + 4 * channel + 3, off >> 8)

    def write_data(self, address, first, second, third):
        data = [first, second, third]
        # Debug.msg("Sending data:" + str(data))
        try:
            self.bus.write_i2c_block_data(address, 0, data)
        except Exception as e:
            Debug.error("Error sending I2C data: " + str(e))

    def init_all_tofs(self):
        for i in range(4):
            try:
                self.init_tof(i + 1)
            except:
                Debug.msg("No TOF at PIN: " + str(i + 1))

    def init_tof(self, pin: int):
        """
        initialize a connected tof sensor
        :param pin: the pin number of the tof [1,2,3,4]
        """
        if pin not in [1, 2, 3, 4]:
            raise ValueError("Invalid value for 'pin'. Expected 1, 2, 3, or 4.")
        default_address = 0x29
        desired_address = 0x29 + pin

        if pin == 1:
            self.io.set(TOF2, 0)
            self.io.set(TOF3, 0)
            self.io.set(TOF4, 0)
        elif pin == 2:
            self.io.set(TOF1, 0)
            self.io.set(TOF3, 0)
            self.io.set(TOF4, 0)
        elif pin == 3:
            self.io.set(TOF1, 0)
            self.io.set(TOF2, 0)
            self.io.set(TOF4, 0)
        elif pin == 4:
            self.io.set(TOF1, 0)
            self.io.set(TOF2, 0)
            self.io.set(TOF3, 0)

        time.sleep(0.01)

        try:
            # Change address of tof
            self.bus.write_byte_data(default_address, 0x212, desired_address)

            # INIT the sensor
            self.bus.write_byte_data(desired_address, 0x0207, 0x01)  # SYSTEM__FRESH_OUT_OF_RESET
            self.bus.write_byte_data(desired_address, 0x0208, 0x01)  # SYSTEM__FRESH_OUT_OF_RESET
            self.bus.write_byte_data(desired_address, 0x0096, 0x00)  # SYSTEM__MODE_GPIO1
            self.bus.write_byte_data(desired_address, 0x0097, 0xfd)  # SYSTEM__MODE_GPIO1
            self.bus.write_byte_data(desired_address, 0x00e3, 0x00)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x00e4, 0x04)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x00e5, 0x02)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x00e6, 0x01)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x00e7, 0x03)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x00f5, 0x02)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x00d9, 0x05)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x00db, 0xce)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x00dc, 0x03)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x00dd, 0xf8)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x009f, 0x00)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x00a3, 0x3c)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x00b7, 0x00)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x00bb, 0x3c)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x00b2, 0x09)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x00ca, 0x09)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x0198, 0x01)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x01b0, 0x17)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x01ad, 0x00)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x00ff, 0x05)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x0100, 0x05)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x0199, 0x05)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x01a6, 0x1b)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x01ac, 0x3e)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x01a7, 0x1f)  # SYSTEM__MODE_GPIO0
            self.bus.write_byte_data(desired_address, 0x0030, 0x00)  # SYSTEM__MODE_GPIO0
            self.__initialized_tofs.append(pin)
            Debug.msg("Initialized TOF" + str(pin))
        except Exception as e:
            Debug.error("Cant init TOF on pin " + str(pin) + " :" + str(e))
            raise

        self.io.set(TOF1, 1)
        self.io.set(TOF2, 1)
        self.io.set(TOF3, 1)
        self.io.set(TOF4, 1)

    def read_tof(self, pin: int) -> int:
        """
        read the distance of the tof sensor in mm
        :param pin: the pin number of the tof [1,2,3,4]
        :return: returns the distance
        """
        if pin not in [1, 2, 3, 4]:
            raise ValueError("Invalid value for 'pin'. Expected 1, 2, 3, or 4.")
        desired_address = 0x29 + pin

        try:
            self.bus.write_byte_data(desired_address, 0x0180, 0x01)  # SYSRANGE__START
            time.sleep(0.01)  # WAIT
            distance = int(self.bus.read_byte_data(desired_address, 0x062))  # RESULT__RANGE_VAL
            return distance
        except Exception as e:
            Debug.error("Cant read TOF on pin " + str(pin) + " :" + str(e))
            return -1

    def update_tof(self) -> None:
        """
        updates the tof distances without delay. The distance is delayed because of that
        :return:
        """
        desired_address = 0x29
        for i in self.__initialized_tofs:
            try:
                self.bus.write_byte_data(desired_address + i, 0x0180, 0x01)  # SYSRANGE__START
                self.distances[i + 1] = int(self.bus.read_byte_data(desired_address + i, 0x062))  # RESULT__RANGE_VAL
            except Exception as e:
                Debug.error("Cant read TOF on pin " + str(i) + " :" + str(e))


class IO:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

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

        GPIO.setup(25, GPIO.IN)  # GPIO 25 Restart Button

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
            Debug.warning(str(colour) + " is not a valid number for sensor colour!")


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
            x += 10000  # LL
        if int(self.read(channel=2)) > threshold[2]:
            x += 1000  # L
        if int(self.read(channel=3)) > threshold[3]:
            x += 100  # M
        if int(self.read(channel=4)) > threshold[4]:
            x += 10  # R
        if int(self.read(channel=5)) > threshold[5]:
            x += 1  # RR
        return x

    def close(self):
        self.spi.close()
