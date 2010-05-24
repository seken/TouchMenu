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
import imaplib
from xml.sax import saxutils
import threading
import gobject
from keyring import Keyring
import glib

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
			gtk.gdk.threads_enter()
			self.emit("doneFetching", emails)
			gtk.gdk.threads_leave()

	def onTrigger(self):
		self.waitCond.acquire()
		self.waitCond.notify()
		self.waitCond.release()
		return True


class Pane(gtk.ScrolledWindow):
	def __init__(self, button, config):
		gtk.ScrolledWindow.__init__(self)
		self.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
		self.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC

		#TODO set the email count to the button label
		self.button = button

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
				elif protocol == 'imap' and port == 143:
					connector = imaplib.IMAP4(domain, port)
				else:
					raise "Unrecognised Email protocol/port"
				connector.login(cred[0], cred[1])
				connector.select('INBOX', True)
				self.imapConnectors.append(connector)

		self.updater = EmailThread(self, int(config.get('misc', 'email-interval')))
		self.updater.connect("doneFetching", self.updatePane)
		self.updater.start()
		self.updater.onTrigger()

		self.connect("destroy", self.destroy)

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

class Button(gtk.Button):
	def __init__(self):
		gtk.Button.__init__(self, 'Emails')
		self.mod_name = 'emails'
