#!/usr/bin/env python

# example helloworld.py

import pygtk
pygtk.require('2.0')
import gtk
import glib
import webkit
import datetime

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


class EmailPane(gtk.ScrolledWindow):
	def __init__(self):
		gtk.ScrolledWindow.__init__(self)
		self.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
		self.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC

		self.emailList = gtk.VBox()
		self.emailList.set_spacing(12)

		self.emailList.pack_start(gtk.Button("This"))
		self.emailList.pack_start(gtk.Button("is"))
		self.emailList.pack_start(gtk.Button("new"))
		self.emailList.pack_start(gtk.Button("new"))
		self.emailList.pack_start(gtk.Button("new"))
		self.emailList.pack_start(gtk.Button("new"))
		self.emailList.pack_start(gtk.Button("new"))
		self.emailList.pack_start(gtk.Button("new"))
		self.emailList.pack_start(gtk.Button("new"))
		self.emailList.pack_start(gtk.Button("new"))
		self.emailList.pack_start(gtk.Button("new"))
		self.emailList.pack_start(gtk.Button("new"))
		self.emailList.pack_start(gtk.Button("new"))
		self.emailList.pack_start(gtk.Button("new"))
		self.emailList.pack_start(gtk.Button("new"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))
		self.emailList.pack_start(gtk.Button("new2"))

		self.add_with_viewport(self.emailList)

		self.show_all()

class WebPane(webkit.WebView):
	def __init__(self):
		webkit.WebView.__init__(self)
		#settings = self.get_settings()
		#settings.set_property("enable-developer-extras", True)

		self.set_full_content_zoom(True)

		self.parentScroller = gtk.ScrolledWindow()
		self.parentScroller.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
		self.parentScroller.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
		self.parentScroller.add(self)
		self.parentScroller.show_all()
	
	def getScroller(self):
		return self.parentScroller

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
		self.time = ClockDate()

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
		self.emailView = EmailPane()
		self.mainWindow.append_page(self.emailView)
		self.torrentView = WebPane()
		self.torrentView.open("http://seken.co.uk/")
		self.mainWindow.append_page(self.torrentView.getScroller())

		table.attach(self.clock, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
		table.attach(bbox, 0, 1, 0, 2, xoptions=gtk.SHRINK, yoptions=gtk.SHRINK)
		table.attach(self.mainWindow, 1, 2, 1, 2)

		# Attach events
		glib.timeout_add(1000, self.onSecond)

		# This will cause the window to be destroyed by calling
		# gtk_widget_destroy(window) when "clicked".  Again, the destroy
		# signal could come from here, or the window manager.
		self.quitButton.connect_object("clicked", gtk.Widget.destroy, self.window)
		self.remoteButton.connect("clicked", self.onSwitch)
		self.calendarButton.connect("clicked", self.onSwitch)
		self.emailButton.connect("clicked", self.onSwitch)
		self.torrentButton.connect("clicked", self.onSwitch)

		bbox.show()
		self.clock.show()
		self.remoteButton.show()
		self.emailButton.show()
		self.calendarButton.show()
		self.torrentButton.show()
		self.quitButton.show()
		table.show()
		self.window.show()

	def main(self):
		gtk.main()

if __name__ == "__main__":
	app = TouchMenu()
	app.main()
