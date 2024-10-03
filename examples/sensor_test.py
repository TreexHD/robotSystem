from robotsystem.robot import *


def setup():
    """
    your setup code here
    """
    Robot.Debug.msg("This is the sensor-test example...")



def loop():
    """
    your logic code here
    """
    Robot.delay(500)
    Robot.Debug.msg("TOFs: " + str(Robot.distances[1:]))
    Robot.Debug.msg("Grayscale: " + str(Robot.grayscale))
    Robot.Debug.msg("SW3 : " + str(Robot.get_switch_value(3)))
    Robot.Debug.msg("SW3 : " + str(Robot.get_switch_value(4)))

if __name__ == "__main__":
    Robot = Robot_()
    setup()
    Robot.Debug.okblue("Setup Complete...")
    try:
        while True:
            loop()
            #Robot.update()
    except BaseException as e:
        Robot.Debug.error_imp("Stopped: " + str(e))
        Robot.terminate()
        exit(42)
