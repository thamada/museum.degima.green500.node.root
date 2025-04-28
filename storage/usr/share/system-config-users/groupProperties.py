# -*- coding: utf-8 -*-
#
# groupProperties - event handling code for userconf's group properties
# Copyright © 2001 - 2005, 2007, 2009, 2010 Red Hat, Inc.
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
import gobject
import mainWindow
import libuser
import messageDialog
import userGroupCheck

import gettext
_ = lambda x: gettext.ldgettext ("system-config-users", x)

busy_cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
ready_cursor = gtk.gdk.Cursor(gtk.gdk.LEFT_PTR)

class groupProperties:
    def __init__(self, parent, user_clist, group_clist, xml):
        self.parent = parent
        self.user_clist = user_clist
        self.group_clist = group_clist

        self.groupWin = xml.get_widget('groupProperties')
        self.groupWin.connect("delete-event", self.on_groupProperties_cancel_button_clicked)
        self.groupWin.set_position(gtk.WIN_POS_CENTER)
        self.groupWin.set_icon_name(mainWindow.iconName)
        self.groupWinGroupName = xml.get_widget('groupNameEntry')
        self.groupWinGroupName.set_max_length (userGroupCheck.maxgroupnamelength)
        self.groupNotebook = xml.get_widget('groupNotebook')
        self.userVBox = xml.get_widget('groupPropUserVBox')

        self.userStore = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING)

        self.userTreeView = gtk.TreeView(self.userStore)
        self.userTreeView.set_property("headers-visible", False)

        self.checkboxrenderer = gtk.CellRendererToggle()
        self.checkboxrenderer.connect("toggled", self.toggled_item)
        col = gtk.TreeViewColumn(None, self.checkboxrenderer, active=0)
        self.userTreeView.append_column(col)
        col = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=1)
        self.userTreeView.append_column(col)

        self.userChecklistSW = gtk.ScrolledWindow()
        self.userChecklistSW = gtk.ScrolledWindow()
        self.userChecklistSW.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.userChecklistSW.set_shadow_type(gtk.SHADOW_IN)
        self.userChecklistSW.add(self.userTreeView)           
        self.userVBox.pack_start(self.userChecklistSW, True)

        xml.signal_connect("on_groupProperties_cancel_button_clicked", self.on_groupProperties_cancel_button_clicked)
        xml.signal_connect("on_groupProperties_ok_button_clicked", self.on_groupProperties_ok_button_clicked)

    def busy(self):
        self.groupWin.set_sensitive(False)
        self.groupWin.window.set_cursor(busy_cursor)

    def ready(self):
        self.groupWin.window.set_cursor(ready_cursor)
        self.groupWin.set_sensitive(True)

    def groupWinReset(self):
        self.groupNotebook.set_current_page(0)
        self.userStore.clear()

    def showGroupProperties(self, groupEnt):
        self.groupEnt = groupEnt
        self.groupWinReset()

        cn = self.groupEnt.get(libuser.GROUPNAME)[0]
        self.groupWinGroupName.set_text(cn)

        self.fill_users_list(self.groupEnt)
        self.groupWin.show_all()

    def on_groupProperties_cancel_button_clicked(self, *args):
        self.groupWinReset()
        self.groupWin.hide()
        return True

    def on_groupProperties_ok_button_clicked(self, *args):
        self.busy()
        currentGroupName = self.groupEnt.get(libuser.GROUPNAME)[0]
        newGroupName = self.groupWinGroupName.get_text()

        # Avoid empty group names
        if newGroupName == "":
            messageDialog.show_message_dialog (_("Please enter a group name."))
            self.ready ()
            self.groupWinGroupName.set_text ("")
            self.groupWinGroupName.grab_focus ()
            return

        # Check for UTF-8-only strings
        if not userGroupCheck.isGroupnameOk(newGroupName, self.groupWinGroupName):
            self.ready()
            self.groupWinGroupName.grab_focus()
            return

        # Avoid duplicate group names
        if currentGroupName != newGroupName and userGroupCheck.groupExists (self.parent.ADMIN, newGroupName):
            messageDialog.show_message_dialog (_("The group '%s' already exists. Please choose a different name.") % newGroupName)
            self.ready ()
            self.groupWinGroupName.set_text ("")
            self.groupWinGroupName.grab_focus ()
            return

        if newGroupName != currentGroupName:
            self.groupEnt.set(libuser.GROUPNAME, newGroupName)
        
        user_list = []
        
        group_gidNumber = self.groupEnt.get(libuser.GIDNUMBER)[0]
        groupName = self.groupEnt.get(libuser.GROUPNAME)[0]
        members = self.parent.ADMIN.enumerateUsersByGroup(groupName)
        if not members:
            members = []

        #Let's iterate through the groupStore and see what groups are selected
        iter = self.userStore.get_iter_root()

        while iter:
            val = self.userStore.get_value(iter, 0)
            user = self.userStore.get_value(iter, 1)

            if val:
                if user in members:
                    user_list.insert(0, user)
                else:
                    try:
                        userEnt = self.parent.user_dict[user]
                    except:
                        userEnt = self.parent.ADMIN.lookupUserByName(user)
                    user_gidNumber = userEnt.get(libuser.GIDNUMBER)[0]
                    if user_gidNumber != group_gidNumber:
                        user_list.append(user)
            else:
                if user in members:
                    userEnt = self.parent.ADMIN.lookupUserByName(user)
                    if userEnt.get(libuser.GIDNUMBER)[0] == self.groupEnt.get(libuser.GIDNUMBER)[0]:
                        #You can't remove a user from their primary group, so reselect the user and popup an error
                        self.userStore.set_value(iter, 0, True)
                        dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                                (_("You cannot remove user '%s' from their primary "
                                                   "group." % user)))
                        dlg.set_position(gtk.WIN_POS_CENTER)
                        dlg.set_icon_name(mainWindow.iconName)
                        dlg.set_modal(True)
                        dlg.run()
                        dlg.destroy()
                        self.ready()
                        return
                        
                    members.remove(user)
                    
            iter = self.userStore.iter_next(iter)
                        
        self.groupEnt.set(libuser.MEMBERNAME, user_list)
        self.parent.ADMIN.modifyGroup(self.groupEnt)

        self.parent.refresh_users_and_groups(user_list + [currentGroupName] + [newGroupName])
        self.groupWinReset()
        self.groupWin.hide()
        self.ready()

    def toggled_item(self, data, row):
        iter = self.userStore.get_iter(int(row))
        val = self.userStore.get_value(iter, 0)
        self.userStore.set_value(iter, 0, not val)

    def fill_users_list (self, groupEnt):
        self.users = self.parent.ADMIN.enumerateUsers()
        self.users.sort()
        row = 0
        group = groupEnt.get(libuser.GROUPNAME)[0]
        members = self.parent.ADMIN.enumerateUsersByGroup(group)
        if not members:
            members = []

        for user in self.users:
            iter = self.userStore.append()
            
            if user in members:            
                self.userStore.set_value(iter, 0, True)
                self.userStore.set_value(iter, 1, user)
            else:
                self.userStore.set_value(iter, 0, False)
                self.userStore.set_value(iter, 1, user)                
