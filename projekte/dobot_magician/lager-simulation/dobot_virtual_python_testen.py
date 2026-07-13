import dobot_virtual_python as dobot


def mein_programm(robot):
    robot.home()
    robot.move_xy(182, 162)
    robot.suction(True)
    robot.wait(0.5)

    robot.move_xy(246, 162)
    robot.suction(False)

    for winkel in [-30, 0, 30, 0]:
        robot.movej(joint1=winkel)
        robot.wait(0.2)


dobot.run(mein_programm)