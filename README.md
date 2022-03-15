# BusDisplay

A thing that tells you when the next buses are. It fetches data from [Metz bus network website](https://www.lemet.fr/) and displays the next two arrivals for a particular line at a given stop.
Written in Python3, running on the Raspberry Pi Zero 2 W.

[IMAGE]

## Usage
Press the button to fetch data
Long press turns off the Raspberry Pi so it can be safely unplugged

## Software setup
### Setting up the Raspberry Pi
Install Raspberry Pi OS Lite (64 bits) on a MicroSD card using Raspberry Pi Imager
    Click the Advanced Settings to enable SSH, set up Wi-Fi and change the hostname
Insert the card into the Raspberry Pi and plug it in.

### Installation (on the Raspberry Pi)
Connect to the Raspberry Pi using SSH
```
ssh pi@busdisplay
```

Update the system and install git and pip
```
sudo apt-get update
sudo apt-get install git pip
```

Clone this repository and install the required libraries
```
git clone https://github.com/GhettoBastler/BusDisplay.git
sudo pip install -r BusDisplay/requirements.txt
```

Create a service and enable it to run the program at startup
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
To configure change the bus line and stop, you need LE MET's internal number for your station and line.
Go to [](https://services.lemet.fr/) and search for the bus line on the left pannel

[](images/lemet_screen_1.png)
Choose a stop in the list
[](images/lemet_screen_2.png)
Edit ```config.py``` and change the values for the ones that appears in the URL
```
nano BusDisplay/config.py
```

[](images/lemet_screen_3.png)

Restart the service
```
sudo systemctl restart BusDisplay
```

## Notes
- The enclosure was designed for 5mm plywood. The front panel is provided in a separate file for customization.
- The 7-segments displays (SUNLED XDMR20A-1) used for this project were scavenged from an old appliance I had laying around. Those may be hard to source, so I would advise redesigning the PCB and front panel for the parts you can find using the included schematics and SVG files. Other components used for this project include:
    - 9 10O ohm resistors
    - 2 yellow LEDs
    - A momentary push button (I used the R18-25B)
    - A 2x20 connector for connecting the board to the Raspberry Pi

## License
This project is licensed under the terms of the GNU GPLv3 license.
