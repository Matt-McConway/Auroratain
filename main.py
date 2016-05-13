import rumps  # Rumps allows the program to run in the background task bar: https://github.com/jaredks/rumps
from geopy.geocoders import Nominatim  # For converting city name to lat and longitude
import json  # For config files. http://stackoverflow.com/questions/19078170/python-how-would-you-save-a-simple-settings-config-file
import time  # For time related things
import py2app  # When I decide to make this a standalone mac app
from lxml import html  # Web Scraping
import requests  # Web Scraping


__title__ = 'Auroratain'
__version__ = '0.1'
__author__ = 'Matt McConway'
__license__ = 'IDK'
__copyright__ = 'Copyright 2016 Mercurious'
"""
    This application scrapes data from K_INDEX SITE, regarding the current k index, and predicted k indicies for
    relevant times. It also calculates the sundown time, so it will only notify you if you can see the aurora.
    I.e. after sundown, before sunrise.


    NZST (NZ Standard time) is +1200 UTC (UTC is also GMT?)


    KP Index
    KP 6+ is potentially visible to mum. 7+ is guaranteed.
"""

rumps.rumps.debug_mode(True)  # turn on command line logging information for development - default is off


# menu plan
# KP Value
# Notifications On/Off
# Settings ==========================|-About
#                                   |-Location
# sep (None)
# quit - enabled by default.

# In Rumps, None works as a separator in your menu
# rumps.MenuItem.update(). TO UPDATE/REFRESH MENU ITEMS
# Can use a dict for a drop down menu. e.g. {"Menu item" : ["submenu1", "submenu2", "submenu3"]}

#Constants
APP_SUPPORT_PATH = rumps.application_support("Auroratain")

def fetch_kp():
    # TODO - Tidy this up, it's ugly af. Maybe look into Scrapy - another library I could use instead of Requests
    page = requests.get("http://www.aurora-service.net/aurora-forecast/")
    try:
        page.raise_for_status()  # Checks quality of download
    except Exception as exc:
        print('There was a problem: %s' % exc)  # Change this to an alert via the app.

    kp_text_index = page.text.find("Right now, the aurora is predicted to be: ")
    kp_text = page.text[kp_text_index:(kp_text_index + 90)]
    kp_index = kp_text.find("Kp")

    # Because it is always to 2dp
    kp = kp_text[kp_index:kp_index + 8]

    # TODO - log data?
    # if Auroratain.notification_state:
    #    pass
    # with app.open('times', 'a') as f:  # this opens files in your app's Application Support folder
    #   f.write('The unix time now: {}\n'.format(time.time()))

    return str(kp)

def get_config():
    config_path = APP_SUPPORT_PATH + "/config.json"  # can just put this into the with statement.
    with open(config_path, "r") as f:
        config = json.load(f)
    return config

def set_config(name, value):
    config_path = APP_SUPPORT_PATH + "/config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)

    config[name] = value

    with open(config_path, 'w') as f:
        json.dump(config, f)

def update_coordinates():
    #TODO - Use geopy to get co ords from location from config. Then update config's latitude and longitude
    pass

class Auroratain(rumps.rumps.App):
    geoLocator = Nominatim()  # Add geolocation later I guess. For now, manual is fine.

    def __init__(self):
        super(Auroratain, self).__init__("Auroratain")
        self.menu = [fetch_kp(), "Notifications", "Say hi", {"Settings": ["Location", "About"]}, None]
        self.icon = 'assets/graphics/icon.png'

    # Alert message example.
    # @rumps.clicked(fetch_kp())
    # def prefs(self, _):
    #    rumps.alert(fetch_kp())

    # Two state checkbox type menu item.
    @rumps.rumps.clicked("Notifications")
    def notification_state(self, sender):
        # TODO - link this to alert messages
        sender.state = not sender.state
        if sender.state:
            notifications = True
        else:
            notifications = False
        return notifications

    # Notification example
    @rumps.rumps.clicked("Say hi")
    def say_hi(self, _):
        rumps.rumps.notification("Awesome title", "amazing subtitle", "hi!!1")

    @rumps.rumps.clicked("Settings", "Location")
    def get_location(self, sender):
        # TODO - link config to current location (default_text) -- DONE??
        config = get_config()
        location = config["location"]
        sender.title = 'Location' if sender.title == 'Location' else 'Location'  # Can probably remove this tbh
        window = rumps.rumps.Window(message="Enter your location:", title="Change Location",
                                    default_text=location,
                                    ok="Ok", cancel="Cancel", dimensions=(320, 160))
        response = window.run()  # THIS WORKS: https://github.com/camilopayan/pompy/blob/master/pom.py
        if response.clicked == 1:
            set_config("location", response.text)

    @rumps.rumps.clicked("Settings", "About")
    def about(self):
        # TODO - Update alert text, maybe change ok button text too.
        rumps.rumps.alert("About Auroratain",
                          "About text goes here :)",
                          ok="Thanks!")

    @rumps.rumps.timer(1800)  # create a new thread that calls the decorated function every 1800 seconds (30 minutes)
    def update_kp(self):
        rumps.rumps.MenuItem.update(self.menu, self.menu)


if __name__ == "__main__":
    Auroratain().run()
