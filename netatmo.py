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

logging.basicConfig(level = logging.INFO, format = '%(asctime)-15s | %(message)s')

# JSON file names
config_filename = "config.json"
token_filename = "token.json"
data_filename = "data.json"

# Global variables
g_config = dict()
g_token = dict()
g_data = dict()

def timestr(t):
    return time.strftime("%H:%M",time.localtime(t))

#def nowstr():
#    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

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
        json.dump(data, f, indent = 2)

#def authenticate():
#    """NetAtmo API authentication. Result:  g_token and token.json file."""
#    global g_token
#    payload = {
#        'grant_type': 'password',
#        'username': g_config['username'],
#        'password': g_config['password'],
#        'client_id': g_config['client_id'],
#        'client_secret': g_config['client_secret'],
#        'scope': 'read_station'
#    }
#    try:
#        response = requests.post("https://api.netatmo.com/oauth2/token", data=payload)
#        logging.debug("%d %s", response.status_code, response.text)
#        response.raise_for_status()
#        g_token = response.json()
#        write_json(g_token, token_filename)
#        logging.info("authenticate() OK.")
#    except requests.exceptions.HTTPError as e:
#        logging.error("authenticate() HTTPError")
#        logging.error("%d %s", e.response.status_code, e.response.text)
#        #logging.info("authenticate() exiting")
#        #sys.exit(1)
#    except requests.exceptions.RequestException:
#        logging.error("authenticate() RequestException", exc_info=1)
#        #logging.info("authenticate() exiting")
#        #sys.exit(1)

def get_new_token():
    """Instruct the user to authenticate on the dev portal and get a new token."""
    if not os.path.isfile(token_filename):
        g_token = {"access_token": "xxxx", "refresh_token": "xxxx"}
        write_json(g_token, token_filename)

    logging.error('_______________________________________________________')
    logging.error("Please generate a new access token, edit %s,", token_filename)
    logging.error("and try again.")
    logging.error(' - Go to https://dev.netatmo.com/apps/, authenticate')
    logging.error('   if necessary, and select your app.')
    logging.error(' - Under "Token generator", select the "read_station"')
    logging.error('   scope and click "Generate Token".')
    logging.error(' - It takes a while, but you will get a page where you')
    logging.error('   have to authorize your app to access to your data.')
    logging.error(' - Click "Yes I accept".')
    logging.error('   You now have a new Access Token and a new Refresh')
    logging.error('   token.')
    logging.error(' - Click on the access token. It will copy it to your')
    logging.error('   clipboard. Paste it in your %s file in place', token_filename)
    logging.error('   of the access_token placeholder.')
    logging.error(' - same thing for the refresh token.')
    logging.error(' - save the %s file.', token_filename)
    logging.error('_______________________________________________________')
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
        #if e.response.status_code == 403:
        #    logging.info("refresh_token() calling authenticate()")
        #    authenticate()
        logging.warning("refresh_token() failed. Need a new access token.")
        get_new_token()
        return
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
            logging.info("get_station_data() retrying")
            get_station_data()
    except requests.exceptions.RequestException:
        logging.error("get_station_data() RequestException:", exc_info=1)

def display_console():
    """Displays weather data on the console. Input: g_data"""
    global g_data
    # console
    displaystr = "No data"
    if "body" in g_data:
        displaystr = "Time " + timestr(g_data["time_server"])
        device = g_data["body"]["devices"][0]
        if "dashboard_data" in device:
            if "Pressure" in device["dashboard_data"]:
                displaystr += " | Pressure " + str(device["dashboard_data"]["Pressure"])
            if "Temperature" in device["dashboard_data"]:
                displaystr += " | Indoor " + str(device["dashboard_data"]["Temperature"])
        for module in device["modules"]:
            if "dashboard_data" in module:
                module_type = module["type"]
                if module_type == "NAModule1":
                    # Outdoor Module
                    if "Temperature" in module["dashboard_data"]:
                        displaystr += " | Outdoor " + str(module["dashboard_data"]["Temperature"])
                elif module_type == "NAModule2":
                    # Wind Gauge
                    if "WindStrength" in module["dashboard_data"]:
                        displaystr += " | Wind " + str(module["dashboard_data"]["WindStrength"])
                    if "WindAngle" in module["dashboard_data"]:
                        displaystr += " angle " + str(module["dashboard_data"]["WindAngle"])
                elif module_type == "NAModule3":
                    # Rain Gauge
                    if "Rain" in module["dashboard_data"]:
                        displaystr += " | Rain " + str(module["dashboard_data"]["Rain"])
                elif module_type == "NAModule4":
                    # Optional indoor module
                    if "module_name" in module:
                        module_name = module["module_name"]
                    else:
                        module_name = "Opt Indoor"
                    if "Temperature" in module["dashboard_data"]:
                        displaystr += " | " + module_name + " " + str(module["dashboard_data"]["Temperature"])
    logging.info(displaystr)

def main():
    """Main function"""
    global g_token
    global g_config
    global g_data
    #print("netatmo.py v0.17 2019-10-31")
    #print("netatmo.py v0.18 2021-01-10")
    print("netatmo.py v0.19 2024-07-21")

    # read config
    if os.path.isfile(config_filename):
        g_config = read_json(config_filename)
    else:
        g_config = {'client_id': 'xxxx', 'client_secret': 'xxxx', 'device_id': 'xxxx'}
        write_json(g_config, config_filename)
        logging.error("main() error:")
        logging.error("Config file not found: creating an empty one.")
        logging.error("Please edit %s and try again.", config_filename)
        return

    # read last token    
    if os.path.isfile(token_filename):
        g_token = read_json(token_filename)
    else:
        #authenticate()
        logging.error("main() error:")
        logging.error("Token file not found: creating an empty one.")
        get_new_token()
        return

    # read last data
    if os.path.isfile(data_filename):
        g_data = read_json(data_filename)

    # main loop
    while True:
        get_station_data()
        display_console()
        # external display
        if os.path.isfile('./custom_display.py'):
            os.system('python3 ./custom_display.py')
        elif os.path.isfile('./display.py'):
            os.system('python3 ./display.py')
        # sleep 10 minutes
        try:
            time.sleep(600)
        except KeyboardInterrupt:
            # Crtl+C
            logging.info("Keyboard exception received. Exiting.")
            return

if __name__ == '__main__':
    main()
