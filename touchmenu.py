#!/usr/bin/env python
# -*- coding: latin-1 -*-

'''
    This file is part of TouchMenu.

    TouchMenu is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    TouchMenu is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TouchMenu.  If not, see <http://www.gnu.org/licenses/>.
'''

import pygtk
pygtk.require('2.0')
import os
import sys
import gtk
import glib
import time
import pywapi
import datetime
import threading
import subprocess
import gtkmozembed
import modules.others
from modules import WebPane
from ConfigParser import RawConfigParser

class ClockDate:
	def __init__(self, form="%a %d %b, %H:%M"):
		self.form = form
	
	def getString(self):
		return datetime.datetime.now().strftime(self.form)
	
	def getTime(self):
		return datetime.datetime.now().strftime("%H:%M")

class Screen(threading.Thread):
	def __init__(self, config):
		threading.Thread.__init__(self)
		self.daemon = True
		self.enabled = True
		self.days = [
			[(True, datetime.time(int(x)/100, int(x)%100)) for x in config.get('onoff', 'monon').split(',')],
			[(True, datetime.time(int(x)/100, int(x)%100)) for x in config.get('onoff', 'tueon').split(',')],
			[(True, datetime.time(int(x)/100, int(x)%100)) for x in config.get('onoff', 'wedon').split(',')],
			[(True, datetime.time(int(x)/100, int(x)%100)) for x in config.get('onoff', 'thuon').split(',')],
			[(True, datetime.time(int(x)/100, int(x)%100)) for x in config.get('onoff', 'frion').split(',')],
			[(True, datetime.time(int(x)/100, int(x)%100)) for x in config.get('onoff', 'saton').split(',')],
			[(True, datetime.time(int(x)/100, int(x)%100)) for x in config.get('onoff', 'sunon').split(',')]
		]
		self.days[0].extend([(False, datetime.time(int(x)/100, int(x)%100)) for x in config.get('onoff', 'monoff').split(',')])
		self.days[1].extend([(False, datetime.time(int(x)/100, int(x)%100)) for x in config.get('onoff', 'tueoff').split(',')])
		self.days[2].extend([(False, datetime.time(int(x)/100, int(x)%100)) for x in config.get('onoff', 'wedoff').split(',')])
		self.days[3].extend([(False, datetime.time(int(x)/100, int(x)%100)) for x in config.get('onoff', 'thuoff').split(',')])
		self.days[4].extend([(False, datetime.time(int(x)/100, int(x)%100)) for x in config.get('onoff', 'frioff').split(',')])
		self.days[5].extend([(False, datetime.time(int(x)/100, int(x)%100)) for x in config.get('onoff', 'satoff').split(',')])
		self.days[6].extend([(False, datetime.time(int(x)/100, int(x)%100)) for x in config.get('onoff', 'sunoff').split(',')])

		self.days = [sorted(day, key=lambda timeState:timeState[1]) for day in self.days]

	def isOff():
		# TODO xset q | grep "Monitor is On" | wc -l
		pass
	
	def off(self):
		subprocess.call(('xset', 'dpms', 'force', 'off'))

	def on(self):
		subprocess.call(('xset', 'dpms', 'force', 'on'))

	def disable(self):
		self.enabled = False
		self.on()

	def enable(self):
		self.enabled = True

	def run(self):
		while True:
			if self.enabled:
				temporal = datetime.datetime.now()
				day = temporal.weekday()
				temporal = temporal.time()
				turn = False
				for timeState in self.days[day]:
					if temporal > timeState[1]:
						turn = timeState[0]
					else:
						break
				if turn:
					self.on()
				else:
					self.off()
			time.sleep(60)

class WeatherWidget(gtk.HBox):
	def __init__(self, config):
		gtk.HBox.__init__(self)
		self.set_spacing(12)
		self.location = config.get('misc', 'location')

		# Setup the icon
		self.icon = gtk.Image()
		self.icon.set_alignment(1.0, 0.5)
		self.setIcon("sunny")

		# Setup the label
		self.temp = gtk.Label("Loading")
		self.temp.set_alignment(0.0, 0.5)

		self.pack_start(self.icon, False, False)
		self.pack_start(self.temp, False, True)

		self.update()
		glib.timeout_add(60000*int(config.get('misc', 'weather-interval')), self.update)

	def setIcon(self, type):
		self.icon.set_from_file("/usr/share/icons/gnome/24x24/status/stock_weather-"+type+".png")

	def update(self):
		weather = pywapi.get_weather_from_google(self.location)
		self.temp.set_label(weather['current_conditions']['temp_c']+'°C')
		c = weather['current_conditions']['condition'].lower()
		if c == 'partly sunny':
			self.setIcon('few-clouds')
		elif c == 'scattered thunderstorms' or c == 'thunderstorm' or c == 'storm' or c == 'chance of tstorm' or c == 'chance of storm':
			self.setIcon('storm')
		elif c == 'showers' or c == 'scattered showers' or c == 'rain' or c == 'chance of rain' or c == 'light rain' or c == 'sleet' or c =='drizzle':
			self.setIcon('showers')
		elif c == 'rain and snow' or c == 'snow' or c == 'chance of snow' or c == 'light snow' or c == 'freezing drizzle' or c == 'flurries' or c == 'icy':
			self.setIcon('snow')
		elif c == 'overcast' or c == 'mostly cloudy' or c == 'cloudy':
			self.setIcon('cloudy')
		elif c == 'sunny' or c == 'clear':
			self.setIcon('sunny')
		elif c == 'mostly sunny' or c == 'partly cloudy':
			self.setIcon('few-clouds')
		elif c == 'mist' or c == 'dust' or c == 'fog' or c == 'smoke' or c == 'haze':
			self.setIcon('fog')
		else:
			print "I don't know what weather icon to use: '" + c + "'"
			self.setIcon('severe-alert')

		return True

class touchMenuConfig(RawConfigParser):
	def __init__(self):
		RawConfigParser.__init__(self)
		location = os.path.expanduser('~/.touchmenu/settings')
		if os.path.exists(location):
			self.read(location)
		else:
			print "No config file found, run config program"
			sys.exit(-1)

class TouchMenu:
	def on2Seconds(self):
		if not self.clock:
			return false
		
		# Update the clock
		self.clock.set_text(self.time.getString())
		return True

	# Quit
	def delete_event(self, widget, event, data=None):
		return False

	# Quit
	def destroy(self, widget, data=None):
		gtk.main_quit()

	def onSwitch(self, widget, data=None):
		pane = widget.mod_name
		self.mainWindow.set_current_page(self.NotebookDict[pane])

	def __init__(self):
		glib.set_application_name("TouchMenu")
		glib.set_prgname("TouchMenu")
		gtk.gdk.threads_init()

		self.config = touchMenuConfig()
		self.config.screen = Screen(self.config)
		self.config.screen.start()

		self.time = ClockDate()

		# create a new window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)
		self.window.set_default_size(800, 480)
    
		# Sets the border width of the window.
		self.window.set_border_width(12)

		# Set to full screen
		self.window.fullscreen()

		# Setup the mozilla engine
		modules.WebPane.setup()

		# Create the main layout
		table = gtk.Table(2, 2)
		table.set_row_spacings(12)
		table.set_col_spacings(12)
		self.window.add(table)

		# Setup the button box
		bbox = gtk.VButtonBox()
		bbox.set_spacing(12)

		# Main Window
		self.mainWindow = gtk.Notebook()
		self.mainWindow.set_show_tabs(False)
		self.mainWindow.set_show_border(False)
		self.mainWindow.show()

		# Load the config
		mainModules = self.config.get('modules', 'main').split(',')
		otherModules = self.config.get('modules', 'others').split(',')

		self.NotebookDict = dict()
		otherList = list()

		# Load the main modules
		for mod in mainModules:
			module = 'modules.'+mod
			__import__(module)
			module = sys.modules[module]
			button = module.Button()
			button.connect('clicked', self.onSwitch)
			button.set_size_request(-1, 75)
			bbox.pack_start(button)
			pane = module.Pane(button, self.config)
			id = self.mainWindow.append_page(pane)
			self.NotebookDict[button.mod_name] = id

		# Load the other modules
		for mod in otherModules:
			module = 'modules.'+mod
			__import__(module)
			module = sys.modules[module]
			button = module.Button()
			button.connect('clicked', self.onSwitch)
			otherList.append(button)
			pane = module.Pane(button, self.config)
			id = self.mainWindow.append_page(pane)
			self.NotebookDict[button.mod_name] = id
			
		# Add the 'others' pane and button
		button = modules.others.Button()
		button.connect('clicked', self.onSwitch)
		button.set_size_request(-1, 75)
		bbox.pack_start(button)
		pane = modules.others.Pane(button, self.config, otherList)
		id = self.mainWindow.append_page(pane)
		self.NotebookDict[button.mod_name] = id
    
		# Setup the clock
		self.clock = gtk.Label(self.time.getString())
		self.clock.set_justify(gtk.JUSTIFY_RIGHT)
		self.clock.set_alignment(1.0, 0.5)

		# Setup the weather
		self.weather = WeatherWidget(self.config)
		table.attach(self.weather, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
    
		table.attach(self.clock, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
		table.attach(bbox, 0, 1, 1, 2, xoptions=gtk.SHRINK, yoptions=gtk.SHRINK)
		table.attach(self.mainWindow, 1, 2, 1, 2)

		# Attach events
		glib.timeout_add(2000, self.on2Seconds)

		self.window.show_all()

	def main(self):
		gtk.main()

if __name__ == "__main__":
	app = TouchMenu()
	app.main()
