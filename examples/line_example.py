from robotsystem.robot import *

def setup():
    """
    your setup code here
    """
    Robot.Debug.msg("This is the line-following example...")
    Robot.set_threshold(LL, 2350)
    Robot.set_threshold(L, 2350)
    Robot.set_threshold(M, 2350)
    Robot.set_threshold(R, 2350)
    Robot.set_threshold(RR, 2350)
    Robot.set_motor_driver(True)


def loop():
    """
    your logic code here
    """
    x = Robot.grayscale
    # LL L M R RR
    #  0 0 0 0 0

    if x == 100: # 0 0 1 0 0
        Robot.move(2000,2000,2000,2000)
    elif x == 1100 or x == 1000 or x == 11000:
        Robot.move(3000,3000,1000,1000)
    elif x == 110 or x == 10 or x == 11:
        Robot.move(1000,1000,3000,3000)

    Robot.delay(50)
    if Robot.get_switch_value(3) == 0:
        Robot.move(0, 0, 0, 0)
        Robot.delay(500)
        while Robot.get_switch_value(3):
            Robot.delay(100)
        Robot.set_mode_led_on(True)
        Robot.Debug.okblue("Restarting... ")
        Robot.delay(500)
        Robot.set_mode_led_on(False)

if __name__ == "__main__":
    Robot = Robot_()
    setup()
    Robot.Debug.okblue("Setup Complete...")
    try:
        while True:
            Robot.update()
            loop()
    except BaseException as e:
        Robot.Debug.error_imp("Stopped: " + str(e))
        Robot.terminate()
        exit(42)
