import time
from yeelight import Bulb
import pyscreenshot
import _thread
from phue import Bridge
from rgbxy import Converter
from rgbxy import GamutA, GamutB, GamutC
from blinkstick import blinkstick

GAMUTS = {
    'LCT001': {
        'name': 'Hue bulb A19',
        'gamut': 'B'
    },
    'LCT007': {
        'name': 'Hue bulb A19',
        'gamut': 'B'
    },
    'LCT010': {
        'name': 'Hue bulb A19',
        'gamut': 'C'
    },
    'LCT014': {
        'name': 'Hue bulb A19',
        'gamut': 'C'
    },
    'LCT002': {
        'name': 'Hue Spot BR30',
        'gamut': 'B'
    },
    'LCT003': {
        'name': 'Hue Spot GU10',
        'gamut': 'B'
    },
    'LCT011': {
        'name': 'Hue BR30',
        'gamut': 'C'
    },
    'LST001': {
        'name': 'Hue LightStrips',
        'gamut': 'A'
    },
    'LLC010': {
        'name': 'Hue Living Colors Iris',
        'gamut': 'A'
    },
    'LLC011': {
        'name': 'Hue Living Colors Bloom',
        'gamut': 'A'
    },
    'LLC012': {
        'name': 'Hue Living Colors Bloom',
        'gamut': 'A'
    },
    'LLC006': {
        'name': 'Living Colors Gen3 Iris*',
        'gamut': 'A'
    },
    'LLC007': {
        'name': 'Living Colors Gen3 Bloom, Aura*',
        'gamut': 'A'
    },
    'LLC013': {
        'name': 'Disney Living Colors',
        'gamut': 'A'
    },
    'LLM001': {
        'name': 'Color Light Module',
        'gamut': 'A'
    },
    'LLC020': {
        'name': 'Hue Go',
        'gamut': 'C'
    },
    'LST002': {
        'name': 'Hue LightStrips Plus',
        'gamut': 'C'
    },
}

HUE = Bridge('philips-hue')
HUE.connect()

HUE_API = HUE.get_api()
HUE_LIGHTS = HUE.get_light_objects('name')

GAMUT_A_CONVERTER = Converter(GamutA)
GAMUT_B_CONVERTER = Converter(GamutB)
GAMUT_C_CONVERTER = Converter(GamutC)

LOW_THRESHOLD = 10
MID_THRESHOLD = 40
HIGH_THRESHOLD = 240


def get_gamut(modelid):
    return GAMUTS[modelid]['gamut']


def update_hue_light(light, hue_color, hue_darkness_ratio):
    try:
        gamut = get_gamut(light['modelid'])

        converted_color = None

        if gamut == 'A':
            converted_color = GAMUT_A_CONVERTER.rgb_to_xy(hue_color[0], hue_color[1], hue_color[2])

        if gamut == 'B':
            converted_color = GAMUT_B_CONVERTER.rgb_to_xy(hue_color[0], hue_color[1], hue_color[2])

        if gamut == 'C':
            converted_color = GAMUT_C_CONVERTER.rgb_to_xy(hue_color[0], hue_color[1], hue_color[2])

        HUE_LIGHTS[light['name']].brightness = int(254 * ((100 - hue_darkness_ratio) / 100))
        HUE_LIGHTS[light['name']].xy = converted_color
    except:
        pass


def update_hue(hue_color, hue_darkness_ratio):
    for key, light in HUE_API['lights'].items():
        if ('desk spot' in light['name'].lower()) or ('tv spot' in light['name'].lower()):
            _thread.start_new_thread(update_hue_light, (light, hue_color, hue_darkness_ratio))

def get_color():
    dark_pixels = 1
    mid_range_pixels = 1
    total_pixels = 1
    r = 1
    g = 1
    b = 1

    img = pyscreenshot.grab()
    img = img.resize((16, 9))

    # Create list of pixels
    pixels = list(img.getdata())

    for red, green, blue in pixels:
        # Don't count pixels that are too dark
        if red < LOW_THRESHOLD and green < LOW_THRESHOLD and blue < LOW_THRESHOLD:
            dark_pixels += 1
        # Or too light
        elif red > HIGH_THRESHOLD and green > HIGH_THRESHOLD and blue > HIGH_THRESHOLD:
            pass
        else:
            if red < MID_THRESHOLD and green < MID_THRESHOLD and blue < MID_THRESHOLD:
                mid_range_pixels += 1
                dark_pixels += 1
            r += red
            g += green
            b += blue
        total_pixels += 1

    n = len(pixels)
    r_avg = r / n
    g_avg = g / n
    b_avg = b / n
    rgb = [r_avg, g_avg, b_avg]

    # If computed average below darkness threshold, set to the threshold
    for index, item in enumerate(rgb):
        if item <= LOW_THRESHOLD:
            rgb[index] = LOW_THRESHOLD

    rgb = (rgb[0], rgb[1], rgb[2])

    data = {
        'rgb': rgb,
        'dark_ratio': float(dark_pixels) / float(total_pixels) * 100
    }

    return data


def update_yeelight(light, yeelight_color, yeelight_darkness_ratio):
    try:
        light.set_rgb(int(yeelight_color[0]), int(yeelight_color[1]), int(yeelight_color[2]))
        light.set_brightness(int(100 - yeelight_darkness_ratio))
    except:
        pass


def update_blinkstick(blinkstick_color, blinkstick_darkness_ratio):
    try:
        for stick in blinkstick.find_all():

            blink_red = int(blinkstick_color[0]) - (100 - blinkstick_darkness_ratio)
            blink_green = int(blinkstick_color[1]) - (100 - blinkstick_darkness_ratio)
            blink_blue = int(blinkstick_color[2]) - (100 - blinkstick_darkness_ratio)

            if blink_blue < 0:
                blink_blue = 0

            if blink_red < 0:
                blink_red = 0

            if blink_green < 0:
                blink_green = 0

            for x in range(7):
                stick.set_color(channel=0, red=blink_red, green=blink_green, blue=blink_blue, index=x)
    except:
        pass


if __name__ == '__main__':
    yeelight = Bulb('10.70.2.8', duration=300)
    properties = yeelight.get_properties()

    if properties['music_on'] == '0':
        yeelight.start_music()

    while True:
        try:
            color = get_color()
            darkness_ratio = color['dark_ratio']
            color = color['rgb']

            # hue
            _thread.start_new_thread(update_hue, (color, darkness_ratio))

            # Yeelight
            _thread.start_new_thread(update_yeelight, (yeelight, color, darkness_ratio))

            # Blinkstick
            _thread.start_new_thread(update_blinkstick, (color, darkness_ratio))
        except Exception as e:
            pass

        time.sleep(0.1)
