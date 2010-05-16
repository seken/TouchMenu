#!/usr/bin/env python
# -*- coding: latin-1 -*-

import pygtk
pygtk.require('2.0')
import os
import sys
import gtk
import glib
import email
import pywapi
import gobject
import imaplib
import datetime
import threading
import gtkmozembed
from keyring import Keyring
from xml.sax import saxutils
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
		subjectLabel.set_label('<span size="xx-large">'+saxutils.escape(subject)+'</span>')
		subjectLabel.set_alignment(0.0, 0.5)
		vbox.pack_start(subjectLabel, False)

		senderLabel = gtk.Label()
		senderLabel.set_use_markup(True)
		senderLabel.set_label('<span size="small">From: '+saxutils.escape(sender)+'\n'+saxutils.escape(date)+'</span>')
		senderLabel.set_alignment(0.0, 0.5)
		vbox.pack_start(senderLabel, False)

		bodyLabel = gtk.Label(saxutils.escape(body[:100]))
		bodyLabel.set_alignment(0.0, 0.5)
		vbox.pack_start(bodyLabel, False)
		
		#self.show_all()

class EmailThread(threading.Thread, gobject.GObject):
	def __init__(self, pane, interval):
		threading.Thread.__init__(self)
		gobject.GObject.__init__(self)
		self.waitCond = threading.Condition()
		self.daemon = True
		self.pane = pane
		self.stop = False
		glib.timeout_add(interval*60000, self.onTrigger)
		gobject.signal_new("doneFetching", self, gobject.SIGNAL_ACTION, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
	
	def run(self):
		while True:
			self.waitCond.acquire()
			self.waitCond.wait()
			self.waitCond.release()
			if self.stop:
				return
			emails = list()
			for i in self.pane.imapConnectors:
				typ, messageIds = i.search(None, 'ALL')
				messageIds = messageIds[0].split()
				messageIds.reverse()
				if typ != 'OK':
					continue
				for m in messageIds[:20]:
					typ, data = i.fetch(m, '(FLAGS BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])')
					if typ != 'OK': continue
					email = dict()
					email['Flags'] = imaplib.ParseFlags(data[0][0])
					for line in data[0][1].splitlines():
						if line == '': continue
						bits = line.split(': ', 1)
						try:
							email[bits[0]] = bits[1]
						except:
							pass
					typ, data = i.fetch(m, '(BODY.PEEK[TEXT])')
					if typ != 'OK': continue
					try:
						email['Body'] = data[0][1].split('\r\n\r\n', 1)[1]
					except IndexError:
						email['Body'] = data[0][1]
					emails.append(email)
			# TODO sort the emails from all accounts!

			print 'Fetched '+str(len(emails))+' emails.'
			self.emit("doneFetching", emails)

	def onTrigger(self):
		self.waitCond.acquire()
		self.waitCond.notify()
		self.waitCond.release()
		return True


class EmailPane(gtk.ScrolledWindow):
	def __init__(self, config):
		gtk.ScrolledWindow.__init__(self)
		self.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
		self.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC

		self.emailList = gtk.VBox()
		self.emailList.set_spacing(12)
		self.emailList.pack_start(gtk.Label('Loading emails...'))
		self.add_with_viewport(self.emailList)
		
		self.imapConnectors = list()

		for i in range(int(config.get("misc", "accounts"))):
			domain = config.get("email"+str(i), "domain")
			port = int(config.get('email'+str(i), 'port'))
			protocol = config.get('email'+str(i), 'protocol')
			keyring = Keyring('TouchMenu settings for '+domain, domain, protocol)
			if keyring.has_credentials():
				connector = None
				cred = keyring.get_credentials()
				if protocol == 'imap' and port == 993:
					connector = imaplib.IMAP4_SSL(domain, port)
				else:
					raise "Unrecognised"
				connector.login(cred[0], cred[1])
				connector.select('INBOX', True)
				self.imapConnectors.append(connector)

		self.updater = EmailThread(self, int(config.get('misc', 'email-interval')))
		self.updater.connect("doneFetching", self.updatePane)
		self.updater.start()
		self.updater.onTrigger()

		self.connect("delete_event", self.delete_event)
		self.connect("destroy", self.destroy)

		self.show_all()

	def delete_event(self, widget, event, data=None):
		self.updater.stop = True
		self.updater.onTrigger()
	
	def destroy(self, widget, data=None):
		self.updater.stop = True
		self.updater.onTrigger()

	def updatePane(self, widget, emails):
		for child in self.emailList.get_children():
			self.emailList.remove(child)
		for email in emails:
			flag = 'unread'
			if '\\Seen' in email['Flags']:
				flag = 'read'
			if '\\Answered' in email['Flags']:
				flag = 'replied'
			self.emailList.pack_start(Email(flag, email['Subject'], email['From'], email['Date'], email['Body'][:200]))
			self.emailList.pack_start(gtk.HSeparator())
		self.emailList.show_all()
		self.emailList.check_resize()

class WebPane(gtkmozembed.MozEmbed):
	def __init__(self):
		gtkmozembed.MozEmbed.__init__(self)

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
		elif c == 'showers' or c == 'scattered showers' or c == 'rain' or c == 'chance of rain' or c == 'light rain' or c == 'sleet':
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
			print "I don't know what weather icon to use!"
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
		gtk.gdk.threads_init()

		if hasattr(gtkmozembed, 'set_profile_path'):
			set_profile_path = gtkmozembed.set_profile_path
		else:
			set_profile_path = gtkmozembed.gtk_moz_embed_set_profile_path
		set_profile_path(os.path.expanduser('~/.touchmenu/'), 'mozilla')

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
		self.weather = WeatherWidget(self.config)
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
		self.calendarView.load_url("https://www.google.com/calendar/hosted/seken.co.uk")
		self.mainWindow.append_page(self.calendarView)
		self.emailView = EmailPane(self.config)
		self.mainWindow.append_page(self.emailView)
		self.torrentView = WebPane()
		self.torrentView.load_url("http://seken.co.uk/")
		self.mainWindow.append_page(self.torrentView)

		table.attach(self.clock, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
		table.attach(bbox, 0, 1, 1, 2, xoptions=gtk.SHRINK, yoptions=gtk.SHRINK)
		table.attach(self.mainWindow, 1, 2, 1, 2)

		# Attach events
		glib.timeout_add(2000, self.on2Seconds)
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
