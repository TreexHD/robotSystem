import robotsystem.robot


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
    Robot = robotsystem.robot.Robot()
    setup()
    Robot.Debug.okblue("Setup Complete...")
    try:
        while True:
            loop()
            Robot.update()
    except BaseException as e:
        Robot.Debug.error_imp("Stopped: " + str(e))
        Robot.terminate()
        exit(42)
