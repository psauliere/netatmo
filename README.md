# netatmo
NetAtmo weather station display

> Warning: Code and documentation are a work in progress.

The [NetAtmo Smart Weather Station][1] is a nice weather station with an indoor and an outdoor module, and optional rain gauge, anemometer and additional indoor modules. All the data from the different modules is available on the [web portal][2] and on the mobile app.

[1]: https://www.netatmo.com/en-eu/weather/weatherstation

[2]: https://my.netatmo.com/app/station

The modules themselves don't have any kind of display, so this project is an attempt to make a compact dedicated display for the NetAtmo weather station with at least indoor and outdoor temperatures, using:

- a [Raspberry Pi Zero W][3] --a Raspberry Pi 3 or 4 would also work, although less compact. The Zero W can be found with a soldered header if soldering is not your thing: it is called a [Raspberry Pi Zero WH][4]. See [here][5] or [here][6].

- a [PaPiRus ePaper / eInk Screen HAT for Raspberry Pi][7]. I use the 2.7 inch screen.

[3]: https://www.raspberrypi.org/products/raspberry-pi-zero-w/

[4]: https://www.raspberrypi.org/blog/zero-wh/

[5]: https://uk.pi-supply.com/products/raspberry-pi-zero-w-soldered-header

[6]: https://shop.pimoroni.com/products/raspberry-pi-zero-wh-with-pre-soldered-header

[7]: https://uk.pi-supply.com/products/papirus-epaper-eink-screen-hat-for-raspberry-pi

To be clear: I chose the PaPiRus ePaper HAT for Raspberry Pi because the [pHAT and screen for the Raspberry Pi Zero][8] are two small for my taste. Anyway, you will see that the display code is isolated so that you can easyly replace it with your own if you choose another screen.

[8]: https://uk.pi-supply.com/products/papirus-zero-epaper-screen-phat-pi-zero

As this is a new project (as of sept. 2019), I chose Python 3 for the code: Python 3.5.3 on Raspbian Stretch, but also works on 3.6 and 3.7.

Preparation
===========

> Warning: documentation is not complete.

Raspbian for the Raspberry Pi
-----------------------------

Download the [Raspbian 9 (stretch) lite (without GUI) image][11]. You may be lucky with the [latest version][12] but I advise to stick to the lite version.

Copy the image on the microSD card, for instance with [etcher][13].

[11]:http://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2018-04-19/2018-04-18-raspbian-stretch-lite.zip

[12]: https://www.raspberrypi.org/downloads/raspbian/

[13]: https://www.balena.io/etcher/

Before removing the microSD card from your computer, in the `boot` volume of the card, create an empty file named `ssh`. This is the simplest way to enable the OpenSSH server on Raspbian.

Also copy a `wpa_supplicant.conf` file to the same `boot` volume, with this content:

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=FR

network={
	ssid="Your Wifi network name"
	psk="Your Wifi network password"
}
```

Remove the microSD from the PC, insert it in the Raspberry Pi Zero W and plug the power supply. The first boot should take a few minutes. It should connect to your Wifi network and you should be able to get its IP address from your router.

Connect to the device from you PC or MAC:

```
ssh pi@<IP_address>
```

The user is `pi` and the password is `raspberry`.

If this doesn't work, boot the Raspberry with its microSD, a keyboard and an HDMI screen, login with the `pi` user and use the `raspi-config` utility to configure the network.

One connected with SSH, install the latest OS updates:

```
sudo apt update
sudo apt dist-upgrade
sudo reboot
```

Python 3
--------

Python 3 should already be installed:

```
$ python3 -V
```

Install pip for python3:
```
sudo apt install python3-pip
sudo python3 -m pip install -upgrade pip
```

Requests Python module
----------------------

Install the [Requests][31] module (needed to call the NetAtmo API):

```
sudo pip3 install requests
```

[31]: https://github.com/psf/requests

PaPiRus hardware setup
----------------------

Documentation:

https://www.pi-supply.com/make/papirus-assembly-tips-and-gotchas/

PaPiRus Python module
---------------------

IMPORTANT: On the Raspberry Pi [Zero W], you need to __enable the SPI and the I2C interfaces__. You can enable them by typing `sudo raspi-config` at the command line and then selecting `Interfacing options` > `SPI` and then selecting `Enable`. Without exiting the tool still in `Interfacing options` > `I2C` and then selecting `Enable`. (from the [PaPiRus documentation](https://github.com/PiSupply/PaPiRus))

Then, follow the instructions here: https://github.com/PiSupply/PaPiRus

or, here is the short version of these instructions:

```
sudo apt-get install git bc i2c-tools fonts-freefont-ttf whiptail make gcc -y

sudo apt-get install python3-pil python3-smbus python3-dateutil -y

git clone --depth=1 https://github.com/PiSupply/PaPiRus.git

cd PaPiRus

sudo python3 setup.py install

sudo papirus-setup

sudo papirus-set 2.7
```

The last command sets the size of the screen you have.

You can then test the Python API with tools present in /usr/local/bin. For instance:

```
papirus-clear
papirus-write "Hello world!"
papirus-test
papirus-clock
papirus-temp
papirus-clear
```

NetAtmo API
-----------

First you need to get the MAC address of your indoor module. Open https://my.netatmo.com/app/station, authenticate with your NetAtmo username and password, then click on _Manage my Station_. In the popup, look for _Indoor module_ and then _MAC address_. Take note of the value, which begins with `70:ee:50:`.

Then go to https://dev.netatmo.com/myaccount/, authenticate with your NetAtmo username and password, and create a new app. Take note of the _client id_ and the _client secret_ for your app.

Once you have all these values, copy the `sample_config.json` file to a new `config.json` file. Edit the file with your values:

- `username`: your NetAtmo username
- `password`: your NetAtmo password
- `client_id`: your NetAtmo app client id
- `client_secret`: your NetAtmo app client secret
- `device_id`: your indoor module MAC address

Files
=====

You need these 3 files to begin:

- `config.json`
- `netatmo.py`
- `display.py`

If `config.json` does not exist, `netatmo.py` creates an empty one and you have to edit it.

`config.json` is the configuration file. You must edit this file with your values (see above: NetAtmo API).

`netatmo.py`: main module. Every 10 minutes, it calls the [NetAtmo getstationdata API][getstationdata] to get the weather station data, stores it to the `data.json` file, and calls `display.py`. Manages the authentication and refreshes the oAuth2 token according to the NetAtmo documentation.

[getstationdata]: https://dev.netatmo.com/resources/technical/reference/weather/getstationsdata

`display.py`: display module, called by `netatmo.py`every 10 minutes. It reads `data.json` and displays the data on the screen. So if you choose another screen, you just have to rewrite this file. If no PaPiRus screen is present, `display.py` does nothing, so you can run `netatmo.py` on any system with python3, with or without an ePaper screen. See below (`image.bmp`) for an example of display.

Files created by the program:

`token.json`: authentication token and refresh token. This file is written by `netatmo.py` every time it authenticates or refreshes the authentication token.

`data.json`: weather station data file. This file holds the JSON result of the latest NetAtmo `getstationdata` API call.

`image.bmp`: image of the latest PaPiRus screen display, written by `display.py` Example:

![Sample image](sample_image.bmp "Sample image")

In this example, the display shows:

- the date date & time of the `getstationdata` API call.
- the indoor temperature and trend
- the outdoor temperature and trend
- the rain in mm/h

Running the program
===================

> Warning: documentation is not complete.

Run `./netatmo.py`, for instance in a `tmux` session to let it run even when you disconnect your SSH session.

On the console, you will see that:

 - Every 10 minutes, netatmo.py gets weather data and prints 1 line on the console with the date, time and temperatures.
 - Every three hours, the access token expires and the program refreshes it.

More on tmux:

- https://www.hamvocke.com/blog/a-quick-and-easy-guide-to-tmux/
- https://leanpub.com/the-tao-of-tmux/read

To stop the program, type Ctrl+C.

References
==========

NetAtmo developer documentation: https://dev.netatmo.com/resources/technical/introduction

PaPiRus documentation: https://github.com/PiSupply/PaPiRus

Another NetAtmo Display project: https://github.com/bkoopman/netatmo-display
