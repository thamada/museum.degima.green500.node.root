# -*- coding: utf-8 -*-
#
# mainWindow.py - main interface window for redhat-config-users
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
import gtk.glade
import string
import os
import rpm
import shutil

import libuser

import preferences

import groupWindow
import userWindow
import userProperties
import groupProperties
import messageDialog
import prefWindow

import gettext
_ = lambda x: gettext.ldgettext ("system-config-users", x)
N_ = lambda x: x

def service_pending_events():
    while gtk.events_pending():
        if gtk.__dict__.has_key ("main_iteration"):
            gtk.main_iteration()
        else:
            gtk.mainiteration()

domain = "system-config-users"
gtk.glade.bindtextdomain(domain)
if os.access("system-config-users.glade", os.F_OK):
    xml = gtk.glade.XML ("./system-config-users.glade", domain=domain)
else:
    xml = gtk.glade.XML ("/usr/share/system-config-users/system-config-users.glade", domain=domain)

busy_cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
ready_cursor = gtk.gdk.Cursor(gtk.gdk.LEFT_PTR)

##
## Icon for windows
##
iconName = "system-users"

##
## email/url/help functions and callbacks
##
def help_display (url):
    paths = ["/usr/bin/yelp", None]

    for path in paths:
        if path and os.access (path, os.X_OK):
            break

    if path == None:
        messageDialog.show_message_dialog (_("The help viewer could not be found. To be able to view help you need to install the 'yelp' package."))
        return
    
    pid = os.fork()
    if not pid:
        os.execv(path, [path, url])

def url_display (url):
    paths = ["/usr/bin/xdg-open", None]

    for path in paths:
        if path and os.access (path, os.X_OK):
            break

    if path == None:
        messageDialog.show_message_dialog (_("No helper application for the URL '%(url)s can be found.") % {'url': url})
        return
    
    pid = os.fork()
    if not pid:
        os.execv(path, [path, url])

def open_email (dialog, email, *args, **kwargs):
    url_display ('mailto:%s' % email)
gtk.about_dialog_set_email_hook (open_email)

def open_url (dialog, link, *args, **kwargs):
    url_display (link)
gtk.about_dialog_set_url_hook (open_url)

class mainWindow:

    def version():
        # substituted to the real version by the Makefile at installation time.
        return ""

    def destroy (self, *args):
        try:
            self.preferences.save ()
        except IOError:
            print _("Error saving settings to %s") % preferences.filename
        if gtk.__dict__.has_key ("main_quit"):
            gtk.main_quit()
        else:
            gtk.mainquit()

    def __init__(self):
        self.preferences = preferences.Preferences ()
        self.preferences.load ()
        self.prefWindow = prefWindow.PrefWindow (xml)
        nameTag = _("Users and Groups")
        commentTag = _("Add or remove users and groups")
        
        self.toplevel = xml.get_widget ('mainWindow')
        self.toplevel.resize(775, 550)
        self.toplevel.set_icon_name(iconName)
        self.add_user_button = xml.get_widget("add_user_button")
        self.add_group_button = xml.get_widget("add_group_button")
        self.properties_button = xml.get_widget("properties_button")
        self.properties_menu = xml.get_widget("properties_menu")
        self.delete_button = xml.get_widget("delete_button")
        self.delete_menu = xml.get_widget("delete_menu")
        self.toplevel.connect("destroy", self.destroy)

        self.ADMIN = libuser.admin()

        self.userStore = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_UINT64, gobject.TYPE_STRING,
                                       gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING,
                                       gobject.TYPE_PYOBJECT)
        self.userStore.set_sort_column_id(1, gtk.SORT_ASCENDING)        
        self.userTreeView = xml.get_widget('user_view')
        self.userTreeView.set_rules_hint(True)
        self.userTreeView.set_model(self.userStore)
        self.userTreeView.get_selection().connect("changed", self.itemSelected)
        self.userTreeView.connect("row_activated", self.rowActivated)

        col = gtk.TreeViewColumn(_("User Name"), gtk.CellRendererText(), text=0)
        col.set_sort_column_id(0)
        col.set_resizable(True)
        self.userTreeView.append_column(col)
        col = gtk.TreeViewColumn(_("User ID"), gtk.CellRendererText(), text=1)
        col.set_sort_column_id(1)
        col.set_resizable(True)
        self.userTreeView.append_column(col)
        col = gtk.TreeViewColumn(_("Primary Group"), gtk.CellRendererText(), text=2)
        col.set_sort_column_id(2)
        col.set_resizable(True)
        self.userTreeView.append_column(col)
        col = gtk.TreeViewColumn(_("Full Name"), gtk.CellRendererText(), text=3)
        col.set_sort_column_id(3)
        col.set_resizable(True)
        self.userTreeView.append_column(col)
        col = gtk.TreeViewColumn(_("Login Shell"), gtk.CellRendererText(), text=4)
        col.set_sort_column_id(4)
        col.set_resizable(True)
        self.userTreeView.append_column(col)
        col = gtk.TreeViewColumn(_("Home Directory"), gtk.CellRendererText(), text=5)
        col.set_sort_column_id(5)
        col.set_resizable(True)
        self.userTreeView.append_column(col)

        self.userTreeView.set_property("headers-visible", True)

        self.groupStore = gtk.ListStore(gobject.TYPE_STRING,
                                        gobject.TYPE_UINT64,
                                        gobject.TYPE_STRING,
                                        gobject.TYPE_PYOBJECT)
        self.groupStore.set_sort_column_id(1, gtk.SORT_ASCENDING)
        self.groupTreeView = xml.get_widget('group_view')
        self.groupTreeView.set_rules_hint(True)
        self.groupTreeView.set_model(self.groupStore)
        self.groupTreeView.get_selection().connect("changed", self.itemSelected)
        self.groupTreeView.connect("row_activated", self.rowActivated)
        
        col = gtk.TreeViewColumn(_("Group Name"), gtk.CellRendererText(), text=0)
        col.set_sort_column_id(0)
        col.set_resizable(True)
        self.groupTreeView.append_column(col)
        col = gtk.TreeViewColumn(_("Group ID"), gtk.CellRendererText(), text=1)
        col.set_sort_column_id(1)
        col.set_resizable(True)
        self.groupTreeView.append_column(col)
        col = gtk.TreeViewColumn(_("Group Members"), gtk.CellRendererText(), text=2)
        col.set_resizable(True)
        self.groupTreeView.append_column(col)

        self.notebook = xml.get_widget('notebook1')
        self.notebook.connect('switch-page', self.changeNotebookPage)
        self.filter = xml.get_widget('filterEntry')

        self.filterSystemUsersGroupsCheckButton = xml.get_widget ('filterSystemUsersGroupsCheckButton')
        self.filterSystemUsersGroupsCheckButton.set_active (self.preferences['FILTER'])
        self.assignHighestUidCheckButton = xml.get_widget ('assignHighestUidCheckButton')
        self.assignHighestUidCheckButton.set_active (self.preferences['ASSIGN_HIGHEST_UID'])
        self.assignHighestGidCheckButton = xml.get_widget ('assignHighestGidCheckButton')
        self.assignHighestGidCheckButton.set_active (self.preferences['ASSIGN_HIGHEST_GID'])
        self.preferSameUIDGIDCheckButton = xml.get_widget ('preferSameUIDGIDCheckButton')
        self.preferSameUIDGIDCheckButton.set_active (self.preferences['PREFER_SAME_UID_GID'])

        self.user_dict = {}
        self.group_dict = {}
        self.gid_dict = {}
        self.member_dict = {}
        self.service_interval = 10

        selinuxEnabled = self.isSELinuxEnabled()

        self.userWin = userWindow.userWindow(self, self.userStore, self.groupTreeView, xml, selinuxEnabled)
        self.groupWin = groupWindow.groupWindow(self, self.userTreeView, self.groupTreeView, xml)
        self.userProperties = userProperties.userProperties(self, self.userTreeView, self.groupTreeView, xml, selinuxEnabled)
        self.groupProperties = groupProperties.groupProperties(self, self.userTreeView, self.groupTreeView, xml)
        self.userSelectedRow = None
        self.groupSelectedRow = None
        self.toplevel.show_all ()

        xml.signal_connect("on_about_activate", self.on_about_button_clicked)
        xml.signal_connect("on_manual_activate", self.on_manual_button_clicked)
        xml.signal_connect("on_add_user_activate", self.on_add_user_activate)
        xml.signal_connect("on_add_user_button_clicked", self.on_add_user_activate)
        xml.signal_connect("on_add_group_activate", self.on_add_group_activate)
        xml.signal_connect("on_add_group_button_clicked", self.on_add_group_activate)
        xml.signal_connect("on_properties_activate", self.on_properties_activate)
        xml.signal_connect("on_properties_button_clicked", self.on_properties_activate)
        xml.signal_connect("on_preferences_activate", self.on_preferences_activate)
        xml.signal_connect("on_delete_activate", self.on_delete_activate)
        xml.signal_connect("on_delete_button_clicked", self.on_delete_activate)
        xml.signal_connect("on_help_button_clicked", self.on_help_button_clicked)
        xml.signal_connect("on_new_user_activate", self.on_add_user_activate)
        xml.signal_connect("on_filterButton_clicked", self.refresh)
        xml.signal_connect("on_filterEntry_activate", self.refresh)
        xml.signal_connect("on_refreshButton_clicked", self.refresh)
        xml.signal_connect("on_exit_activate", self.on_exit_activate)

        xml.signal_connect("on_filterSystemUsersGroupsCheckButton_toggled", self.on_filterSystemUsersGroupsCheckButton_toggled)
        xml.signal_connect("on_assignHighestUidCheckButton_toggled", self.on_assignHighestUidCheckButton_toggled)
        xml.signal_connect("on_assignHighestGidCheckButton_toggled", self.on_assignHighestGidCheckButton_toggled)
        xml.signal_connect("on_preferSameUIDGIDCheckButton_toggled", self.on_preferSameUIDGIDCheckButton_toggled)

        self.refresh()
        self.ready()
        if gtk.__dict__.has_key ("main"):
            gtk.main ()
        else:
            gtk.mainloop ()

    def on_exit_activate(self, args):
        self.destroy()

    def busy(self):
        self.toplevel.set_sensitive(False)
        self.toplevel.window.set_cursor(busy_cursor)
        pass

    def ready(self):
        self.toplevel.window.set_cursor(ready_cursor)
        self.toplevel.set_sensitive(True)
        pass

    def get_user_list (self, filter):
        if filter == "":
            users = self.ADMIN.enumerateUsersFull()
        else:
            users = self.ADMIN.enumerateUsersFull(filter)

        users.sort()
        return users

    def get_group_list(self, filter):
        if filter == "":
            groups = self.ADMIN.enumerateGroupsFull()
        else:
            groups = self.ADMIN.enumerateGroupsFull(filter)
        groups.sort()

        return groups

    def refresh_users(self):
        self.user_dict = {}
        self.gid_dict = {}
        inconsistent_users = []

        # pull up information about users and store the objects in
        # a dictionary keyed by user name
        i = 0
        for user in self.get_user_list(self.get_filter_data()):
            i = i + 1
            if i >= self.service_interval:
                service_pending_events()
                i = 0

            userName = user.get(libuser.USERNAME)[0]
            self.user_dict[userName] = user

            # try to get a name to associate with the user's primary gid,
            # and attempt to minimize lookups by caching answers
            gidNumber = -1
            try:
                gidNumber = user.get(libuser.GIDNUMBER)[0]
            except IndexError:
                if userName not in inconsistent_users:
                    inconsistent_users.append (userName)

            if gidNumber >= 0:
                try:
                    group = self.gid_dict[long (gidNumber)]
                except KeyError:
                    group = self.ADMIN.lookupGroupById(long (gidNumber))
                    self.gid_dict[long (gidNumber)] = group

        inconsistent_users.sort ()
        return inconsistent_users

    def refresh_groups(self):
        self.group_dict = {}
        self.member_dict = {}
        inconsistent_groups = []

        i = 0
        for group in self.get_group_list(self.get_filter_data()):
            i = i + 1
            if i >= self.service_interval:
                service_pending_events()
                i = 0

            groupName = group.get(libuser.GROUPNAME)[0]

            # /etc/group <-> /etc/gshadow inconsistency canary
            try:
                gidNumber = group.get (libuser.GIDNUMBER)[0]
            except IndexError:
                if groupName not in inconsistent_groups:
                    inconsistent_groups.append (groupName)

            self.group_dict[groupName] = group

            members = self.ADMIN.enumerateUsersByGroup(groupName)

            if not members:
                members = []
                
            members.sort()

            self.member_dict[groupName] = members

        inconsistent_groups.sort ()
        return inconsistent_groups

    def refresh_users_and_groups(self, names):
        self.busy()
        updated_names = {}
        for name in names:
            # If we've already updated this user/group, skip it.
            if updated_names.has_key(name):
                continue
            updated_names[name] = name
            service_pending_events()

            userEnt = self.ADMIN.lookupUserByName(name)
            if userEnt:
                self.user_dict[name] = userEnt
                try:
                    gidNumber = userEnt.get(libuser.GIDNUMBER)[0]
                    try:
                        groupEnt = self.gid_dict[long (gidNumber)]
                    except KeyError:
                        try:
                            groupEnt = self.ADMIN.lookupGroupById(long (gidNumber))
                            self.gid_dict[long (gidNumber)] = groupEnt
                        except:
                            pass
                except IndexError:
                    pass
            else:
                try:
                    del (self.user_dict[name])
                except:
                    pass

            groupEnt = self.ADMIN.lookupGroupByName(name)
            if groupEnt:
                self.group_dict[name] = groupEnt
                self.member_dict[name] = self.ADMIN.enumerateUsersByGroup(name)
                try:
                    gidNumber = groupEnt.get(libuser.GIDNUMBER)[0]
                    self.gid_dict[long (gidNumber)] = groupEnt
                except IndexError:
                    pass
            else:
                try:
                    del(self.group_dict[name])
                    del(self.member_dict[name])
                except:
                    pass

        users = self.get_user_list(self.get_filter_data())
        for user in self.user_dict.keys():
            if user not in users:
                del self.user_dict[user]

        groups = self.get_group_list(self.get_filter_data())
        for group in self.group_dict.keys():
            if group not in groups:
                del self.group_dict[group]

        self.refresh()
        self.ready()

    def refresh(self, *args):
        self.busy()
        inconsistent_users = self.refresh_users()
        inconsistent_groups = self.refresh_groups()
        consistent = True

        if len (inconsistent_users):
            consistent = False
            msg_users = gettext.ngettext (
                    N_("I couldn't find the numerical ID of the user '%(user)s'.\n\n"),
                    N_("I couldn't find the numerical IDs of these users:\n%(users)s\n\n"),
                    len (inconsistent_users)) % {
                            'user': inconsistent_users[0],
                            'users': '\n'.join (inconsistent_users)
                            }
        else:
            msg_users = ""

        if len (inconsistent_groups):
            consistent = False
            msg_groups = gettext.ngettext (
                    N_("I couldn't find the numerical ID of the group '%(group)s'.\n\n"),
                    N_("I couldn't find the numerical IDs of these groups:\n%(groups)s\n\n"),
                    len (inconsistent_groups)) % {
                            'group': inconsistent_groups[0],
                            'groups': '\n'.join (inconsistent_groups)
                            }
        else:
            msg_groups = ""

        if not consistent:
            messageDialog.show_message_dialog (
                    _("%(msg_users)s%(msg_groups)s\nIn most cases this is caused by inconsistencies in the user or group database, e.g. between the files /etc/passwd, /etc/group and their respective shadow files /etc/shadow and /etc/gshadow. I will try to ignore these entries and continue for now, but please fix these inconsistencies as soon as possible.") % {
                        'msg_users': msg_users,
                        'msg_groups': msg_groups
                        })

        self.populate_lists()
        self.toggleWidgets(False)
        self.ready()

    def populate_user_list(self):
        self.userStore.clear()
        for user in self.user_dict.keys():
            userEnt = self.user_dict[user]
            uid = userEnt.get(libuser.USERNAME)[0]
            consistent = True
            uidNumber = -1
            gidNumber = -1
            try:
                uidNumber = userEnt.get(libuser.UIDNUMBER)[0]
                gidNumber = userEnt.get(libuser.GIDNUMBER)[0]
            except IndexError:
                # user present in /etc/shadow but not /etc/passwd
                consistent = False

            if userEnt.get(libuser.GECOS):
                gecos = userEnt.get(libuser.GECOS)[0]
            else:
                gecos = uid
            if userEnt.get(libuser.HOMEDIRECTORY):
                homeDir = userEnt.get(libuser.HOMEDIRECTORY)[0]
            else:
                homeDir = ''
            if userEnt.get(libuser.LOGINSHELL):
                shell = userEnt.get(libuser.LOGINSHELL)[0]
            else:
                shell = ''

            try:
                groupEnt = self.gid_dict[long (gidNumber)]
                groupName = groupEnt.get(libuser.GROUPNAME)[0]
            except:
                groupName = gidNumber

            #Convert the user fullName into unicode so pygtk2 doesn't truncate strings
            gecos = unicode (gecos, encoding = 'utf-8', errors = 'replace')

            if self.preferences['FILTER'] == True:
                #display users with UIDs > 499
                if long (uidNumber) > 499L and not (uid == "nfsnobody" and (long (uidNumber) == 65534L or long (uidNumber) == 4294967294L)):
                    iter = self.userStore.append()
                    self.userStore.set_value(iter, 0, uid)
                    self.userStore.set_value(iter, 1, uidNumber)
                    self.userStore.set_value(iter, 2, groupName)
                    self.userStore.set_value(iter, 3, gecos)
                    self.userStore.set_value(iter, 4, shell)
                    self.userStore.set_value(iter, 5, homeDir)
                    self.userStore.set_value(iter, 6, userEnt)
            else:
                #display users with UIDs > 499
                if long (uidNumber) > -1L:
                    iter = self.userStore.append()
                    self.userStore.set_value(iter, 0, uid)
                    self.userStore.set_value(iter, 1, uidNumber)
                    self.userStore.set_value(iter, 2, groupName)
                    self.userStore.set_value(iter, 3, gecos)
                    self.userStore.set_value(iter, 4, shell)
                    self.userStore.set_value(iter, 5, homeDir)
                    self.userStore.set_value(iter, 6, userEnt)

    def populate_group_list(self):
        self.groupStore.clear()
        members = []

        for group in self.group_dict.keys():
            groupEnt = self.group_dict[group]

            if groupEnt.get(libuser.GIDNUMBER) != []:
                cn = groupEnt.get(libuser.GROUPNAME)[0]
                gid = groupEnt.get(libuser.GIDNUMBER)[0]
                members = self.member_dict[group]
                if not members:
                    members = []

                #concatenate the list of members in the group into a comma separated list
                memberlist = string.join(members, ", ")

                if self.preferences['FILTER'] == True:
                    #display groups with UIDs > 499
                    if long (gid) > 499 and not (cn == "nfsnobody" and (long (gid) == 65534L or long (gid) == 4294967294L)):
                        iter = self.groupStore.append()
                        self.groupStore.set_value(iter, 0, cn)
                        self.groupStore.set_value(iter, 1, gid)
                        self.groupStore.set_value(iter, 2, memberlist)
                        self.groupStore.set_value(iter, 3, groupEnt)
                else:
                    #display groups with UIDs > 499
                    if long (gid) > -1:
                        iter = self.groupStore.append()
                        self.groupStore.set_value(iter, 0, cn)
                        self.groupStore.set_value(iter, 1, gid)
                        self.groupStore.set_value(iter, 2, memberlist)
                        self.groupStore.set_value(iter, 3, groupEnt)
                
    def populate_lists(self):
        self.populate_user_list()
        self.populate_group_list()
        pass

    #------------Event handlers-------------#
    #---------------------------------------#

    #--------Event handlers for toplevel window-----#
    def on_about_button_clicked(self, *args):
        copyright_by = [ [ "2001 - 2007", "Red Hat, Inc." ],
                         [ "2001 - 2004", "Brent Fox", "bfox@redhat.com" ] ]
        authors = [ [ "Brent Fox", "bfox@redhat.com" ],
                    [ "Nils Philippsen", "nils@redhat.com" ] ]

        aboutDialog = xml.get_widget ("aboutDialog")
        aboutDialog.set_program_name (_("system-config-users"))
        aboutDialog.set_version ("")
        aboutDialog.set_logo_icon_name (iconName)

        cb_strings = []
        for cb in copyright_by:
            years = cb[0]
            holder = cb[1]
            try:
                email = cb[2]
                cb_strings.append (_("Copyright © %(years)s %(holder)s <%(email)s>") % {'years': years, 'holder': holder, 'email': email})
            except IndexError:
                cb_strings.append (_("Copyright © %(years)s %(holder)s") % {'years': years, 'holder': holder})
        aboutDialog.set_copyright ('\n'.join (cb_strings))

        au_strings = []
        for au in authors:
            author = au[0]
            try:
                email = au[1]
                au_strings.append (_("%(author)s <%(email)s>") % {'author': author, 'email': email})
            except IndexError:
                au_strings.append (_("%(author)s") % {'author': author})
        aboutDialog.set_authors (au_strings)

        aboutDialog.set_website ('http://fedoraproject.org/wiki/SystemConfig/users')

        aboutDialog.run ()
        aboutDialog.hide ()

    def on_help_button_clicked(self, *args):
        help_pages = ['ghelp:system-config-users#s2-system-config-users-user-new',
                      'ghelp:system-config-users#s2-system-config-users-group-new']
        page = help_pages [self.notebook.get_current_page ()]
        help_display (page)

    def on_manual_button_clicked(self, *args):
        page = 'ghelp:system-config-users'
        help_display (page)

    def on_exit1_activate(self, *args):
        if gtk.__dict__.has_key ("main_quit"):
            gtk.main_quit()
        else:
            gtk.mainquit()

    def on_add_user_activate(self, *args):
        filter = self.get_filter_data()
        self.userWin.newUserWin(filter)
        self.userWin.userWin.set_transient_for(self.toplevel)

    def on_add_group_activate(self, *args):
        self.groupWin.newGroupWin()
        self.groupWin.groupWin.set_transient_for(self.toplevel)

    def on_delete_activate(self, *args):
        page = self.notebook.get_current_page()
        if page == 0:
            if self.userTreeView.get_selection().get_selected():
                data, iter = self.userTreeView.get_selection().get_selected()
                userEnt = self.userStore.get_value(iter, 6)

                user = userEnt.get(libuser.USERNAME)[0]
                uid = userEnt.get(libuser.UIDNUMBER)[0]
                homeDir = userEnt.get(libuser.HOMEDIRECTORY)[0]                    
                mailSpool = "/var/spool/mail/%s" % (user)

                errMsgs = []

                if uid == 0:
                    dlg = gtk.MessageDialog (None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, _("Deleting the root user is not allowed."))
                    dlg.set_position(gtk.WIN_POS_CENTER)
                    dlg.set_modal (True)
                    dlg.set_icon_name (iconName)
                    dlg.run ()
                    dlg.destroy ()
                    return
                ts = rpm.TransactionSet ()
                if ts.dbMatch ("basenames", homeDir).count () > 0 or ts.dbMatch ("basenames", os.path.abspath (homeDir)).count () > 0 or ts.dbMatch ("basenames", os.path.realpath (homeDir)).count () > 0:
                    errMsgs.append (_("- An installed software package contains this directory."))
                if uid < 500 or (user == "nfsnobody" and (long (uid) == 65534L or long (uid) == 4294967294L)):
                    errMsgs.append (_("- A system user owns this directory and removing it may impair the system's integrity."))
                if not os.access(homeDir, os.W_OK):
                    errMsgs.append (_("- This directory doesn't exist or isn't writable."))
                elif os.lstat (homeDir).st_uid != uid:
                    errMsgs.append (_("- The user '%s' doesn't own this directory.") % (user))
                
                pipe = os.popen ("/usr/bin/pgrep -fl -U %d; /usr/bin/pgrep -u %d" % (uid, uid))
                processes = pipe.readlines ()
                pipe.close ()
                processes_running_text = ""
                if len (processes) > 0:
                    processes_running_text = _("<b>There are currently processes running that are owned by '%s'!</b>  This user is probably still logged in.  ") % (user)
                
                text = _("Do you really want to remove the user '%s'?") % (user)
                
                dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO)
                dlg.set_markup(processes_running_text + text)
                dlg.set_position(gtk.WIN_POS_CENTER)
                dlg.set_modal(True)
                dlg.set_icon_name(iconName)
                filesDeleteCheckButton = None
                if len (errMsgs) == 0:
                    filesDeleteText = _("Delete %(user)s's home directory ('%(homedir)s') and temporary files.") % {'user': user, 'homedir': homeDir}
                    if os.access (mailSpool, os.W_OK) and os.lstat (mailSpool).st_uid == uid:
                        filesDeleteText = _("Delete %(user)s's home directory ('%(homedir)s'), mail spool ('%(mailspool)s') and temporary files.") % {'user': user, 'homedir': homeDir, 'mailspool': mailSpool}
                    filesDeleteCheckButton = gtk.CheckButton (filesDeleteText)
                    filesDeleteCheckButton.set_active(True)
                    filesDeleteCheckButton.set_border_width(5)
                    filesDeleteCheckButton.get_child().set_line_wrap (True)
                    dlg.vbox.pack_start(filesDeleteCheckButton)
                else:
                    l_txt = (gettext.ngettext (N_("I won't delete %(user)s's home directory ('%(homedir)s') for this reason:\n%(reason)s"),
                                       N_("I won't delete %(user)s's home directory ('%(homedir)s') for these reasons:\n%(reason)s"),
                                       len (errMsgs)) % {'user': user, 'homedir': homeDir, 'reason': string.join (errMsgs, "\n")})
                    errLabel = gtk.Label (l_txt)
                    errLabel.set_line_wrap (True)
                    dlg.vbox.pack_start (errLabel)
                dlg.show_all()
                                                                                
                rc = dlg.run()

                if rc != gtk.RESPONSE_YES:
                    #bail out
                    dlg.destroy()
                    return
                else:
                    #Ok, we're going to delete the user
                    if filesDeleteCheckButton and filesDeleteCheckButton.get_active() == 1:
                        #Let's delete the home directory too
                        self.rmrf(homeDir)
                        if os.access (mailSpool, os.W_OK) and os.lstat (mailSpool).st_uid == uid:
                            self.rmrf(mailSpool)
                        self.rmtmpfiles (("/tmp", "/var/tmp"), uid)
                    self.ADMIN.deleteUser(userEnt)
                    dlg.destroy()
                                                                                
                try:
                    del self.user_dict[user]
                except:
                    pass

                need_refresh = [user]
                for group in self.group_dict.keys():
                    groupEnt = self.group_dict[group]
                    members = groupEnt.get(libuser.MEMBERNAME)

                    if members:
                        if user in members:
                            members.remove(user)
                            groupEnt.set(libuser.MEMBERNAME, members)
                            self.ADMIN.modifyGroup(groupEnt)

                    self.userSelectedRow = None

                #Let's check out the user's primary group
                groupEnt = self.ADMIN.lookupGroupById(userEnt.get(libuser.GIDNUMBER)[0])
                if groupEnt != None and len(groupEnt.get(libuser.MEMBERNAME)) == 0:
                    #Get the user's primary group.  If there's no one besides that user in the group,
                    #delete it.

                    if groupEnt.get(libuser.GIDNUMBER)[0] > 500:
                        #Only delete the group if it is a non-system group
                        self.ADMIN.deleteGroup(groupEnt)
                        try:
                            del self.group_dict[group]
                        except:
                            pass
                    
                self.refresh_users_and_groups(need_refresh)

        elif page == 1:
            if self.groupTreeView.get_selection().get_selected():
                data, iter = self.groupTreeView.get_selection().get_selected()
                groupEnt = self.groupStore.get_value(iter, 3)
                groupName = groupEnt.get(libuser.GROUPNAME)[0]

                #Let's check and see if we are deleting a user's primary group.  We don't want that to happen
                members = self.ADMIN.enumerateUsersByGroup(groupName)
                for userName in members:
                    userEnt = self.ADMIN.lookupUserByName(userName)
                    if userEnt.get(libuser.GIDNUMBER)[0] == groupEnt.get(libuser.GIDNUMBER)[0]:
                        messageDialog.show_message_dialog(_("You cannot remove user '%s' from their primary "
                                                   "group.") % userName)
                        return
                    
                rc = messageDialog.show_confirm_dialog(_("Are you sure you want to delete the group '%s'?")
                                                         % groupName)
                if rc != gtk.RESPONSE_YES:
                    return
                        
                self.ADMIN.deleteGroup(groupEnt)
                try:
                    del self.group_dict[groupName]
                except:
                    pass
                self.refresh_users_and_groups(groupName)

    def on_properties_activate(self, *args):        
        page = self.notebook.get_current_page()
        if page == 0:
            self.user_properties()
        elif page == 1:
            self.group_properties()

    def on_preferences_activate (self, *args):
        self.prefWindow.show ()

    def user_properties(self):
        if self.userTreeView.get_selection().get_selected():
            data, iter = self.userTreeView.get_selection().get_selected()
        
            userEnt = self.userStore.get_value(iter, 6)
            self.userProperties.showUserProperties(userEnt)
            self.userProperties.userWin.set_transient_for(self.toplevel)

    def group_properties(self):
        if self.groupTreeView.get_selection().get_selected():
            data, iter = self.groupTreeView.get_selection().get_selected()
            groupEnt = self.groupStore.get_value(iter, 3)
            self.groupProperties.showGroupProperties(groupEnt)
            self.groupProperties.groupWin.set_transient_for(self.toplevel)

    def itemSelected(self, *args):
        # When an item is selected, sensitize the properties and the delete buttons.
        # When an item is unselected, desensitize the properties and delete buttons.
        page = self.notebook.get_current_page()

        if page == 0:
            object, data = self.userTreeView.get_selection().get_selected()
        elif page == 1:
            object, data = self.groupTreeView.get_selection().get_selected()

        if data == None:
            self.toggleWidgets(False)
        else:
            self.toggleWidgets(True)

    def changeNotebookPage(self, *args):
        # When the user changes a notebook page, unselect all the choices on both the user and group lists
        # This keeps the program from getting confused on which widget is currently selected
        page = self.notebook.get_current_page()

        if page == 0:
            self.groupTreeView.get_selection().unselect_all()
        elif page == 1:
            self.userTreeView.get_selection().unselect_all()

        self.toggleWidgets(False)
        
    def toggleWidgets(self, value):
        self.properties_button.set_sensitive(value)
        self.properties_menu.set_sensitive(value)
        self.delete_button.set_sensitive(value)
        self.delete_menu.set_sensitive(value)
        
    def get_filter_data(self):
        filter = self.filter.get_text()
        filter = string.strip(filter)

        if len(filter) == 0:
            filter = ''
        else:
            index = string.find(filter, '*')
            length = len(filter) - 1

            if index != length:
                filter = filter + "*"
        return filter

    def on_filterSystemUsersGroupsCheckButton_toggled (self, *args):
        if self.filterSystemUsersGroupsCheckButton.get_active () == True:
            self.preferences['FILTER'] = True
        else:
            self.preferences['FILTER'] = False
        self.populate_lists()

    def on_assignHighestUidCheckButton_toggled (self, *args):
        if self.assignHighestUidCheckButton.get_active () == True:
            self.preferences['ASSIGN_HIGHEST_UID'] = True
        else:
            self.preferences['ASSIGN_HIGHEST_UID'] = False

    def on_assignHighestGidCheckButton_toggled (self, *args):
        if self.assignHighestGidCheckButton.get_active () == True:
            self.preferences['ASSIGN_HIGHEST_GID'] = True
        else:
            self.preferences['ASSIGN_HIGHEST_GID'] = False

    def on_preferSameUIDGIDCheckButton_toggled (self, *args):
        if self.preferSameUIDGIDCheckButton.get_active () == True:
            self.preferences['PREFER_SAME_UID_GID'] = True
        else:
            self.preferences['PREFER_SAME_UID_GID'] = False
            
    def rmrf(self, path):
        # only allow absolute paths to be deleted
        if not os.path.isabs(path):
            raise RuntimeError("rmrf(): path must be absolute")

        path = os.path.abspath (path)
        pathcomps = path.split (os.path.sep)

        # Don't allow the system root or anything beneath /dev to be deleted
        if path != os.path.sep and len (pathcomps) >= 2 and pathcomps[1] != "dev" \
                and os.path.lexists (path):
            try:
                os.remove (path)
            except OSError:
                # possibly a directory
                shutil.rmtree (path)
            except:
                raise

    def do_rm_userowned (self, path, uid):
        if os.path.isdir (path) and not os.path.islink (path):
            for file in os.listdir (path):
                self.do_rm_userowned (os.path.join(path, file), uid)
            if os.lstat (path).st_uid == uid:
                try:
                    os.rmdir (path)
                except OSError:
                    pass
        else:
            if os.lstat (path).st_uid == uid:
                try:
                    os.unlink (path)
                except OSError:
                    pass

    def rmtmpfiles (self, tmppaths, uid):
        for path in tmppaths:
            self.do_rm_userowned (path, uid)
        
    def rowActivated(self, *args):
        self.on_properties_activate()

    def isSELinuxInstalled(self):
        ts = rpm.TransactionSet()

        mi = ts.dbMatch('name', 'policy-sources')
        if mi.count() > 0:
            return True
        return False

    def isSELinuxEnabled(self):
        if self.isSELinuxInstalled():
            if os.system("/usr/bin/selinuxenabled") > 0:
                #it's enabled, return True
                return True
            else:
                #it's installed, but not enabled
                return False
        else:
            #not installed
            return False
