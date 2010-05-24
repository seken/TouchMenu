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
import gtk
import sys
import dbus
import math

class Pane(gtk.Table):
	def __init__(self, button, config, otherList):
		rows = 1 + int(math.ceil(float(len(otherList))/2))
		gtk.Table.__init__(self, 2, rows)
		self.set_row_spacings(12)
		self.set_col_spacings(12)

		self.killApp = gtk.Button("Kill Dash")
		self.killApp.set_size_request(-1, 75)
		self.killApp.connect("clicked", self.onPress)
		self.attach(self.killApp, 0, 1, rows-1, rows)

		self.offButton = gtk.Button("Power Off")
		self.offButton.set_size_request(-1, 75)
		self.offButton.connect("clicked", self.onPress)
		self.attach(self.offButton, 1, 2, rows-1, rows)

		for i, button in enumerate(otherList):
			x = i%2
			y = i/2
			self.attach(button, x, x+1, y, y+1)

		#self.show_all()

	def onPress(self, widget, data=None):
		action = widget.get_label()

		if action == "Kill Dash":
			# gtkmozembed hangs if we do this by the book
			sys.exit(0)
		elif action == "Power Off":
			bus = dbus.SystemBus()
			proxy = bus.get_object('org.freedesktop.ConsoleKit', '/org/freedesktop/ConsoleKit/Manager')
			iface = dbus.Interface(proxy, 'org.freedesktop.ConsoleKit.Manager')
			iface.Stop()

class Button(gtk.Button):
	def __init__(self):
		gtk.Button.__init__(self, 'Others')
		self.mod_name = 'others'
