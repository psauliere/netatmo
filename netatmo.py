#!/usr/bin/env python3
"""netatmo.py
NetAtmo weather station display
Every 10 minutes, gets the weather station data to a
local data.json file, and calls display.py.
"""

import json
import requests
import time
import sys
import os
import logging

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)-15s | %(message)s'
)

import display

# JSON file names
config_filename = "config.json"
token_filename = "token.json"
data_filename = "data.json"

# Global variables
g_config = dict()
g_token = dict()
g_data = dict()

def timestr(t):
    return time.strftime("%H:%M:%S",time.localtime(t))

def nowstr():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

def read_json(filename):
    """Read a JSON file to a dict object."""
    with open(filename, 'r') as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            logging.warning("read_json() JSONDecodeError", exc_info=1)
            data = dict()
    return data

def write_json(data, filename):
    """Write a dict object to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f)

def authenticate():
    """NetAtmo API authentication. Result:  g_token and token.json file."""
    global g_token
    payload = {
        'grant_type': 'password',
        'username': g_config['username'],
        'password': g_config['password'],
        'client_id': g_config['client_id'],
        'client_secret': g_config['client_secret'],
        'scope': 'read_station'
    }
    try:
        response = requests.post("https://api.netatmo.com/oauth2/token", data=payload)
        logging.debug("%d %s", response.status_code, response.text)
        response.raise_for_status()
        g_token = response.json()
        write_json(g_token, token_filename)
        logging.info("authenticate() OK.")
    except requests.exceptions.HTTPError as e:
        logging.error("authenticate() HTTPError")
        logging.error("%d %s", e.response.status_code, e.response.text)
        logging.info("authenticate() exiting")
        sys.exit(1)
    except requests.exceptions.RequestException:
        logging.error("authenticate() RequestException", exc_info=1)
        logging.info("authenticate() exiting")
        sys.exit(1)

def refresh_token():
    """NetAtmo API token refresh. Result: g_token and token.json file."""
    global g_token
    global g_config
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': g_token['refresh_token'],
        'client_id': g_config['client_id'],
        'client_secret': g_config['client_secret'],
    }
    try:
        response = requests.post("https://api.netatmo.com/oauth2/token", data=payload)
        logging.debug("%d %s", response.status_code, response.text)
        response.raise_for_status()
        g_token = response.json()
        write_json(g_token, token_filename)
        logging.info("refresh_token() OK.")
    except requests.exceptions.HTTPError as e:
        logging.warning("refresh_token() HTTPError")
        logging.warning("%d %s", e.response.status_code, e.response.text)
        logging.info("refresh_token() calling authenticate()")
        authenticate()
    except requests.exceptions.RequestException:
        logging.error("refresh_token() RequestException", exc_info=1)

def get_station_data():
    """Gets Netatmo weather station data. Result: g_data and data.json file."""
    global g_token
    global g_config
    global g_data
    params = {
        'access_token': g_token['access_token'],
        'device_id': g_config['device_id']
    }
    try:
        response = requests.post("https://api.netatmo.com/api/getstationsdata", params=params)
        logging.debug("%d %s", response.status_code, response.text)
        response.raise_for_status()
        g_data = response.json()
        write_json(g_data, data_filename)    
    except requests.exceptions.HTTPError as e:
        logging.warning("get_station_data() HTTPError")
        logging.warning("%d %s", e.response.status_code, e.response.text)
        if e.response.status_code == 403:
            logging.info("get_station_data() calling refresh_token()")
            refresh_token()
            # retry
            logging.info("get_station_data() calling get_station_data()")
            get_station_data()
    except requests.exceptions.RequestException:
        logging.error("get_station_data() RequestException:", exc_info=1)

def display_console():
    """Displays weather data on the console. Input: g_data"""
    global g_data
    # console
    if "body" in g_data:
        device = g_data["body"]["devices"][0]
        indoor = device["dashboard_data"]
        outdoor = device["modules"][0]["dashboard_data"]
        rain = device["modules"][1]["dashboard_data"]
        displaystr = (
            "Pressure " + str(indoor["Pressure"]) + " | " +
            "Indoor " + str(indoor["Temperature"]) + " | " +
            "Outdoor " + str(outdoor["Temperature"]) + " | " +
            "Rain " + str(rain["Rain"])
        )
        logging.info(displaystr)

def main():
    """Main function"""
    global g_token
    global g_config
    global g_data
    print("netatmo.py v0.14 2019-10-02")

    # read config
    if os.path.isfile(config_filename):
        g_config = read_json(config_filename)
    else:
        g_config = {'username': 'xx', 'password': 'xx',
            'client_id': 'xx', 'client_secret': 'xx', 'device_id': 'xx'}
        write_json(g_config, config_filename)
        logging.error("main() error:")
        logging.error("config file not found: creating an empty one.")
        logging.error("Please edit %s and try again.", config_filename)
        return

    # read last token    
    if os.path.isfile(token_filename):
        g_token = read_json(token_filename)
    else:
        authenticate()

    # read last data
    if os.path.isfile(data_filename):
        g_data = read_json(data_filename)

    # main loop
    while True:
        get_station_data()
        display_console()
        display.main()
        try:
            # sleep 10 minutes
            time.sleep(600)
        except KeyboardInterrupt:
            # Crtl+C
            logging.info("Keyboard exception received. Exiting.")
            return

if __name__ == '__main__':
    main()
