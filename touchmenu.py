#!/usr/bin/env python
# -*- coding: latin-1 -*-

import pygtk
pygtk.require('2.0')
import os
import gtk
import glib
import webkit
import datetime
from keyring import Keyring
from ConfigParser import RawConfigParser

class ClockDate:
	def __init__(self, form="%a %d %b, %H:%M"):
		self.form = form
	
	def getString(self):
		return datetime.datetime.now().strftime(self.form)
	
	def getTime(self):
		return datetime.datetime.now().strftime("%H:%M")

class RemotePane(gtk.Table):
	def __init__(self):
		gtk.Table.__init__(self, 2, 2)
		self.set_row_spacings(12)
		self.set_col_spacings(12)

		self.show_all()

class Email(gtk.HBox):
	def __init__(self, status, subject, sender, date, body):
		gtk.HBox.__init__(self)
		self.set_spacing(12)

		icon = gtk.Image()
		if status == "read":
			icon.set_from_file("/usr/share/icons/gnome/24x24/status/stock_mail-open.png")
		elif status == "unread":
			icon.set_from_file("/usr/share/icons/gnome/24x24/status/stock_mail-unread.png")
		elif status == "replied":
			icon.set_from_file("/usr/share/icons/gnome/24x24/status/stock_mail-replied.png")
		else:
			icon.set_from_file("/usr/share/icons/gnome/24x24/status/stock_mail-unread.png")
		self.pack_start(icon, False)

		vbox = gtk.VBox()
		vbox.set_spacing(6)
		self.pack_start(vbox, False)

		subjectLabel = gtk.Label()
		subjectLabel.set_use_markup(True)
		subjectLabel.set_label('<span size="xx-large">'+subject+'</span>')
		subjectLabel.set_alignment(0.0, 0.5)
		vbox.pack_start(subjectLabel, False)

		senderLabel = gtk.Label()
		senderLabel.set_use_markup(True)
		senderLabel.set_label('<span size="small">From: '+sender+'\n'+date+'</span>')
		senderLabel.set_alignment(0.0, 0.5)
		vbox.pack_start(senderLabel, False)

		bodyLabel = gtk.Label(body[:200])
		bodyLabel.set_alignment(0.0, 0.5)
		vbox.pack_start(bodyLabel, False)
		
		self.show_all()

class EmailPane(gtk.ScrolledWindow):
	def __init__(self, domain):
		gtk.ScrolledWindow.__init__(self)
		self.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
		self.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC

		self.emailList = gtk.VBox()
		self.emailList.set_spacing(12)

		self.emailList.pack_start(Email("read", "FOOD", "stomach", "noew!", "eat"), False)
		self.emailList.pack_start(Email("unread", "FOOD", "stomach", "noew!", "eat lorem ipsum dfgon asd fg asdfg as fg asf g asdfg  afsdg adfg as fgasfg\nasd fa sdf\n asd f asd f asd f asdf  d  df sdf  ds dfssdf."), False)
		self.emailList.pack_start(Email("replied", "FOOD", "stomach", "noew!", "eat"), False)
		self.emailList.pack_start(Email("read", "FOOD", "stomach", "noew!", "eat"), False)
		self.emailList.pack_start(Email("read", "FOOD", "stomach", "noew!", "eat"), False)
		self.emailList.pack_start(Email("read", "FOOD", "stomach", "noew!", "eat"), False)
		self.emailList.pack_start(Email("read", "FOOD", "stomach", "noew!", "eat"), False)

		self.add_with_viewport(self.emailList)

		self.keyring = Keyring("Email Account for "+domain, domain, "imap")

		self.show_all()

class WebPane(webkit.WebView):
	def __init__(self):
		webkit.WebView.__init__(self)
		self.set_full_content_zoom(True)

		self.parentScroller = gtk.ScrolledWindow()
		self.parentScroller.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
		self.parentScroller.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
		self.parentScroller.add(self)
		self.parentScroller.show_all()
	
	def getScroller(self):
		return self.parentScroller

class WeatherWidget(gtk.HBox):
	def __init__(self, location):
		gtk.HBox.__init__(self)
		self.set_spacing(12)
		self.location = location

		# Setup the icon
		self.icon = gtk.Image()
		self.icon.set_alignment(1.0, 0.5)
		self.setIcon("sunny")

		# Setup the label
		self.temp = gtk.Label("14°C")
		self.temp.set_alignment(0.0, 0.5)

		self.pack_start(self.icon, False, False)
		self.pack_start(self.temp, False, True)

	def setIcon(self, type):
		self.icon.set_from_file("/usr/share/icons/gnome/24x24/status/stock_weather-"+type+".png")

class touchMenuConfig(RawConfigParser):
	def __init__(self):
		RawConfigParser.__init__(self)
		location = os.path.expanduser('~')+'.touchmenu'
		if os.path.exists(location):
			self.read(location)
		else:
			print "No config file found!"
			# Popup menu


class TouchMenu:
	def onSecond(self):
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
		pane = widget.get_label()
		
		if pane == "Remote":
			self.mainWindow.set_current_page(0)

		if pane == "Calendar":
			self.mainWindow.set_current_page(1)

		if pane == "Email":
			self.mainWindow.set_current_page(2)

		if pane == "Torrents":
			self.mainWindow.set_current_page(3)


	def __init__(self):
		glib.set_application_name("TouchMenu")
		glib.set_prgname("TouchMenu")

		self.time = ClockDate()

		self.config = touchMenuConfig()

		# create a new window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)
    
		# Sets the border width of the window.
		self.window.set_border_width(12)

		# Set to full screen
		self.window.fullscreen()

		# Create the main layout
		table = gtk.Table(2, 2)
		table.set_row_spacings(12)
		table.set_col_spacings(12)
		self.window.add(table)

		# Setup the button box
		bbox = gtk.VButtonBox()
		bbox.set_spacing(12)
    
		self.remoteButton = gtk.Button("Remote")
		self.remoteButton.set_size_request(-1, 75)
		self.emailButton = gtk.Button("Email")
		self.emailButton.set_size_request(-1, 75)
		self.calendarButton = gtk.Button("Calendar")
		self.calendarButton.set_size_request(-1, 75)
		self.torrentButton = gtk.Button("Torrents")
		self.torrentButton.set_size_request(-1, 75)
		self.quitButton = gtk.Button("Quit")
		self.quitButton.set_size_request(-1, 75)
    
		# Setup the clock
		self.clock = gtk.Label(self.time.getString())
		self.clock.set_justify(gtk.JUSTIFY_RIGHT)
		self.clock.set_alignment(1.0, 0.5)

		# Setup the weather
		self.weather = WeatherWidget("York, UK")
		table.attach(self.weather, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
    
		# Pack button box
		bbox.pack_start(self.remoteButton)
		bbox.pack_start(self.emailButton)
		bbox.pack_start(self.calendarButton)
		bbox.pack_start(self.torrentButton)
		bbox.pack_start(self.quitButton)
    
		# Main Window
		self.mainWindow = gtk.Notebook()
		self.mainWindow.set_show_tabs(False)
		self.mainWindow.set_show_border(False)
		self.mainWindow.show()

		self.remoteView = RemotePane()
		self.mainWindow.append_page(self.remoteView)
		self.calendarView = WebPane()
		self.calendarView.open("http://google.co.uk/")
		self.mainWindow.append_page(self.calendarView.getScroller())
		self.emailView = EmailPane("test")
		self.mainWindow.append_page(self.emailView)
		self.torrentView = WebPane()
		self.torrentView.open("http://seken.co.uk/")
		self.mainWindow.append_page(self.torrentView.getScroller())

		table.attach(self.clock, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
		table.attach(bbox, 0, 1, 1, 2, xoptions=gtk.SHRINK, yoptions=gtk.SHRINK)
		table.attach(self.mainWindow, 1, 2, 1, 2)

		# Attach events
		glib.timeout_add(1000, self.onSecond)
		self.quitButton.connect_object("clicked", gtk.Widget.destroy, self.window)
		self.remoteButton.connect("clicked", self.onSwitch)
		self.calendarButton.connect("clicked", self.onSwitch)
		self.emailButton.connect("clicked", self.onSwitch)
		self.torrentButton.connect("clicked", self.onSwitch)

		self.window.show_all()

	def main(self):
		gtk.main()

if __name__ == "__main__":
	app = TouchMenu()
	app.main()
