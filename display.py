#!/usr/bin/env python3
"""display.py
Displays NetAtmo weather station data on a local screen
input: data.json file, result of NetAtmo getstationsdata API
screen: PaPiRus ePaper / eInk Screen HAT for Raspberry Pi - 2.7"
output: copy of the screen in file: image.bmp
"""

import json
import time
import os
import sys
import logging
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

logging.basicConfig(level=logging.WARNING)

WHITE = 1
BLACK = 0
# Font file
font_file = '/usr/share/fonts/truetype/freefont/FreeSans.ttf'
if not os.path.isfile(font_file):
    font_file = '../freefont/FreeSans.ttf'
    if not os.path.isfile(font_file):
        exit()
# File names
data_filename = 'data.json'
image_filename = 'image.bmp'
# Global variables
g_data = dict()
g_image = None

def datetimestr(t):
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(t))

def timestr(t):
    return time.strftime('%H:%M',time.localtime(t))

def read_json(filename):
    """Read a JSON file to a dict object."""
    with open(filename, 'r') as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            data = dict()
    return data

def trend_symbol(trend):
    """Unicode symbol for temperature trend"""
    if trend == 'up':
        return '\u2197' # '↗' U+2197
    elif trend == 'down':
        return '\u2198' # '↘' U+2198
    elif trend == 'stable':
        return '\u2192' # '→' U+2192
    else:
        return ' '

def draw_image():
    """Draws the image in memory (g_image)"""
    global g_data
    global g_image

    # prepare for drawing
    draw = ImageDraw.Draw(g_image)
    width, height = g_image.size

    # base font size on mono spaced font
    font_size_temp = int((width - 4) / (10 * 0.65))     # room for 10 chars
    font_temp = ImageFont.truetype(font_file, font_size_temp)
    font_size_time = int((width - 10) / (20 * 0.65))    # YYYY-MM-DD HH:MM:SS
    font_time = ImageFont.truetype(font_file, font_size_time)

    # read data
    if os.path.isfile(data_filename):
        g_data = read_json(data_filename)
    else:
        logging.error("No data file")
        sys.exit(1)
    if not ("body" in g_data):
        logging.error("Bad data format")
        sys.exit(1)

    # extract data
    user_admin = g_data["body"]["user"]["administrative"]
    device = g_data["body"]["devices"][0]
    #place = device["place"]
    indoor = device["dashboard_data"]
    outdoor = device["modules"][0]["dashboard_data"]
    rain = device["modules"][1]["dashboard_data"]

    # Units
    # see https://dev.netatmo.com/en-US/resources/technical/reference/weather/getstationsdata
    # for details
    unit_temp = ['°C', '°F'][user_admin["unit"]]
    unit_rain = ['mm/h', 'in/h'][user_admin["unit"]]
    # Uncomment if needed
    #unit_wind = ['kph', 'mph', 'm/s', 'beaufort', 'knot'][user_admin["windunit"]]
    #unit_pressure = ['mbar', 'inHg', 'mmHg'][user_admin["pressureunit"]]

    # get and format values
    data_time_str = timestr(g_data["time_server"])
    indoor_temp_str = '{0:.2f}'.format(indoor["Temperature"]) + " " + unit_temp + trend_symbol(indoor["temp_trend"])
    outdoor_temp_str = '{0:.2f}'.format(outdoor["Temperature"]) + " " + unit_temp + trend_symbol(outdoor["temp_trend"])
    rain_str = '{0:.1f}'.format(rain["Rain"]) + " " + unit_rain

    # width and height of strings
    (width_indoor, height_indoor) = draw.textsize(indoor_temp_str, font=font_temp)
    (width_outdoor, height_outdoor) = draw.textsize(outdoor_temp_str, font=font_temp)
    (width_rain, height_rain) = draw.textsize(rain_str, font=font_temp)
    (width_time, height_time) = draw.textsize(data_time_str, font=font_time)

    # which is bigger?
    txtwidth, txtheight = width_indoor, height_indoor
    if width_outdoor > txtwidth:
        txtwidth = width_outdoor
    if width_rain > txtwidth:
        txtwidth = width_rain

    x = int((width - txtwidth) / 2)
    y = int((height - 3*txtheight - 10) / 2)

    draw.rectangle((2, 2, width - 2, height - 2), fill=WHITE, outline=BLACK)
    # temperature and rain
    draw.text((x, y), indoor_temp_str, fill=BLACK, font=font_temp)
    draw.text((x, y + txtheight + 5), outdoor_temp_str, fill=BLACK, font = font_temp)
    draw.text((x, y + 2*txtheight + 10), rain_str, fill=BLACK, font = font_temp)
    # time
    draw.text((width - width_time - 5, 5), data_time_str, fill = BLACK, font = font_time)

def main():
    """Main function"""
    global g_image

    try:
        # *** PaPiRus ePaper / eInk Screen HAT for Raspberry Pi - 2.7" ***
        from papirus import Papirus
        papirus = Papirus(rotation = 0)
        g_image = Image.new('1', papirus.size, WHITE)
        draw_image()
        g_image.save(image_filename)
        papirus.display(g_image)
        papirus.update()
        return
    except:
        logging.info("Papirus failed.", exc_info=1)
        pass

    try:
        # *** Waveshare 2.7inch e-Paper HAT ***
        libdir = os.path.realpath(os.getenv('HOME') + '/e-Paper/RaspberryPi&JetsonNano/python/lib')
        if os.path.exists(libdir):
            sys.path.append(libdir)
        from waveshare_epd import epd2in7
        epd = epd2in7.EPD()
        epd.init()
        g_image = Image.new('1', (epd.height, epd.width), 255)
        draw_image()
        g_image.save(image_filename)
        epd.display(epd.getbuffer(g_image))
        epd.sleep()
        return
    except:
        logging.info("Waveshare failed.", exc_info=1)
        pass

    # *** no known screen: just save the bmp
    logging.info("No known screen.")
    g_image = Image.new('1', (264, 176), WHITE)
    draw_image()
    g_image.save(image_filename)

# main
if "__main__" == __name__:
        main()
