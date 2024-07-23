# netatmo

NetAtmo weather station display, based on a Raspberry Pi and an e-Paper screen.

<details><summary>Table of contents</summary>

* [Introduction](#introduction)
* [Installation](#installation)
  * [Raspbian/Raspberry Pi OS](#raspbian)
  * [PaPiRus setup](#papirus)
  * [Waveshare Setup](#waveshare)
  * [Download the app!](#download)
  * [NetAtmo API](#netatmoapi)
* [Files](#files)
* [Running the program](#running)
* [Launching on system startup](#startup)
* [References](#references)

</details>

<a name="introduction"></a>

# Introduction

The [NetAtmo Smart Weather Station][1] is a nice weather station with an indoor and an outdoor module, and optional rain gauge, anemometer and additional indoor modules. All the data from the different modules is available on the [web portal][2] and on the mobile app.

[1]: https://www.netatmo.com/en-eu/smart-weather-station

[2]: https://home.netatmo.com/control/dashboard

The modules themselves don't have any kind of display, so this project is an attempt to make a compact dedicated display for the NetAtmo weather station with at least indoor and outdoor temperatures, using a Raspberry Pi and a e-Paper screen.

The first setup I tried is this one:

- [Raspberry Pi Zero W][3]. The Zero W can be found with a soldered header if soldering is not your thing: it is called a [Raspberry Pi Zero WH][4]. See [here][5] or [here][6].

- [PaPiRus ePaper / eInk Screen HAT for Raspberry Pi][7]. I used the 2.7 inch screen, which has a resolution of 264 x 176.

[3]: https://www.raspberrypi.com/products/raspberry-pi-zero-w/

[4]: https://www.raspberrypi.org/blog/zero-wh/

[5]: https://uk.pi-supply.com/products/raspberry-pi-zero-w-soldered-header

[6]: https://shop.pimoroni.com/products/raspberry-pi-zero-w

[7]: https://uk.pi-supply.com/products/papirus-epaper-eink-screen-hat-for-raspberry-pi

![PaPiRus photo](images/papirus_2in7.jpg "Raspberry Pi Zero W and PaPiRus 2.7inch ePaper HAT")

Then I tried a second setup:

- [Raspberry Pi 3 B+][8] or [Raspberry Pi 4][9].

- [Waveshare 2.7inch e-Paper HAT][10], which has the same size and resolution of 264 x 176 as the PaPiRus.

[8]: https://www.raspberrypi.com/products/raspberry-pi-3-model-b-plus/

[9]: https://www.raspberrypi.com/products/raspberry-pi-4-model-b/

[10]: http://www.waveshare.com/2.7inch-e-paper-hat.htm

![Waveshare photo](images/waveshare_2in7.jpg "Raspberry Pi 3 B+ and Waveshare 2.7 inch ePaper Hat")

The first setup works fine but the PaPiRus screen is not attached to the HAT board, making the thing very fragile without a suitable case. The Waveshare is well attached and the whole setup is much more robust. But on the software side, the PaPiRus has a much better story than the Waveshare. Anyway, both work as expected.

I chose Python 3 for the code as it is available and up to date on every Raspbery Pi OS.

<a name="installation"></a>

# Installation

<a name="raspbian"></a>

## Raspbian/Raspberry Pi OS for the Raspberry Pi

You need to prepare a microSD card with Raspberry Pi OS Lite. It is important to get the 'Lite' version because you don't want the graphical interface on a fully headless device. The simplest way to do that is to use the Raspberry Pi Imager tool:

Insert a new microSD card in your PC or Mac (8 GB or more).

Download, install and run the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) for your OS.

- Under Raspberry Pi Device, choose your target device.
- Under Operating System, click **Choose OS**, select **Raspberry Pi OS (other)**, and then **Raspberry Pi OS Lite (32 bit)**.
- Under Storage, choose your microSD card.
- Click **NEXT**.

Next, you will have the option to use OS custom settings: click **EDIT SETTINGS**.

- At least set the username and password. To make things simple, you can name the user `pi` and choose a password that will be easy to remember.
- If you plan to use wifi, configure your wifi network.
- In the SERVICE tab, check the **Enable SSH** box.
- Chose if you want to authenticate with the password or a SSH key. If you already have a SSH key, paste your public key.
- Click **SAVE**.

Click **YES** to use the OS customization settings.

If you are sure you selected the right target microSD, click **YES** in the Warning window.

The tool then does the downloading, the writing and the checking, so it may take some time.

When the tool displays "Write Successfull", remove the microSD from the PC, click **CONTINUE** and close the Window.

Insert the microSD in the Raspberry Pi and plug the power supply. The first boot should take a few minutes. It should connect to your Wifi network and you should be able to **get its IP address from your router**.

Connect to the device from your PC or Mac:

```
ssh <username>@<IP_address>
```

If this doesn't work, boot the Raspberry with its microSD, a keyboard and an HDMI screen, login with your username and password, and use the `raspi-config` utility to configure the network.

Once connected with SSH, install the latest OS updates, and reboot:

```
sudo apt update && sudo apt full-upgrade -y && sudo reboot
```

Reconnect after the reboot. Python 3 should already be installed. You can check its version with:

```
python3 -V
```

Install [git][14], the [Freefont TrueType fonts][15], [PIL][16], and the [Requests][17] module (needed to call the NetAtmo API):

```
sudo apt install git fonts-freefont-ttf python3-pil python3-requests
```

[14]: https://git-scm.com/

[15]: http://savannah.gnu.org/projects/freefont/

[16]: https://python-pillow.org/

[17]: https://github.com/psf/requests

<a name="papirus"></a>

## PaPiRus setup

Follow these instructions *only if you have a PaPiRus HAT and e-Paper screen*.

First, the hardware setup. Follow this documentation:

https://www.pi-supply.com/make/papirus-assembly-tips-and-gotchas/

Next, the Python module:

IMPORTANT: On the Raspberry Pi, you need to __enable both SPI and I2C interfaces__ :

```
sudo raspi-config
```

Select `Interface options` > `SPI` > `Yes`. Without exiting the tool, still in `Interface options`, select `I2C` > `Yes`.

Reboot:

```
sudo reboot
```

Then, follow the instructions here: https://github.com/PiSupply/PaPiRus. Or, here is the short version of these instructions:

```
sudo apt update
sudo apt install bc i2c-tools fonts-freefont-ttf whiptail make gcc -y
sudo apt install python3-pil python3-smbus python3-dateutil -y
git clone --depth=1 https://github.com/PiSupply/PaPiRus.git
cd PaPiRus
sudo python3 setup.py install
sudo papirus-setup
sudo papirus-set 2.7
```

The last command sets the size of the screen you have.

You can then test the Python API with tools present in /usr/local/bin. For instance:

```
papirus-write "Hello world!"
papirus-clear
```

<a name="waveshare"></a>

## Waveshare Setup

If you have a Waveshare 2.7inch e-Paper screen, the instructions are here:

https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT

and the software is here :

https://github.com/waveshare/e-Paper

The hardware setup is very simple. Just plug the board on the 40-pin GPIO header. The software setup is documented on the wiki above, and here is the short and simplified version:

Activate the SPI interface:

```
sudo raspi-config
```

Choose `Interface Options` > `SPI` > `Yes` to enable SPI interface.

Reboot:

```
sudo reboot
```

Reconnect and install Python 3 libraries:

```
sudo apt update
sudo apt install python3-numpy python3-rpi.gpio python3-spidev
```

Download the Waveshare repo in your home dir:

```
cd
git clone https://github.com/waveshare/e-Paper
```

(Optional) test the display:

```
cd e-Paper/RaspberryPi_JetsonNano/python/examples
python3 epd_2in7_test.py
```

This should display some test patterns on the Waveshare screen.

Come back to the home dir:

```
cd
```

<a name="download"></a>

## Download the app!

Download the code in your home dir:

```
cd
git clone https://github.com/psauliere/netatmo.git
cd netatmo
```

To test the display module, type this:

```
cp sample_data.json data.json
./display.py
```

This should display a sample based on the sample data included in the repo.

<a name="netatmoapi"></a>

## NetAtmo API

First you need to get the MAC address of your indoor module. Unfortunately it seems that it is not available any more on the new [dashboard](https://home.netatmo.com/control/dashboard),  So you need to use the mobile app.

On the Android NetAtmo app, you need to tap the menu icon on the top left, then _Manage my home_, and then your indoor module. Look for its _Serial number_ and take note of the value, which begins with `70:ee:50:`.

Then on your computer, go to https://dev.netatmo.com/apps/, authenticate with your NetAtmo username and password, and create a new app. Take note of the _client id_ and the _client secret_ for your app.

You now need to authorize the app to access your NetAtmo data:

- Under _Token generator_, select the **read_station** scope and click **Generate Token**.
- It might take a while, and you will get a page where you have to _authorize_ your app to access to your data.
- Click **Yes I accept**. You now have a new _Access Token_ and a new _Refresh Token_, that you can copy to your clipboard by clicking on them.

Once you have all these values,
- copy the `sample_config.json` file to a new `config.json` file
- copy the `sample_token.json` file to a new `token.json` file

```
cd
cd netatmo
cp sample_config.json config.json
cp sample_token.json token.json
```

Edit the `config.json` file with your values:

```json
{
    "client_id": "your app client id",
    "client_secret": "your app client secret",
    "device_id": "your indoor module serial number"
}
```

Edit the `token.json` file with your tokens:
```json
{
    "access_token": "you Access Token",
    "refresh_token": "your Refresh Token"
}
```

<a name="files"></a>

# Files

You need these 4 files to begin:

- `config.json`
- `token.json`
- `netatmo.py`
- `display.py` or `custom_display.py`

If `config.json` does not exist, `netatmo.py` creates an empty one and you have to edit it. `config.json` is the configuration file. You must edit this file with your values (see above).

If `token.json` does not exist, `netatmo.py` creates an empty one and you have to edit it. `token.json` contains the _access token_ for the program to access to your NetAtmo, and the _refresh token_ for the program to renew the _access token_ when it expires (every 3 hours). This file is written by `netatmo.py` every time it refreshes the _access token_. The refresh operation is managed by the program, but the initial tokens have to be generated and validated interactively online (see above).

`netatmo.py`: main module. Every 10 minutes, it calls the [NetAtmo `getstationdata` API](https://dev.netatmo.com/apidocumentation/weather#getstationsdata) to get the weather station data, stores it to the `data.json` file, and calls `display.py`. It refreshes the access token when it expires.

`display.py`: display module, called by `netatmo.py` every 10 minutes. It reads `data.json` and displays the data on the screen. So if you choose another screen, or wish to change the display, you just have to adapt or rewrite this file. If no supported screen is present, `display.py` draws the image of the display into a `image.bmp` file. See below (`image.bmp`) for an example of display.

If you want to customize the display, just copy `display.py` to `custom_display.py` and edit the copy. If `netatmo.py` finds a file named `custom_display.py`, it calls this one instead of `display.py`.

Files created by the program:

`token.json`: _access token_ and _refresh token_. This file is written by `netatmo.py` every time it refreshes the tokens.

`data.json`: weather station data file. This file holds the JSON result of the latest NetAtmo `getstationdata` API call.

`image.bmp`: image of the latest screen display, written by `display.py`. Example:

![Sample image](images/sample_image.bmp "Sample image")

In this example, the display shows:

- the time of the `getstationdata` API call.
- the indoor temperature and trend
- the outdoor temperature and trend
- the rain in mm/h

<a name="running"></a>

# Running the program

Run `./netatmo.py`, for instance in a `tmux` session to let it run even when you disconnect your SSH session.

On the console, you will see that:

 - Every 10 minutes, netatmo.py gets weather data and prints 1 line on the console with the date, time, temperatures and, if you have the modules, rain and wind data.
 - Every three hours, the access token expires and the program refreshes it.

To stop the program, type Ctrl+C.

![netatmo.py screenshot](images/console_screenshot.png "netatmo.py running in a tmux session")

<a name="startup"></a>

# Launching on system startup

To act like an appliance, the program must survive power failures, that is it must automatically launch on system boot. As I find it convenient to use tmux to be able to watch the program's console output anytime I ssh to the system, the `launcher.sh` script creates a tmux session named NETATMO and launches `netatmo.py` inside the new tmux session.

First you need to install `tmux` if not already done:
```
sudo apt install tmux
```

To run the `launcher.sh` script at system startup, edit the `/etc/rc.local` file as root and add this line, *before* the `exit 0` line:

```
su -c /home/pi/netatmo/launcher.sh -l pi
```

This will run the script as the `pi` user.

Later, when you ssh to the system as the `pi` user, you can attach to the NETATMO tmux session this way:

```
tmux a
```

and detach from the session with this key sequence: `Ctrl+B`, `d`.

<a name="references"></a>

# References

- [NetAtmo developer documentation](https://dev.netatmo.com/)
- [PaPiRus documentation](https://github.com/PiSupply/PaPiRus)
- [Waveshare 2.7inch e-Paper documentation](https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT)
- [Another NetAtmo Display project: netatmo-display](https://github.com/bkoopman/netatmo-display)

More on tmux:

- [A Quick and Easy Guide to tmux](https://www.hamvocke.com/blog/a-quick-and-easy-guide-to-tmux/)
- [The Tao of tmux](https://leanpub.com/the-tao-of-tmux/read)
