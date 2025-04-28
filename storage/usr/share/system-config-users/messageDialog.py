# -*- coding: utf-8 -*-
#
# messageDialog.py - a message dialog for redhat-config-users
# Copyright © 2001 - 2007, 2010 Red Hat, Inc.
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
# Brent Fox <bfox@redhat.com>
# Nils Philippsen <nils@redhat.com>

import gtk
import mainWindow

def show_message_dialog(text):
    dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, text)
    dlg.set_position(gtk.WIN_POS_CENTER)
    dlg.set_modal(True)
    dlg.set_icon_name(mainWindow.iconName)
    dlg.run()
    dlg.destroy()

def show_confirm_dialog(text):
    dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, text)
    dlg.set_position(gtk.WIN_POS_CENTER)
    dlg.set_modal(True)
    dlg.set_icon_name(mainWindow.iconName)
    rc = dlg.run()
    dlg.destroy()
    return rc
