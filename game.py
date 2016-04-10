import subprocess
import cv2
import numpy as np
from time import time

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 1920
HALF_SCREEN_WIDTH = SCREEN_WIDTH / 2

RIM_WIDTH = 300
HALF_RIM_WIDTH = RIM_WIDTH / 2


NET_WIDTH = 596
HALF_NET_WIDTH = NET_WIDTH / 2

BALL_WIDTH = 258
HALF_BALL_WIDTH = BALL_WIDTH / 2

NET_Y = 600
BALL_Y = 1540

VELOCITY_THRESHOLD = 200
SECOND_VELOCITY_THRESHOLD = 350

round = 0

class IAintDoingThat(Exception):
    pass

def screenshot():
    #global i
    subprocess.call("./get_screenshot.sh", shell=True)
    # subprocess.call("cp screen.png screen_{}.png".format(i), shell=True)
    #i += 1
    return cv2.imread("screen.png")

def get_basketball_position(image):
    """Gets the x position of the basketball, normalized from 0 to 100."""
    def _is_pixel_gray(pixel):
        return sum(pixel) == 244 * 3

    # just get, like, one slice of the basketball
    basketball_region = image[1679:1780, 0:1080].tolist()[0]

    first_orange_pixel = None
    for i, pixel in enumerate(basketball_region):
        if not _is_pixel_gray(pixel):
            return i + HALF_BALL_WIDTH, BALL_Y
    raise IAintDoingThat()

def get_net_position(image):
    def _is_pixel_white(pixel):
        return sum(pixel) == 255 * 3

    net_region = image[499:500, 0:1080].tolist()[0]

    for i, pixel in enumerate(net_region):
        if not _is_pixel_white(pixel):
            return i + HALF_NET_WIDTH, NET_Y
    raise Error()

def get_net_velocity(start, end, dt):
    x0, y0 = start
    x1, y1 = end
    dx, dy = (x1 - x0) / dt, (y1 - y0) / dt

    print "dx:{}, dy:{}".format(dx, dy)
    if round < 10:
        return 0, 0
    elif round < 20:
        if abs(dx) < VELOCITY_THRESHOLD:
            raise IAintDoingThat()
        return (220, 0) if dx > 0 else (-220, 0)
    elif round < 40:
        if abs(dx) < SECOND_VELOCITY_THRESHOLD:
            raise IAintDoingThat()
        return (440, 0) if dx > 0 else (-440, 0)
    raise IndexError()


def predict_net_position(coords, dx, dy, t):
    x, y = coords
    fx, fy = x + (t * dx), y + (t * dy)
    if fx < HALF_RIM_WIDTH:
        fx = RIM_WIDTH - fx
    if fx > SCREEN_WIDTH - HALF_RIM_WIDTH:
        fx = 2 * SCREEN_WIDTH - RIM_WIDTH - fx
    return fx, fy

def shoot(x, y, image):
    bx, by = get_basketball_position(image)
    start = time()
    flop = "adb shell input swipe {0} {1} {2} {3} 50".format(bx, by, x, y)
    subprocess.call(flop, shell=True)
    end = time()
    dtt = end - start
    print('time to shoot: {}'.format(dtt))


if __name__ == "__main__":
    while True:
        second_most_recent_screenshot = screenshot()
        start_time = time()
        most_recent_screenshot = screenshot()
        end_time = time()
        dt = end_time - start_time
        #print('time between snapshots: {}'.format(dt))

        start_net_coords = get_net_position(second_most_recent_screenshot)
        end_net_coords = get_net_position(most_recent_screenshot)

        #print "start: ({},{}) end: ({},{})".format(start_net_coords[0], start_net_coords[1], end_net_coords[0], end_net_coords[1])
        try:
            dx, dy = get_net_velocity(start_net_coords, end_net_coords, dt)
            x, y = predict_net_position(end_net_coords, dx, dy, 1.8)
            #print "predict: ({},{})".format(x, y)
            shoot(x, y, most_recent_screenshot)
            round += 1
        except IAintDoingThat:
            print("hello")
            continue
