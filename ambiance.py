from PIL import Image
from yeelight import Bulb
import pyscreenshot as ImageGrab
import time
from colorthief import ColorThief

coloring = ColorThief('./picture.png')

bulb = Bulb("10.70.2.8")
bulb.ensure_on()
bulb.start_music()

bulb.set_rgb(255, 255, 255)
time.sleep(0.5)
bulb.set_rgb(0, 255, 0)
time.sleep(0.5)
bulb.set_rgb(255, 0, 255)
time.sleep(0.5)
bulb.set_rgb(255, 255, 0)
time.sleep(0.5)

"""
:type image: PIL.Image
"""


def color():
    image = ImageGrab.grab(bbox=(1920, 0, 3840, 1080))
    image = image.resize((200, 200), Image.DEFAULT_STRATEGY)
    coloring.image = image

    tuple = coloring.get_color(5)

    if (tuple[0] < 30 and tuple[1] < 30 and tuple[2] < 30):
        bulb.set_brightness(0)
        return

    bulb.set_brightness(100)
    bulb.set_rgb(tuple[0], tuple[1], tuple[2])


try:

    while True:
        color()

except KeyboardInterrupt:
    bulb.stop_music()
    print('End!')

