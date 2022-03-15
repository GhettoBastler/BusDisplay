# BusDisplay

A thing that tells you when the next buses are.

[IMAGE]

When the button is pressed, it fetches data from [Metz bus network website](https://www.lemet.fr/) and displays the next two arrivals for a particular line at a given stop.
Four seven-segment displays and two LEDs, mounted on a custom PCB, are controlled by the GPIO of a Raspberry Pi Zero 2 W.
The code is written in Python 3 and uses the requests and lxml library to scrape the data.

## Usage
Press the button to fetch data. An animation is displayed while the device is waiting for the website to respond.
The number of minutes for the next two buses are displayed on the front. A LED below each number indicates if it is "on-demand" service.
To turn the device off, press the button for three seconds. Once the LED of the Raspberry Pi turns off, you can safely unplug the device.

## Software setup
### Setting up the Raspberry Pi
Use Raspberry Pi Imager to create a Raspberry Pi OS Lite (64-bit) on a MicroSD card. Before writing the image, go to the Advanced Settings and change the following settings :
- Change the hostname to **busdisplay**.
- Check **Enable SSH**. You can leave the option to use password authentication checked.
- Leave the default username as **pi** and choose a password.
- Check **Configure wifi** and type in your SSID and wifi password. Change the country to France
- Check **Set locale settings** and change the time zone to Europe/Paris

Write the image on the SD card, then insert the card into the Raspberry Pi and power it on.

### Installation (on the Raspberry Pi)
Connect to the Raspberry Pi using SSH
```
ssh pi@busdisplay
```
When asked, enter the the password you chose when making the image.

Next, update the system and install git and pip
```
sudo apt-get update
sudo apt-get install git pip
```

Clone this repository and install the required libraries
```
git clone https://github.com/GhettoBastler/BusDisplay.git
sudo pip install -r BusDisplay/requirements.txt
```

Copy the service file and enable it to run the program at startup

*Note: the service file contains the full path to main.py. If you are not using the default username (pi) and/or if you cloned the repository into another location, change the content of BusDisplay.service accordingly.*
```
sudo cp BusDisplay/BusDisplay.service /etc/systemd/system/
sudo systemctl enable BusDisplay
```

Restart the Raspberry Pi
```
sudo reboot
```

If everything went right, every LED of the display should flash once during start up. After that, pressing the button will fetch data for the *METTIS A* line at *République* station.

### Configuration
To use another bus line/stop, you need LE MET's internal number for your station and line.

Go to <https://services.lemet.fr/> and search for your bus line on the left pannel

![LE MET Screenshot 1](https://github.com/GhettoBastler/BusDisplay/raw/main/images/lemet_screen_1.png)

Next, click on your stop in the timetable. You will be redirected to another page.

![LE MET Screenshot 2](https://github.com/GhettoBastler/BusDisplay/raw/main/images/lemet_screen_2.png)

The required values appear in the URL :

![LE MET Screenshot 3](https://github.com/GhettoBastler/BusDisplay/raw/main/images/lemet_screen_3.png)

Edit ```config.py``` and change the values for the ones that appears in the URL
```
nano BusDisplay/config.py
```

Restart the service
```
sudo systemctl restart BusDisplay
```

## Hardware
### Electronics
This project uses four SUNLED XDMR20A-1 seven-segment displays I scavenged from an old appliance. **These may be hard to source, so I would advise redesigning the PCB and front panel for the parts you can find using the included schematics and SVG files.**

Other components used for the circuits include:
- 9 100 ohm resistors
- 2 yellow LEDs
- A momentary push button that can fit a 12mm diameter hole (I used the R18-25B)
- A 2x20 connector with a ribbon cable for connecting the board to the Raspberry Pi

### Enclosure
The enclosure is designed to be laser cut. The material should be 5mm thick. All the parts are held in place by M2.5 bolts.

## License
This project is licensed under the terms of the GNU GPLv3 license.
