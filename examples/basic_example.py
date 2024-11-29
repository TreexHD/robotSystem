from robotsystem.robot import *



def setup():
    """
    your setup code here
    """
    Robot.Debug.msg("Hello World")


def loop():
    """
    your logic code here
    """


if __name__ == "__main__":
    Robot = Robot_()
    setup()
    Robot.init()
    Robot.Debug.okblue("Setup Complete...")
    try:
        while True:
            Robot.update()
            loop()
    except BaseException as e:
        Robot.Debug.error_imp("Stopped: " + str(e))
        Robot.terminate()
        exit(42)
