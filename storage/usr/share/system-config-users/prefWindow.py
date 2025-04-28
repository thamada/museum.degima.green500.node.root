# -*- coding: utf-8 -*-
#
# prefWindow.py - preferences window
# Copyright © 2006 - 2007, 2010 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# Authors:
# Nils Philippsen <nils@redhat.com>

import mainWindow

class PrefWindow:
    def __init__ (self, xml):
        self.xml = xml
        
        self.toplevel = xml.get_widget ("preferencesWindow")
        self.close = xml.get_widget ("preferencesWindowCloseButton")

        self.toplevel.set_icon_name (mainWindow.iconName)
        self.toplevel.connect ('delete-event', self.hide)

        self.close.connect ('activate', self.hide)
        self.close.connect ('clicked', self.hide)

    def show (self):
        self.toplevel.show ()
        self.toplevel.deiconify ()
        self.toplevel.window.raise_ ()

    def hide (self, *args):
        self.toplevel.hide ()
        return True
