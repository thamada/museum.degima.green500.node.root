#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# system-config-users.py - this program calls mainWindow to start the GUI
# Copyright © 2001 - 2003, 2009 Red Hat, Inc.
# Copyright © 2001 - 2003 Brent Fox <bfox@redhat.com>
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
# Brent Fox
# Nils Philippsen <nils@redhat.com>

import sys
import signal
import libuser

signal.signal (signal.SIGINT, signal.SIG_DFL)

import gettext
_ = lambda x: gettext.ldgettext ("system-config-users", x)

# only run if an X server is available
try:
    import gtk
except:
    print (_("system-config-users requires a currently running X server."))
    sys.exit(0)
    
import mainWindow
mainWindow.mainWindow()




