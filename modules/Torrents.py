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
from WebPane import WebPane

class Pane(WebPane):
	def __init__(self, button, config):
		WebPane.__init__(self)
		self.load_url(config.get('misc', 'torrent-address'))

class Button(gtk.Button):
	def __init__(self):
		gtk.Button.__init__(self, 'Torrents')
		self.mod_name = 'torrents'
