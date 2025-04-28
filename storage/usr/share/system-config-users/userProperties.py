# -*- coding: utf-8 -*-
#
# userProperties.py - event handling code for userconf's user properties
# Copyright © 2001 - 2010 Red Hat, Inc.
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
import time
import string
import math
import locale
import libuser
import mainWindow
import messageDialog
import userGroupCheck

import gettext
_ = lambda x: gettext.ldgettext ("system-config-users", x)

busy_cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
ready_cursor = gtk.gdk.Cursor(gtk.gdk.LEFT_PTR)

class userProperties:
    defaultsInitialized = False
    pwAllowMin = 0
    pwAllowUnset = 0
    pwAllowMax = 99999
    pwRequireMin = 0
    pwRequireUnset = 99999
    pwRequireMax = 99999
    pwWarnMin = 0
    pwWarnUnset = 7
    pwWarnMax = 99999
    pwInactiveMin = -1
    pwInactiveUnset = -1
    pwInactiveMax = 99999

    def __init__(self, parent, user_clist, group_clist, xml, selinuxEnabled):
        self.parent = parent
        self.user_clist = user_clist
        self.group_clist = group_clist
        self.primaryGroupList = []

        if not userProperties.defaultsInitialized:
            ent = self.parent.ADMIN.initUser ('dummy')
            userProperties.pwAllowDefault = ent.get (libuser.SHADOWMIN, [userProperties.pwAllowUnset])[0]
            userProperties.pwRequireDefault = ent.get (libuser.SHADOWMAX, [userProperties.pwRequireUnset])[0]
            userProperties.pwWarnDefault = ent.get (libuser.SHADOWWARNING, [userProperties.pwWarnUnset])[0]
            userProperties.pwInactiveDefault = ent.get (libuser.SHADOWINACTIVE, [userProperties.pwInactiveUnset])[0]
            userProperties.defaultsInitialized = True
            del (ent)

        self.userWin = xml.get_widget('userProperties')
        self.userWin.connect("delete-event", self.on_cancel_button_clicked)
        self.userWin.set_icon_name(mainWindow.iconName)
        self.userWinUserName = xml.get_widget('userNameEntry')
        self.userWinUserName.set_max_length (userGroupCheck.maxusernamelength)
        self.userWinFullName = xml.get_widget('fullNameEntry')
        self.userWinPassword = xml.get_widget('passwordEntry')
        self.userWinConfirm = xml.get_widget('confirmEntry')
        self.userWinHomeDir = xml.get_widget('homeDirEntry')
        self.userWinHomeDir.set_max_length (userGroupCheck.maxpathlength)
        self.loginShellCombo = xml.get_widget('loginShellCombo')
        self.loginShellCombo.entry.set_property('editable', False)
        self.selinuxPropCombo = xml.get_widget("selinuxPropCombo")
        self.selinuxPropCombo.entry.set_property('editable', False)        
        self.selinuxPropLabel = xml.get_widget("selinuxPropLabel")
        self.userNotebook = xml.get_widget('userNotebook')
        self.lastChangedLabel = xml.get_widget('lastChangedLabel')

        self.accountLockCheck = xml.get_widget('accountLockCheck')
        self.accountExpireCheck = xml.get_widget('accountExpireCheck')
        self.accountMonthEntry = xml.get_widget('accountMonthEntry')
        self.accountDayEntry = xml.get_widget('accountDayEntry')
        self.accountYearEntry = xml.get_widget('accountYearEntry')
        self.accountHSep = xml.get_widget('accountHSep')
        self.accountHBox = xml.get_widget('newAccountHBox')
        self.pwExpireCheck = xml.get_widget('pwExpireCheck')
        self.pwExpireTable = xml.get_widget('pwExpireTable')
        self.pwAllowEntry = xml.get_widget('pwAllowEntry')
        self.pwRequireEntry = xml.get_widget('pwRequireEntry')
        self.pwWarnEntry = xml.get_widget('pwWarnEntry')
        self.pwInactiveEntry = xml.get_widget('pwInactiveEntry')
        self.groupVBox = xml.get_widget('userPropGroupVBox')

        if not selinuxEnabled:
            self.selinuxPropCombo.set_sensitive(False)
            self.selinuxPropLabel.set_sensitive(False)            

        self.selinuxRoleDict = { _("User"): "user_r", _("Staff") : "staff_r",
                                 _("System Administrator") : "sysadm_r"}
        roles = self.selinuxRoleDict.keys()
        roles.sort()
        self.selinuxPropCombo.set_popdown_strings(roles)

        self.groupStore = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING)
        self.groupTreeView = gtk.TreeView(self.groupStore)
        self.groupTreeView.set_property("headers-visible", False)

        self.checkboxrenderer = gtk.CellRendererToggle()
        self.checkboxrenderer.connect("toggled", self.toggled_item)
        col = gtk.TreeViewColumn(None, self.checkboxrenderer, active=0)
        self.groupTreeView.append_column(col)
        col = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=1)
        self.groupTreeView.append_column(col)

        self.groupChecklistSW = gtk.ScrolledWindow()
        self.groupChecklistSW = gtk.ScrolledWindow()
        self.groupChecklistSW.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.groupChecklistSW.set_shadow_type(gtk.SHADOW_IN)
        self.groupChecklistSW.add(self.groupTreeView)           
        self.groupVBox.pack_start(self.groupChecklistSW, True)

        self.shells = self.parent.ADMIN.getUserShells()
        self.shells.sort()
        self.loginShellCombo.set_popdown_strings(self.shells)

        self.groupHBox = gtk.HBox(False, 5)
        self.primaryGroupCombo = gtk.combo_box_entry_new_text ()
        self.primaryGroupCombo.child.set_property ("editable", False)
        self.groupHBox.pack_start(gtk.Label(_("Primary Group:")), False)
        self.groupHBox.pack_start(self.primaryGroupCombo, True)                                  
        self.groupVBox.pack_start(self.groupHBox, False)

        xml.signal_connect("on_cancel_button_clicked", self.on_cancel_button_clicked)
        xml.signal_connect("on_ok_button_clicked", self.on_ok_button_clicked)
        xml.signal_connect("on_accountExpireCheck_toggled", self.on_accountExpireCheck_toggled)
        xml.signal_connect("on_pwExpireCheck_toggled", self.on_pwExpireCheck_toggled)
        xml.signal_connect("on_accountLockCheck_toggled", self.on_accountLockCheck_toggled)

    def busy(self):
        self.userWin.set_sensitive(False)
        self.userWin.window.set_cursor(busy_cursor)

    def ready(self):
        self.userWin.window.set_cursor(ready_cursor)
        self.userWin.set_sensitive(True)

    def userWinReset(self):
        self.userNotebook.set_current_page(0)
        self.userWinUserName.set_text('')
        self.userWinFullName.set_text('')
        self.userWinPassword.set_text('')
        self.userWinConfirm.set_text('')
        self.userWinHomeDir.set_text('')
        self.groupStore.clear()

        self.accountLockCheck.set_active(False)
        self.on_accountLockCheck_toggled()
        self.accountExpireCheck.set_active(False)
        self.accountMonthEntry.set_text("")
        self.accountDayEntry.set_text("")
        self.accountYearEntry.set_text("")
        self.pwExpireCheck.set_active(False)
        self.pwAllowEntry.set_text(str (self.pwAllowDefault))
        self.pwRequireEntry.set_text(str (self.pwRequireDefault))
        self.pwWarnEntry.set_text(str (self.pwWarnDefault)) 
        self.pwInactiveEntry.set_text(str (self.pwInactiveDefault)) 
        
    def showUserProperties(self, userEnt):
        self.userEnt = userEnt
        self.userWinReset()

        uid = self.userEnt.get(libuser.USERNAME)[0]
        uidNumber = self.userEnt.get(libuser.UIDNUMBER)[0]
        if uidNumber == 0:
            #Don't allow root account to be locked
            self.accountLockCheck.set_sensitive(False)
        else:
            self.accountLockCheck.set_sensitive(True)
        self.on_accountLockCheck_toggled()

        fn = self.userEnt.get(libuser.GECOS)[0]
        #Convert the user fullName into unicode so pygtk2 doesn't truncate strings
        fn = unicode (fn, encoding = 'utf-8', errors = 'replace')
        hd = self.userEnt.get(libuser.HOMEDIRECTORY)[0]
        shell = self.userEnt.get(libuser.LOGINSHELL)[0]

        self.userWinUserName.set_text(uid)
        if uid == "root":
            #Don't allow root uid to be changed
            self.userWinUserName.set_sensitive(False)

        self.userWinFullName.set_text(fn)
        self.userWinPassword.set_text('     ')
        self.userWinConfirm.set_text('     ')
        self.userWinHomeDir.set_text(hd)

        if shell not in self.shells:
            self.shells.append(shell)
            self.shells.sort()
            self.loginShellCombo.set_popdown_strings(self.shells)
        self.loginShellCombo.list.select_item(self.shells.index(shell))

        lastChange = self.userEnt.get(libuser.SHADOWLASTCHANGE)
        if lastChange:
            daysSinceEpoch = lastChange[0]
            secondsPerDay = 24 * 60 * 60
            secondsSinceEpoch = int(daysSinceEpoch) * int(secondsPerDay)
            age = time.strftime("%c", time.gmtime(secondsSinceEpoch))
            age = unicode (age, locale.nl_langinfo (locale.CODESET)).encode ("utf-8")
            self.lastChangedLabel.set_text(age)

        if "shadow" in self.userEnt.modules () \
            or "ldap" in self.userEnt.modules ():
            expire = self.userEnt.get(libuser.SHADOWEXPIRE)

            if expire:
                try:
                    if int(expire[0]) != self.pwInactiveDefault:
                        self.accountExpireCheck.set_active(True)
                        days = int (self.userEnt.get(libuser.SHADOWEXPIRE)[0])
                        tmp = days * int(secondsPerDay)
                        age = time.localtime(tmp)
                        year = str(age[0])
                        month = str(age[1])
                        day = str(age[2])
                        self.accountMonthEntry.set_text(month)
                        self.accountDayEntry.set_text(day)
                        self.accountYearEntry.set_text(year)
                except:
                    self.accountExpireCheck.set_active(False)

            min = self.userEnt.get (libuser.SHADOWMIN, [self.pwAllowDefault])
            max = self.userEnt.get (libuser.SHADOWMAX, [self.pwRequireDefault])
            warning = self.userEnt.get (libuser.SHADOWWARNING, [self.pwWarnDefault])
            inactive = self.userEnt.get (libuser.SHADOWINACTIVE, [self.pwInactiveDefault])

            if int(min[0]) == self.pwAllowUnset \
                and int(max[0]) == self.pwRequireUnset \
                and int(warning[0]) == self.pwWarnUnset \
                and int(inactive[0]) == self.pwInactiveUnset:
                self.pwExpireCheck.set_active(False)
            else:
                self.pwExpireCheck.set_active(True)
                self.pwAllowEntry.set_text(str(min[0]))
                self.pwRequireEntry.set_text(str(max[0]))
                self.pwWarnEntry.set_text(str(warning[0]))
                self.pwInactiveEntry.set_text(str(inactive[0]))

        if self.parent.ADMIN.userIsLocked(self.userEnt) == 1:
            self.accountLockCheck.set_active(True)

        self.fill_groups_list(self.userEnt)
        self.set_default_group(self.userEnt)
        self.userWin.show_all()

        #Hide SELinux widgets for now
        self.selinuxPropCombo.hide()
        self.selinuxPropLabel.hide()

        if "shadow" not in self.userEnt.modules () \
            and "ldap" not in self.userEnt.modules ():
            #hide the account expiration and password expiration widgets if shadow passwords are not enabled
            self.accountExpireCheck.hide()
            self.accountHBox.hide()
            self.accountHSep.hide()
            self.userNotebook.get_nth_page(2).hide()

    def on_cancel_button_clicked(self, *args):
        self.userWinReset()
        self.userWin.hide()
        return True

    def on_ok_button_clicked(self, *args):
        self.busy()
        #The logic here is kind of complicated, but I'll try to explain
        newUserName = self.userWinUserName.get_text()
        
        userName = self.userEnt.get(libuser.USERNAME)[0]
        gecos = self.userWinFullName.get_text()
        pw = self.userWinPassword.get_text()
        confirm = self.userWinConfirm.get_text()

        # Avoid empty group names
        if newUserName == "":
            messageDialog.show_message_dialog (_("Please enter a user name."))
            self.ready ()
            self.userWinUserName.set_text ("")
            self.userWinUserName.grab_focus ()
            return

        # Check for UTF-8-only strings
        if not userGroupCheck.isUsernameOk(newUserName, self.userWinUserName):
            self.ready()
            self.userWinUserName.grab_focus()
            return

        if not userGroupCheck.isNameOk(gecos, self.userWinFullName):
            self.ready()
            self.userWinFullName.grab_focus()
            return

        # Avoid duplicate user names
        if userName != newUserName and userGroupCheck.userExists (self.parent.ADMIN, newUserName):
            messageDialog.show_message_dialog (_("The user '%s' already exists. Please choose a different name.") % newUserName)
            self.ready ()
            self.userWinUserName.set_text ("")
            self.userWinUserName.grab_focus ()
            return

        hd = self.userWinHomeDir.get_text()
        shell = self.loginShellCombo.entry.get_text()
        primaryGroup = self.userEnt.get(libuser.GIDNUMBER)[0]

        if pw == confirm == '     ':
            pass
        elif pw == confirm and len (pw) >= 6:
            #Check for ascii-only strings
            if not userGroupCheck.isPasswordOk(pw, self.userWinPassword):
                self.ready()
                self.userWinPassword.grab_focus()
                return

            self.parent.ADMIN.setpassUser(self.userEnt, pw, 0)
        else:
            if not pw and not confirm:
                messageDialog.show_message_dialog(_("Please enter a password for the user."))
            
                self.ready()
                self.userNotebook.set_current_page(0)
                self.userWinPassword.set_text("")
                self.userWinConfirm.set_text("")
                self.userWinPassword.grab_focus()
                return
            elif len (pw) < 6:
                messageDialog.show_message_dialog(_("The password is too short.  Please "
                                                    "use at least 6 characters."))
                self.ready()
                self.userNotebook.set_current_page(0)
                self.userWinPassword.set_text("")
                self.userWinConfirm.set_text("")
                self.userWinPassword.grab_focus()
                return
            else:
                messageDialog.show_message_dialog(_("Passwords do not match."))

                self.ready()
                self.userNotebook.set_current_page(0)
                self.userWinPassword.set_text("")
                self.userWinConfirm.set_text("")
                self.userWinPassword.grab_focus()                
                return

        if not userGroupCheck.isHomedirOk(hd, self.userWinHomeDir, need_homedir = False):
            self.ready()
            self.userWinHomeDir.set_text(self.userEnt.get(libuser.HOMEDIRECTORY)[0])
            self.userWinHomeDir.grab_focus()
            return

        self.userEnt.set (libuser.USERNAME, newUserName)
        self.userEnt.set (libuser.GECOS, gecos)
        if hd != "":
            self.userEnt.set (libuser.HOMEDIRECTORY, hd)
        else:
            self.userEnt.clear (libuser.HOMEDIRECTORY)
        self.userEnt.set (libuser.LOGINSHELL, shell)

        group_list = []
        need_refresh = [newUserName]
        members = []

        #Let's iterate through the groupStore and see what groups are selected
        iter = self.groupStore.get_iter_root()
        
        while iter:
            val = self.groupStore.get_value(iter, 0)
            group = self.groupStore.get_value(iter, 1)

            try:
                groupEnt = self.parent.group_dict[group]
            except:
                groupEnt = self.parent.ADMIN.lookupGroupByName(group)
            gid = groupEnt.get(libuser.GIDNUMBER)[0]
            members = groupEnt.get(libuser.MEMBERNAME)
            if not members:
                members = []
            elif newUserName != userName and userName in members:
                # username has changed, remove references to old name
                members.remove (userName)
                groupEnt.set (libuser.MEMBERNAME, members)
                self.parent.ADMIN.modifyGroup (groupEnt)
                need_refresh.append(group)

            if val:
                try:
                   index = members.index(newUserName)
                except:
                   index = -1

                if index == -1:
                    # the user is not in the group, but should be
                    need_refresh.append(group)
                    if primaryGroup != gid:
                        members.append(newUserName)
                        groupEnt.set(libuser.MEMBERNAME, members)
                        self.parent.ADMIN.modifyGroup(groupEnt)
            else:
                try:
                   index = members.index(newUserName)
                except:
                   index = -1
                if index >= 0:
                    # the user is not supposed to be in the group, but is
                    need_refresh.append(group)
                    members.remove(newUserName)
                    groupEnt.set(libuser.MEMBERNAME, members)
                    self.parent.ADMIN.modifyGroup(groupEnt)

            iter = self.groupStore.iter_next(iter)

        if self.primaryGroupCombo.child.get_text() == "":
            messageDialog.show_message_dialog(_("Please select at least one group for the user."))

            self.ready()
            self.userNotebook.set_current_page(3)            
            return            
        else:
            primaryGroupEnt = self.parent.ADMIN.lookupGroupByName(self.primaryGroupCombo.child.get_text())
            if primaryGroupEnt == None:
                primaryGroupId = int(self.primaryGroupCombo.child.get_text())
            else:
                primaryGroupId = primaryGroupEnt.get(libuser.GIDNUMBER)[0]
            self.userEnt.set(libuser.GIDNUMBER, [primaryGroupId])
        
        if self.accountExpireCheck.get_active():
            year = string.strip(self.accountYearEntry.get_text())
            month = string.strip(self.accountMonthEntry.get_text())
            day = string.strip(self.accountDayEntry.get_text())

            if month == "":
                messageDialog.show_message_dialog(_("Please specify the month that the password will expire."))
                self.ready()
                self.userNotebook.set_current_page(1)
                self.accountMonthEntry.set_text("")
                self.accountMonthEntry.grab_focus()
                return

            if day == "":
                messageDialog.show_message_dialog(_("Please specify the day that the password will expire."))
                self.ready()
                self.userNotebook.set_current_page(1)
                self.accountDayEntry.set_text("")
                self.accountDayEntry.grab_focus()
                return
                
            if year == "":
                messageDialog.show_message_dialog(_("Please specify the year that the password will expire."))
                self.ready()
                self.userNotebook.set_current_page(1)
                self.accountYearEntry.set_text("")
                self.accountYearEntry.grab_focus()
                return

            year = int(year)
            month = int(month)
            day = int(day)

            timetuple = [ year, month, day, 0, 0, 0, 0, 0, -1 ]
            try:
                tmp = time.mktime (timetuple)
            except OverflowError:
                # mktime will throw an OverflowError if the year is too big.  
                messageDialog.show_message_dialog (_("The year is out of range.  Please select a different year."))
                self.ready ()
                self.userNotebook.set_current_page (1)
                self.accountYearEntry.set_text ("")
                self.accountYearEntry.grab_focus ()
                return
                
            seconds = 24 * 60 * 60
            daysTillExpire = tmp / seconds
            fraction, integer = math.modf(daysTillExpire)

            if fraction == 0.0:
                daysTillExpire = integer
            else:
                daysTillExpire = integer + 1

            self.userEnt.set(libuser.SHADOWEXPIRE, daysTillExpire)
        else:
            self.userEnt.set(libuser.SHADOWEXPIRE, self.pwInactiveDefault)

        if self.pwExpireCheck.get_active():
            allowed = string.strip(self.pwAllowEntry.get_text())
            required = string.strip(self.pwRequireEntry.get_text())
            warning = string.strip(self.pwWarnEntry.get_text())
            inactive = string.strip(self.pwInactiveEntry.get_text())

            for (var, widget, min, max, emptytext, invalidtext) in (
                    (allowed, self.pwAllowEntry,
                        self.pwAllowMin, self.pwAllowMax,
                        _("Please specify the number of days before "
                            "changing the password is allowed."),
                        _("The number of days before changing the password "
                            "is allowed must be between %(min)d and %(max)d.")
                        % {'min': self.pwAllowMin, 'max': self.pwAllowMax}),
                    (required, self.pwRequireEntry,
                        self.pwRequireMin, self.pwRequireMax,
                        _("Please specify the number of days before "
                            "changing the password is required."),
                        _("The number of days before changing the password "
                            "is required must be between %(min)d and %(max)d.")
                        % {'min': self.pwRequireMin, 'max': self.pwRequireMax}),
                    (warning, self.pwWarnEntry, self.pwWarnMin, self.pwWarnMax,
                        _("Please specify the number of days to warn the user before "
                            "changing the password is required."),
                        _("The number of days to warn the user before changing "
                            "the password is required must be between "
                            "%(min)d and %(max)d.")
                        % {'min': self.pwWarnMin, 'max': self.pwWarnMax}),
                    (inactive, self.pwInactiveEntry,
                        self.pwInactiveMin, self.pwInactiveMax,
                        _("Please specify the number of days until the user "
                            "account becomes inactive after password has expired."),
                        _("The number of days until the user account becomes "
                            "inactive after the password has expired "
                            "must be between %(min)d and %(max)d. "
                            "Setting it to -1 means the account "
                            "won't become inactive.")
                        % {'min': self.pwInactiveMin, 'max': self.pwInactiveMax})
                ):
                error = False

                if var == "":
                    messageDialog.show_message_dialog (emptytext)
                    error = True
                else:
                    nonint = False
                    try:
                        x = int (var)
                    except ValueError:
                        nonint = True

                    if nonint or x < min or x > max:
                        messageDialog.show_message_dialog (invalidtext)
                        error = True
                
                if error:
                    self.ready ()
                    self.userNotebook.set_current_page (2)
                    widget.set_text ("")
                    widget.grab_focus ()
                    return


            # FIXME: report to the user instead of raising an exception if the
            # field is not numeric
            self.userEnt.set(libuser.SHADOWMIN, int(allowed))
            self.userEnt.set(libuser.SHADOWMAX, int(required))
            self.userEnt.set(libuser.SHADOWWARNING, int(warning))
            self.userEnt.set(libuser.SHADOWINACTIVE, int(inactive))
        else:
            self.userEnt.set(libuser.SHADOWMIN, self.pwAllowUnset)
            self.userEnt.set(libuser.SHADOWMAX, self.pwRequireUnset)
            self.userEnt.set(libuser.SHADOWWARNING, self.pwWarnUnset)
            self.userEnt.set(libuser.SHADOWINACTIVE, self.pwInactiveUnset)

        self.parent.ADMIN.modifyUser(self.userEnt)

        if self.accountLockCheck.get_active():
            if self.parent.ADMIN.userIsLocked(self.userEnt) == 0:
                self.parent.ADMIN.lockUser(self.userEnt)
        else:
            if self.parent.ADMIN.userIsLocked(self.userEnt) == 1:
                self.parent.ADMIN.unlockUser(self.userEnt)

        self.parent.refresh_users_and_groups(need_refresh)
        self.userWinReset()
        self.userWin.hide()
        self.ready()

    def on_accountExpireCheck_toggled(self, *args):
        self.accountHBox.set_sensitive(self.accountExpireCheck.get_active())

    def on_pwExpireCheck_toggled(self, *args):
        self.pwExpireTable.set_sensitive(self.pwExpireCheck.get_active())

    def on_accountLockCheck_toggled(self, *args):
        isLocked = self.accountLockCheck.get_active ()
        self.userWinPassword.set_sensitive (not isLocked)
        self.userWinConfirm.set_sensitive (not isLocked)

    def toggled_item(self, data, row):
        #Store the current selection temporarily.  Otherwise, calling set_popdown_strings will erase it
        tempName = self.primaryGroupCombo.child.get_text()
        
        iter = self.groupStore.get_iter(int(row))
        val = self.groupStore.get_value(iter, 0)
        group = self.groupStore.get_value(iter, 1)
        self.groupStore.set_value(iter, 0, not val)

        if self.primaryGroupList == [""]:
            self.primaryGroupList = []
            
        if val == 0:
            if group not in self.primaryGroupList:
                self.primaryGroupList.append(group)
        elif val ==1:
            if group in self.primaryGroupList:
                self.primaryGroupList.remove(group)
        
        if self.primaryGroupList == []:
            self.primaryGroupList.append("")

        #Sort the list before pushing it into the combo widget    
        self.primaryGroupList.sort()
        #Push the list into the combo widget
        self.primaryGroupCombo.get_model ().clear ()
        map (self.primaryGroupCombo.append_text, self.primaryGroupList)

        if tempName in self.primaryGroupList:
            #If the tempName is still in the list, preserve the current setting
            self.primaryGroupCombo.set_active (self.primaryGroupList.index (tempName))
        else:
            #The tempName is no longer in the list, so select the first choice in the list
            self.primaryGroupCombo.set_active (0)

    def fill_groups_list (self, userEnt):
        self.groups = self.parent.ADMIN.enumerateGroups()
        self.groups.sort()
        row = 0
        uid = userEnt.get(libuser.USERNAME)[0]
        usergroups = self.parent.ADMIN.enumerateGroupsByUser(uid)
        self.primaryGroupList = []

        for group in self.groups:
            if group in usergroups:
                iter = self.groupStore.append()
                self.groupStore.set_value(iter, 0, True)
                self.groupStore.set_value(iter, 1, group)
                self.primaryGroupList.append(group)
            else:
                iter = self.groupStore.append()
                self.groupStore.set_value(iter, 0, False)
                self.groupStore.set_value(iter, 1, group)

    def set_default_group (self, userEnt):
        primaryGroupId = userEnt.get(libuser.GIDNUMBER)[0]        
        primaryGroupEnt = self.parent.ADMIN.lookupGroupById(primaryGroupId)
        if primaryGroupEnt == None:
            primaryGroupName = str(primaryGroupId)
            self.primaryGroupList.append(primaryGroupName)
            self.primaryGroupCombo.get_model ().clear ()
            map (self.primaryGroupCombo.append_text, self.primaryGroupList)
            self.primaryGroupCombo.set_active (len (self.primaryGroupList))
        else:
            self.primaryGroupCombo.get_model ().clear ()
            map (self.primaryGroupCombo.append_text, self.primaryGroupList)
            primaryGroupName = primaryGroupEnt.get(libuser.GROUPNAME)[0]
            self.primaryGroupCombo.set_active (self.primaryGroupList.index (primaryGroupName))

