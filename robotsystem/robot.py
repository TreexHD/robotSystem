"""
this is the main module
"""
import platform
if platform.system() == "Linux":
    from spidev import SpiDev
    import smbus
    import RPi.GPIO as GPIO
import robotsystem.debug


class Robot:

    config = {
        "threshold": [0, 2350, 2350, 2350, 2350, 2350, 3900, 3900]
    }
    Debug = robotsystem.debug.Debug

    def __init__(self):
        pass

