#!/usr/bin/env python
# -*- coding: latin-1 -*-

import pygtk
pygtk.require('2.0')
import os
import sys
import gtk
import glib
from keyring import Keyring
from ConfigParser import RawConfigParser

class ConfigureWindow(gtk.Window):
	def __init__(self):
		gtk.Window.__init__(self)
		glib.set_application_name("TouchMenu")
		glib.set_prgname("TouchMenu")
		self.set_title("Configuration")
		self.set_border_width(12)

		self.connect("delete_event", self.delete_event)
		self.connect("destroy", self.destroy)

		table = gtk.Table(2, 8)
		table.set_col_spacings(12)
		table.set_row_spacings(12)
		self.add(table)

		label = gtk.Label("Configuration Options")
		table.attach(label, 0, 2, 0, 1)

		labelEmail = gtk.Label("Email Settings (imap only):")
		labelEmail.set_alignment(1.0, 0.5)
		table.attach(labelEmail, 0, 2, 1, 2)

		labeleDomain = gtk.Label("Domain:")
		labeleDomain.set_alignment(1.0, 0.5)
		table.attach(labeleDomain, 0, 1, 2, 3)

		self.domain = gtk.Entry()
		table.attach(self.domain, 1, 2, 2, 3)

		labelePort = gtk.Label("Port:")
		labelePort.set_alignment(1.0, 0.5)
		table.attach(labelePort, 0, 1, 3, 4)

		self.port = gtk.Entry()
		self.port.set_text("993")
		table.attach(self.port, 1, 2, 3, 4)

		labeleUser = gtk.Label("Username:")
		labeleUser.set_alignment(1.0, 0.5)
		table.attach(labeleUser, 0, 1, 4, 5)

		self.user = gtk.Entry()
		table.attach(self.user, 1, 2, 4, 5)

		labelePass = gtk.Label("Password:")
		labelePass.set_alignment(1.0, 0.5)
		table.attach(labelePass, 0, 1, 5, 6)

		self.password = gtk.Entry()
		self.password.set_visibility(False);
		table.attach(self.password, 1, 2, 5, 6)

		quit = gtk.Button("Quit")
		quit.connect("clicked", self.close)
		table.attach(quit, 1, 2, 7, 8)

		save = gtk.Button("Save")
		save.connect("clicked", self.save)
		table.attach(save, 0, 1, 7, 8)

		self.show_all()

	# Quit
	def delete_event(self, widget, event, data=None):
		return False

	# Quit
	def destroy(self, widget, data=None):
		gtk.main_quit()

	def save(self, widget):
		config = RawConfigParser()
		config.add_section("misc")
		config.set("misc", "accounts", "1")
		config.add_section("email0")
		domain = self.domain.get_text()
		config.set("email0", "domain", domain)
		config.set("email0", "port", self.port.get_text())
		config.set("email0", "protocol", 'imap')

		keyring = Keyring('TouchMenu settings for '+domain, domain, 'imap')
		keyring.set_credentials((self.user.get_text(), self.password.get_text()))

		try:
			os.remove(os.path.expanduser("~/.touchmenu/settings"))
		except:
			pass

		os.mkdir(os.path.expanduser('~/.touchmenu/'))
		os.mkdir(os.path.expanduser('~/.touchmenu/mozilla/'))
		config.write(open(os.path.expanduser("~/.touchmenu/settings"), 'wb'))
		gtk.main_quit()

	def close(self, widget):
		gtk.main_quit()

	def main(self):
		gtk.main()

if __name__ == "__main__":
	app = ConfigureWindow()
	app.main()
