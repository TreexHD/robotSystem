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
        if not isWindows:
            self.MCP3008 = robotsystem.bus.MCP3008()
            self.IO = robotsystem.bus.IO()

    def terminate(self):
        """
        terminates the whole process correctly
        :return:
        """
        self.IO.cleanup()
        return

    def get_io(self):
        """
        get the IO object
        :return:
        """
        return self.IO

    def get_greyscale(self) -> int:
        """
        reads all sensor datas
        :return: a 5 digit number, example: 11100 = BBBWW
        """
        if isWindows:
            return -1
        x = int(0)
        if int(self.MCP3008.read(channel=LL)) > self.threshold[LL]:
            x += 10000  # LL
        if int(self.MCP3008.read(channel=L)) > self.threshold[L]:
            x += 1000  # L
        if int(self.MCP3008.read(channel=M)) > self.threshold[M]:
            x += 100  # M
        if int(self.MCP3008.read(channel=R)) > self.threshold[R]:
            x += 10  # R
        if int(self.MCP3008.read(channel=RR)) > self.threshold[RR]:
            x += 1  # RR
        return x


