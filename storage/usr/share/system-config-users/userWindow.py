# -*- coding: utf-8 -*-
#
# userWindow.py - event handling code for userconf's user window
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
# Brent Fox
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

class userWindow:

    def __init__(self, parent, userStore, group_clist, xml, selinuxEnabled):
        self.parent = parent
        self.userStore = userStore
        self.group_clist = group_clist
        
        self.userWin = xml.get_widget('newUserWindow')
        self.userWin.connect("delete-event", self.on_userWin_cancel_button_clicked)
        self.userWin.set_icon_name(mainWindow.iconName)
        self.userWinUserName = xml.get_widget('newUserNameEntry')
        self.userWinUserName.set_max_length (userGroupCheck.maxusernamelength)
        self.userWinFullName = xml.get_widget('newFullNameEntry')
        self.userWinPassword = xml.get_widget('newPasswordEntry')
        self.userWinConfirm = xml.get_widget('newConfirmEntry')
        self.userWinHomeDir = xml.get_widget('newHomeDirEntry')
        self.userWinHomeDir.set_max_length (userGroupCheck.maxpathlength)
        self.loginShellCombo = xml.get_widget('newLoginShellCombo')
        self.loginShellCombo.entry.set_property('editable', False)
        self.selinuxCombo = xml.get_widget("selinuxCombo")
        self.selinuxCombo.entry.set_property('editable', False)        
        self.selinuxLabel = xml.get_widget("selinuxLabel")
        self.newGroupCheck = xml.get_widget('newGroupCheck')
        self.passwordLabel = xml.get_widget('passwordLabel')
        self.homeDirHbox = xml.get_widget('homeDirHbox')
        self.homeDirCheck = xml.get_widget('homeDirCheck')

        uidNumber, gidNumber = userGroupFind.find_uid_gid (self.parent.ADMIN, self.parent.preferences)

        self.newUidCheckButton = xml.get_widget('newUidCheckButton')
        self.newUidSpinButton = xml.get_widget('newUidSpinButton')
        self.newUidSpinButton.set_range(0, pow(2, 32))
        self.newUidSpinButton.set_value(uidNumber)
        self.on_newUidCheckButton_toggled ()
        self.newGidCheckButton = xml.get_widget('newGidCheckButton')
        self.newGidSpinButton = xml.get_widget('newGidSpinButton')
        self.newGidSpinButton.set_range(0, pow(2, 32))
        self.newGidSpinButton.set_value(gidNumber)
        self.on_newGidCheckButton_toggled ()

        if not selinuxEnabled:
            self.selinuxCombo.set_sensitive(False)
            self.selinuxLabel.set_sensitive(False)

        self.selinuxRoleDict = { _("User"): "user_r", _("Staff") : "staff_r",
                                 _("System Administrator") : "sysadm_r"}
        roles = self.selinuxRoleDict.keys()
        roles.sort()
        self.selinuxCombo.set_popdown_strings(roles)
        self.selinuxCombo.list.select_item(2)

        self.shells = self.parent.ADMIN.getUserShells()
        self.shells.sort()
        self.loginShellCombo.set_popdown_strings(self.shells)
        default = '/bin/bash'
        if default in self.shells:
            self.loginShellCombo.list.select_item(self.shells.index(default))

        xml.signal_connect("on_userWin_cancel_button_clicked", self.on_userWin_cancel_button_clicked)
        xml.signal_connect("on_userWin_ok_button_clicked", self.on_userWin_ok_button_clicked)
        xml.signal_connect("on_newUserNameEntry_focus_out_event", self.on_newUserNameEntry_focus_out_event)
        xml.signal_connect("on_newUidCheckButton_toggled", self.on_newUidCheckButton_toggled)
        xml.signal_connect("on_newGidCheckButton_toggled", self.on_newGidCheckButton_toggled)

    #--function to reset the entry widgets in the user screen
    def userWinReset(self):
        self.userWinUserName.grab_focus()
        self.userWinUserName.set_text("")
        self.userWinFullName.set_text("")
        self.userWinPassword.set_text("")
        self.userWinConfirm.set_text("")
        self.userWinHomeDir.set_text("")
        self.newGroupCheck.set_active(True)
        self.newUidCheckButton.set_active(False)
        self.newGidCheckButton.set_active(False)
        self.homeDirCheck.set_active(True)
        try:
            #Hack to work around what I suspect is a gtk bug
            uidNumber, gidNumber = userGroupFind.find_uid_gid (self.parent.ADMIN, self.parent.preferences)
            self.newUidSpinButton.set_value(uidNumber)
        except:
            pass

        default = '/bin/bash'
        if default in self.shells:
            self.loginShellCombo.list.select_item(self.shells.index(default))

    def busy(self):
        self.userWin.set_sensitive(False)
        self.userWin.window.set_cursor(busy_cursor)

    def ready(self):
        self.userWin.window.set_cursor(ready_cursor)
        self.userWin.set_sensitive(True)

    def newUserWin(self, filter):
        self.filter = filter
        self.userWinReset()
        self.userWin.show_all()

        #Hide SELinux widgets for now
        self.selinuxCombo.hide()
        self.selinuxLabel.hide()

    def hideWin(self):
        self.userWin.hide()


    def getUserName(self):
        name = self.userWinUserName.get_text()                
        return name

    def getFullName(self):
        return self.userWinFullName.get_text()

    #--------Event handlers for user window-----#
    def on_newUserNameEntry_focus_out_event(self, *args):
        name = self.userWinUserName.get_text ()
        if not name:
            homedir = "/home/"
        else:
            ent = self.parent.ADMIN.initUser (name)
            homedir = ent.get (libuser.HOMEDIRECTORY)
            if homedir:
                homedir = homedir[0]
            else:
                homedir = "/home/%s" % name
        self.userWinHomeDir.set_text (homedir)

    def on_newUidCheckButton_toggled (self, *args):
        self.newUidSpinButton.set_sensitive (self.newUidCheckButton.get_active ())

    def on_newGidCheckButton_toggled (self, *args):
        self.newGidSpinButton.set_sensitive (self.newGidCheckButton.get_active ())

    def on_userWin_cancel_button_clicked (self, *args):
        self.userWinReset()
        self.userWin.hide()
        return True

    def on_userWin_ok_button_clicked(self, *args):
        self.busy ()
        userName = self.userWinUserName.get_text ()
        fullName = self.userWinFullName.get_text ()
        pw = self.userWinPassword.get_text ()
        confirm = self.userWinConfirm.get_text ()
        createHomeDir = self.homeDirCheck.get_active ()
        homeDir = self.userWinHomeDir.get_text ()

        if pw == confirm and len (pw) >= 6:
            #If the passwords match, go on
            pass
        else:
            #The passwords don't match, so complain
            if not pw and not confirm:
                messageDialog.show_message_dialog(_("Please enter a password for the user."))
                self.ready()
                self.userWinPassword.set_text("")
                self.userWinConfirm.set_text("")                
                self.userWinPassword.grab_focus()
                return

            elif len (pw) < 6:
                messageDialog.show_message_dialog(_("The password is too short.  Please "
                                                    "use at least 6 characters."))
                self.ready()
                self.userWinPassword.set_text("")
                self.userWinConfirm.set_text("")                
                self.userWinPassword.grab_focus()
                return

            else:
                messageDialog.show_message_dialog(_("The passwords do not match."))
                self.ready()
                self.userWinPassword.set_text("")
                self.userWinConfirm.set_text("")                
                self.userWinPassword.grab_focus()
                return

        #Check for ascii-only strings
        if not userGroupCheck.isUsernameOk(userName, self.userWinUserName):
            self.ready()
            self.userWinUserName.grab_focus()
            return

        if not userGroupCheck.isNameOk(fullName, self.userWinFullName):
            self.ready()
            self.userWinFullName.grab_focus()
            return

        if not userGroupCheck.isPasswordOk(pw, self.userWinPassword):
            self.ready()
            self.userWinPassword.grab_focus()
            return

        if createHomeDir and not userGroupCheck.isHomedirOk(homeDir, self.userWinHomeDir):
            self.ready()
            self.userWinHomeDir.grab_focus()
            self.on_newUserNameEntry_focus_out_event()
            return

        if userName == "":
            #The user name is blank, so complain
            messageDialog.show_message_dialog(_("Please specify a user name"))
            self.ready()
            self.userWinUserName.grab_focus()
            return

        user = self.parent.ADMIN.lookupUserByName(userName)
        if user != None:
            #This user already exists, so complain
            messageDialog.show_message_dialog(_("An account with username '%s' already exists.") %userName)
            self.ready()
            self.userWinUserName.set_text("")
            self.userWinUserName.grab_focus()
            return


        userEnt = self.parent.ADMIN.initUser(userName)
        userEnt.set(libuser.GECOS, [fullName])
        # Don't set if there are defaults
        if not len (userEnt.get (libuser.SHADOWMIN)):
            userEnt.set(libuser.SHADOWMIN, 0)
        if not len (userEnt.get (libuser.SHADOWMAX)):
            userEnt.set(libuser.SHADOWMAX, 99999)

        userEnt.set (libuser.HOMEDIRECTORY, [homeDir])
            
        userEnt.set (libuser.LOGINSHELL,
                     [self.loginShellCombo.entry.get_text ()])

        if self.newUidCheckButton.get_active ():
            uidNumber = int (self.newUidSpinButton.get_value ())
        else:
            uidNumber = None

        if self.newGidCheckButton.get_active ():
            gidNumber = int (self.newGidSpinButton.get_value ())
        else:
            gidNumber = None

        gidDuplicate = False

        try:
            uidNumber, gidNumber = userGroupFind.find_uid_gid (self.parent.ADMIN, self.parent.preferences, uidNumber = uidNumber, gidNumber = gidNumber)
        except userGroupFind.DuplicateUidNumberError, ue:
            # This uid already exists, so complain
            messageDialog.show_message_dialog (_("The uid %s is already in use.") % ue.uidNumber)
            self.ready ()
            self.newUidSpinButton.grab_focus ()
            return
        except userGroupFind.DuplicateGidNumberError, ge:
            if self.newGidCheckButton.get_active ():
                # This (chosen) gid already exists, so complain
                messageDialog.show_message_dialog (_("The gid %s is already in use.") % gidNumber)
                self.ready ()
                self.newGidSpinButton.grab_focus ()
                return
            gidDuplicate = True
            gidNumber = ge.gidNumber
            # A group with this gid already exists.  Handle this a little further down.

        if self.newUidCheckButton.get_active() and uidNumber < 500:
            # They want a UID < 500.  Warn the user, but allow it if they insist
            dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_YES_NO,
                                    (_("Creating a user with a UID less than 500 is not recommended.  "
                                       "Are you sure you want to do this?")))
            dlg.set_position(gtk.WIN_POS_CENTER)
            dlg.set_modal(True)
            dlg.set_icon_name(mainWindow.iconName)
            result = dlg.run()
            dlg.destroy()

            if result == gtk.RESPONSE_YES:
                pass
            else:
                self.ready()
                return

        userEnt.set(libuser.UIDNUMBER, [uidNumber])

        if self.newGroupCheck.get_active():   #Create new group

            group = self.parent.ADMIN.lookupGroupByName(userName)
            if group != None or gidDuplicate:
                # A group with this name or gid already exists.  Ask them what they want to do.
                dlg = gtk.Dialog()
                dlg.set_modal(True)
                dlg.set_icon_name(mainWindow.iconName)
                dlg.add_button(gtk.STOCK_CANCEL, 0)
                dlg.add_button(gtk.STOCK_OK, 1)
                dlg.set_border_width(4)
                dlg.vbox.set_spacing(4)

                if gidDuplicate:
                    label = gtk.Label(_("A group with this gid already exists.  What would you like to do?"))
                else:
                    label = gtk.Label(_("A group with this name already exists.  What would you like to do?"))
                label.set_line_wrap(True)
                dlg.vbox.pack_start(label)

                self.existingRadio = gtk.RadioButton(None, (_("Add to the existing group")))
                self.usersRadio = gtk.RadioButton(self.existingRadio, (_("Add to the 'users' group")))
                self.existingRadio.set_border_width(6)
                self.usersRadio.set_border_width(6)
                dlg.vbox.pack_start(self.existingRadio)
                dlg.vbox.pack_start(self.usersRadio)
                dlg.show_all()
                result = dlg.run()
                dlg.destroy()

                if result == 1:
                    #The clicked Ok, so do what they want
                    if self.existingRadio.get_active():
                        #Add the user to the existing group
                        if gidDuplicate:
                            cn = [userName, self.parent.ADMIN.lookupGroupById (gidNumber)]
                        else:
                            cn = group.get(libuser.GROUPNAME)[0]
                        #gidNumber = group.get(libuser.GIDNUMBER)[0]
                        userEnt.set(libuser.GIDNUMBER, [gidNumber])
                        self.userWinReset()
                        self.userWin.hide()
                    else:
                        #Add the user to the 'users' group
                        self.addToUsersGroup(userEnt, userName)
                        self.userWinReset()
                        self.userWin.hide()
                else:
                    #They clicked Cancel, so do nothing
                    self.ready()
                    return

            else:
                #No group currently exists with this name, so we can create one
                groupEnt = self.parent.ADMIN.initGroup(userName)
                groupEnt.set (libuser.GIDNUMBER, gidNumber)
                cn = groupEnt.get(libuser.GROUPNAME)[0]

                userEnt.set(libuser.GIDNUMBER, [gidNumber])
                members = groupEnt.get(libuser.MEMBERNAME)
                if not members:
                    members = []
                memberlist = string.join(members, ", ")

                self.parent.ADMIN.addGroup(groupEnt)
                self.parent.refresh_users_and_groups(cn)
                
                self.userWinReset()
                self.userWin.hide()

        else:
            #Add user to group 'users'
            self.addToUsersGroup(userEnt, userName)
            self.userWin.hide()

        if createHomeDir:
            #Create a home directory for the user
            self.parent.ADMIN.addUser(userEnt, mkhomedir = True)
        else:
            #Do not create a home directory for the user
            self.parent.ADMIN.addUser (userEnt, mkhomedir = False)

        self.parent.ADMIN.setpassUser(userEnt, pw, 0)
        self.parent.refresh_users_and_groups([userName, 'users'])
        self.ready()

    def addToUsersGroup(self, userEnt, userName):
        groupEnt = self.parent.ADMIN.lookupGroupByName('users')

        if groupEnt == None:
            #The 'users' doesn't exist.  Let's create one
            groupEnt = self.parent.ADMIN.initGroup('users')
            groupEnt.set(libuser.GIDNUMBER, 100)
            self.parent.ADMIN.addGroup(groupEnt)

        cn = groupEnt.get(libuser.GROUPNAME)[0]

        # try to get a name to associate with the user's primary gid,
        # and attempt to minimize lookups by caching answers
        try:
            gidNumber = groupEnt.get(libuser.GIDNUMBER)[0]
        except:
            #Uh-oh.  It looks like /etc/group and /etc/gshadow are out of sync.  Give up and quit.
            messageDialog.show_message_dialog(_("The system group database cannot be read.  This problem is most likely caused by a mismatch in /etc/group and /etc/gshadow.  The program will exit now."))
            import os
            os._exit(0)

        userEnt.set(libuser.GIDNUMBER, [gidNumber])

        members = groupEnt.get(libuser.MEMBERNAME)
        if not members:
            members = []

        members.append(userName)
        groupEnt.set(libuser.MEMBERNAME, members)
        self.parent.ADMIN.modifyGroup(groupEnt)
