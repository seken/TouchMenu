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

class Pane(gtk.Table):
	def __init__(self, button, config):
		gtk.Table.__init__(self, 2, 2)
		self.set_row_spacings(12)
		self.set_col_spacings(12)

		self.show_all()

class Button(gtk.Button):
	def __init__(self):
		gtk.Button.__init__(self, 'Remote')
		self.mod_name = 'remote'
