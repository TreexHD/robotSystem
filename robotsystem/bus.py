import time


class I2C:  # NANO ADDRESS 0x08
    def __init__(self):
        self.bus = smbus.SMBus(1)
        time.sleep(1)
        Debug.info("SMBus ready")

    def write_data(self, address, first, second, third):
        data = [first, second, third]
        # Debug.msg("Sending data:" + str(data))
        try:
            self.bus.write_i2c_block_data(address, 0, data)
        except Exception as e:
            Debug.error("Error sending I2C data: " + str(e))


class IO:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        # init GPIOs
        GPIO.setup(27, GPIO.OUT)  # GPIO 27 red light sensor
        GPIO.output(27, 1)
        GPIO.setup(22, GPIO.OUT)  # GPIO 22 green light sensor
        GPIO.output(22, 1)
        GPIO.setup(23, GPIO.OUT)  # GPIO 23 red status led
        GPIO.output(23, 0)

        GPIO.setup(25, GPIO.IN)  # GPIO 25 Restart Button

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

    def close(self):
        self.spi.close()