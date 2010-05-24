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
import glib
import time
import pygame
import gobject
import datetime
import threading

class Pane(gtk.Table):
	def __init__(self, button, config):
		gtk.Table.__init__(self, 2, 2)
		self.set_row_spacings(12)
		self.set_col_spacings(12)

		addButton = gtk.Button('Add')
		addButton.set_size_request(-1, 75)
		self.attach(addButton, 0, 1, 0, 1, gtk.EXPAND|gtk.FILL, False)
		addButton.connect("clicked", self.onAdd)

		removeButton = gtk.Button('Remove')
		removeButton.set_size_request(-1, 75)
		self.attach(removeButton, 1, 2, 0, 1, gtk.EXPAND|gtk.FILL, False)
		removeButton.connect("clicked", self.onRemove)

		self.alarms = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_INT, gobject.TYPE_STRING)
		self.alarms.append((True, 800, 'mon,tue,wed,thu,fri'))
		self.alarms.append((True, 1000, 'sat,sun'))

		self.alDisp = gtk.TreeView(self.alarms)
		self.alDisp.set_headers_visible(True)

		activeCol = gtk.TreeViewColumn('Active')
		timeCol = gtk.TreeViewColumn('Time')
		dayCol = gtk.TreeViewColumn('Day')

		self.alDisp.append_column(activeCol)
		self.alDisp.append_column(timeCol)
		self.alDisp.append_column(dayCol)

		activeCell = gtk.CellRendererToggle()
		timeCell = gtk.CellRendererText()
		dayCell = gtk.CellRendererText()

		activeCol.pack_start(activeCell)
		timeCol.pack_start(timeCell)
		dayCol.pack_start(dayCell)

		activeCol.set_attributes(activeCell, active=0)
		timeCol.set_attributes(timeCell, text=1)
		dayCol.set_attributes(dayCell, text=2)

		self.attach(self.alDisp, 0, 2, 1, 2)

		self.alarmThread = AlarmThread(self, config, config.get('alarm', 'sound'))
		self.alarmThread.start()
		self.alarmThread.connect("alarm", self.onAlarm)

		self.show_all()
	
	def onAdd(self, widget, data=None):
		pass
	
	def onRemove(self, widget, data=None):
		selected = self.alDisp.get_selection().get_selected_rows()
		for one in selected[1]:
			self.alarms.remove(self.alarms.get_iter(one))
	
	def onAlarm(self, widget, data=None):
		window = AlarmWindow(self.alarmThread)
		window.show_all()

class AlarmWindow(gtk.Window):
	def __init__(self, thread):
		gtk.Window.__init__(self, gtk.WINDOW_POPUP)
		self.set_border_width(12)
		self.set_decorated(False)
		self.set_position(gtk.WIN_POS_CENTER_ALWAYS)

		self.alarmThread = thread
		
		# VBox setup
		layout = gtk.VBox()
		layout.set_spacing(12)
		self.add(layout)

		self.time = gtk.Label()
		self.time.set_use_markup(True)
		layout.pack_start(self.time)
		self.updateClock()

		snooze = gtk.Button('Snooze')
		snooze.connect('clicked', self.onSnooze)
		layout.pack_start(snooze)

		off = gtk.Button('Off')
		off.connect('clicked', self.close)
		layout.pack_start(off)

		glib.timeout_add(2000, self.updateClock)

	def onSnooze(self, widget, data=None):
		self.alarmThread.stopSound()
		glib.timeout_add(600000, self.onSnoozeOver)
	
	def close(self, widget, data=None):
		self.alarmThread.stopSound()
		self.destroy()

	def onSnoozeOver(self):
		self.alarmThread.playSound()
		return False

	def updateClock(self):
		self.time.set_label('<span size="72000">'+datetime.datetime.now().strftime("%H:%M")+'</span>')
		return True


def dayToNum(day):
	if day == 'mon':
		return 0
	if day == 'tue':
		return 1
	if day == 'wed':
		return 2
	if day == 'thu':
		return 3
	if day == 'fri':
		return 4
	if day == 'sat':
		return 5
	if day == 'sun':
		return 6

class AlarmThread(threading.Thread, gobject.GObject):
	def __init__(self, pane, config, sound):
		threading.Thread.__init__(self)
		gobject.GObject.__init__(self)
		gobject.signal_new("alarm", self, gobject.SIGNAL_ACTION, gobject.TYPE_NONE, ())

		self.daemon = True
		self.config = config
		self.pane = pane
		self.sound = sound
	
	def run(self):

		if self.sound == 'mute':
			self.sound = None
		else:
			pygame.mixer.init()
			self.sound = pygame.mixer.Sound(self.sound)

		while True:
			temporal = datetime.datetime.now()
			self.day = temporal.weekday()
			self.time = temporal.time()
			self.pane.alarms.foreach(self.doCheckAlarm)
			time.sleep(60)

	def doCheckAlarm(self, model, path, iter, data=None):
		alarm = self.pane.alarms.get(iter, 0, 1, 2)
		if not alarm[0]:
			return
		for i in alarm[2].split(','):
			i = i.strip()
			if dayToNum(i) == self.day:
				if self.time.hour == alarm[1]/100 and self.time.minute == alarm[1]%100:
					self.config.screen.disable()
					self.playSound()
					gtk.gdk.threads_enter()
					self.emit("alarm")
					gtk.gdk.threads_leave()
				
	def stopSound(self):
		self.sound.stop()
	
	def playSound(self):
		print 'playing'
		if self.sound != None:
			self.sound.play(loops=-1, maxtime=360000)


class Button(gtk.Button):
	def __init__(self):
		gtk.Button.__init__(self, 'Alarm')
		self.mod_name = 'alarm'
