# -*- coding: utf-8 -*-
#
# groupWindow.py - event handling code for userconf's group window
# Copyright © 2001 - 2007, 2009, 2010 Red Hat, Inc.
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
import string
import libuser
import mainWindow
import messageDialog
import userGroupCheck
import userGroupFind

import gettext
_ = lambda x: gettext.ldgettext ("system-config-users", x)

busy_cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
ready_cursor = gtk.gdk.Cursor(gtk.gdk.LEFT_PTR)

class groupWindow:

    def __init__(self, parent, user_clist, group_clist, xml):
        self.parent = parent
        self.group_clist = group_clist
        
        self.groupWin = xml.get_widget('newGroupWindow')
        self.groupWin.connect("delete-event", self.on_groupWin_cancel_button_clicked)
        self.groupWin.set_icon_name(mainWindow.iconName)
        self.groupWin.set_position(gtk.WIN_POS_CENTER)

        uidNumber, gidNumber = userGroupFind.find_uid_gid (self.parent.ADMIN, self.parent.preferences)

        self.groupWinGroupName = xml.get_widget('newGroupNameEntry')
        self.groupWinGroupName.set_max_length (userGroupCheck.maxgroupnamelength)
        self.newGidCheckButton = xml.get_widget('newGroupGidCheckButton')
        self.newGidSpinButton = xml.get_widget('newGroupGidSpinButton')
        self.newGidSpinButton.set_range(0, pow(2, 32))
        self.newGidSpinButton.set_value(gidNumber)
        self.on_newGidCheckButton_toggled ()

        xml.signal_connect("on_groupWin_cancel_button_clicked", self.on_groupWin_cancel_button_clicked)
        xml.signal_connect("on_groupWin_ok_button_clicked", self.on_groupWin_ok_button_clicked)
        xml.signal_connect("on_newGroupGidCheckButton_toggled", self.on_newGidCheckButton_toggled)

    def busy(self):
        self.groupWin.set_sensitive(False)
        self.groupWin.window.set_cursor(busy_cursor)

    def ready(self):
        self.groupWin.window.set_cursor(ready_cursor)
        self.groupWin.set_sensitive(True)

    def groupWinReset(self):
        self.groupWinGroupName.grab_focus()
        self.groupWinGroupName.set_text("")
        self.newGidCheckButton.set_active(False)
        uidNumber, gidNumber = userGroupFind.find_uid_gid (self.parent.ADMIN, self.parent.preferences)
        self.newGidSpinButton.set_value(gidNumber)

    def newGroupWin(self):
        self.groupWinReset()
        self.groupWin.show_all()

    #--------Event handlers for group window-----#
    def on_groupWin_cancel_button_clicked(self, *args):
        self.groupWinReset()
        self.groupWin.hide()
        return True

    def on_newGidCheckButton_toggled (self, *args):
        self.newGidSpinButton.set_sensitive (self.newGidCheckButton.get_active ())

    def on_groupWin_ok_button_clicked(self, *args):
        self.busy()
        groupName = self.groupWinGroupName.get_text()

        #Check for ascii-only strings
        if not userGroupCheck.isGroupnameOk(groupName, self.groupWinGroupName):
            self.ready()
            self.groupWinGroupName.grab_focus()
            return

        if groupName == "":
            messageDialog.show_message_dialog(_("Please enter a group name."))
            self.ready()
            self.groupWinGroupName.set_text("")
            self.groupWinGroupName.grab_focus()
            return

        group = self.parent.ADMIN.lookupGroupByName(groupName)
        if group != None:
            messageDialog.show_message_dialog(_("A group with name '%s' already exists." %groupName))
            self.ready()
            self.groupWinGroupName.set_text("")
            self.groupWinGroupName.grab_focus()
            return

        groupEnt = self.parent.ADMIN.initGroup(groupName)
        cn = groupEnt.get(libuser.GROUPNAME)[0]

        if self.newGidCheckButton.get_active() == True:
            gidNumber = int(self.newGidSpinButton.get_value())

            gid = self.parent.ADMIN.lookupGroupById(gidNumber)
            if gid != None:
                #This uid already exists, so complain
                messageDialog.show_message_dialog(_("The gid %s is already in use.") %gidNumber)
                self.ready()
                self.newGidSpinButton.grab_focus()
                return

            if gidNumber < 500:
                dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_YES_NO,
                                        (_("Creating a group with a GID less than 500 is not recommended.  "
                                           "Are you sure you want to do this?")))
                dlg.set_position(gtk.WIN_POS_CENTER)
                dlg.set_icon_name(mainWindow.iconName)
                dlg.set_modal(True)
                dlg.show_all()
                result = dlg.run()
                self.ready()
                self.groupWinGroupName.set_text("")
                self.groupWinGroupName.grab_focus()
                dlg.destroy()

                if result == gtk.RESPONSE_YES:
                    pass
                else:
                    return
        else:
            gidNumber = userGroupFind.find_gid (self.parent.ADMIN, self.parent.preferences)

        groupEnt.set(libuser.GIDNUMBER, [gidNumber])

        members = groupEnt.get(libuser.MEMBERNAME)
        if not members:
            members = []
        memberlist = string.join(members, ", ")

        self.parent.ADMIN.addGroup(groupEnt)
        
        self.groupWinReset()
        self.ready()
        self.groupWin.hide()

        self.parent.refresh_users_and_groups([cn])
