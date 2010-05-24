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

import os
import gtkmozembed

class WebPane(gtkmozembed.MozEmbed):
	def __init__(self):
		gtkmozembed.MozEmbed.__init__(self)
		self.load_url('http://google.co.uk')

def setup():
	if hasattr(gtkmozembed, 'set_profile_path'):
		set_profile_path = gtkmozembed.set_profile_path
	else:
		set_profile_path = gtkmozembed.gtk_moz_embed_set_profile_path
	set_profile_path(os.path.expanduser('~/.touchmenu/'), 'mozilla')
