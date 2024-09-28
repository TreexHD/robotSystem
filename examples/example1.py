import robotsystem.robot


def setup():
    """
    your setup code here
    """
    Robot.Debug.okblue("Setup Complete...")


def loop():
    """
    your logic code here
    """


if __name__ == "__main__":
    Robot = robotsystem.robot.Robot()
    setup()
    try:
        while True:
            loop()
    except BaseException as e:
        Robot.Debug.error_imp("Stopped: " + str(e))
        exit(42)
