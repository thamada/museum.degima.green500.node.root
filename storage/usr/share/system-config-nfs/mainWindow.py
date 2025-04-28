# -*- coding: utf-8 -*-

## mainWindow.py - Contains the UI code needed for system-config-nfs
## Copyright (C) 2002 - 2009 Red Hat, Inc.
## Copyright (C) 2002, 2003 Brent Fox <bfox@redhat.com>
## Copyright (C) 2005 Nils Philippsen <nils@redhat.com>

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

## Authors:
## Brent Fox <bfox@redhat.com>
## Nils Philippsen <nils@redhat.com>

import nfsServer
import gtk
import gtk.glade
import gobject
import string
import os
import sys

import propertiesWindow

##
## Icon for windows
##

iconPixbuf = None      
try:
    iconPixbuf = gtk.gdk.pixbuf_new_from_file("/usr/share/system-config-nfs/pixmaps/system-config-nfs.png")
except:
    pass

class mainWindow:
    SHARE_PATH = 0
    SHARE_CLIENT = 1
    SHARE_PERM = 2
    SHARE_SHARE_OBJ = 3
    SHARE_CLIENT_OBJ = 4

    entries_varnames = {
            'lockdTcpPortEntry': 'LOCKD_TCPPORT',
            'lockdUdpPortEntry': 'LOCKD_UDPPORT',
            'mountdPortEntry': 'MOUNTD_PORT',
            'statdPortEntry': 'STATD_PORT',
            'rquotadPortEntry': 'RQUOTAD_PORT'
            }

    def destroy(self, *args):
        if gtk.__dict__.has_key ('main_quit'):
            gtk.main_quit ()
        else:
            gtk.mainquit()
        return True
    
    def __init__(self):
        domain = "system-config-nfs"
        if os.access ("system-config-nfs.glade", os.F_OK):
            self.xml = gtk.glade.XML ("system-config-nfs.glade", domain=domain)
        else:
            self.xml = gtk.glade.XML ("/usr/share/system-config-nfs/system-config-nfs.glade", domain=domain)

        self.mainWindow = self.xml.get_widget ('mainWindow')

        self.mainWindow.set_icon(iconPixbuf)
        self.mainWindow.set_position(gtk.WIN_POS_CENTER)
        self.xml.signal_connect ('on_mainWindow_delete_event', self.destroy)

        # [0 dir, 1 hosts, 2 read/write text, 3 nfsDataObject]

        self.exportsStore = gtk.ListStore(gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_PYOBJECT,
                gobject.TYPE_PYOBJECT)

        self.exportsView = self.xml.get_widget ("exportsView")
        self.exportsView.set_model (self.exportsStore)
        self.exportsView.connect ("row-activated", self.on_propertiesButton_clicked)
        #self.exportsView.columns_autosize()

        self.col = gtk.TreeViewColumn(_("Directory"), gtk.CellRendererText(), text=self.SHARE_PATH)
#        self.col.set_spacing(235)
        self.exportsView.append_column(self.col)
        self.col = gtk.TreeViewColumn(_("Hosts"), gtk.CellRendererText(), text=self.SHARE_CLIENT)
        self.col.set_spacing(235)
        self.exportsView.append_column(self.col)
        self.col = gtk.TreeViewColumn(_("Permissions"), gtk.CellRendererText(), text=self.SHARE_PERM)
        self.exportsView.append_column(self.col)

        self.menuBar = self.xml.get_widget ('menuBar')
        self.xml.signal_connect ("on_addShareMenu_activate", self.on_addButton_clicked)
        self.xml.signal_connect ("on_propertiesMenu_activate", self.on_propertiesButton_clicked)
        self.xml.signal_connect ("on_deleteMenu_activate", self.on_deleteButton_clicked)
        self.xml.signal_connect ("on_quitMenu_activate", self.destroy)
        self.xml.signal_connect ("on_serverSettingsMenu_activate", self.on_serverSettingsButton_clicked)
        self.xml.signal_connect ("on_helpMenu_activate", self.on_helpButton_clicked)
        self.xml.signal_connect ("on_aboutMenu_activate", self.on_aboutButton_clicked)

        self.propertiesMenu = self.xml.get_widget ("propertiesMenu")
        self.deleteMenu = self.xml.get_widget ("deleteMenu")

        self.toolbar = self.xml.get_widget ('toolBar')

        self.addButton = self.xml.get_widget ('addButton')
        self.xml.signal_connect ('on_addButton_clicked', self.on_addButton_clicked)
        self.propertiesButton = self.xml.get_widget ("propertiesButton")
        self.xml.signal_connect ('on_propertiesButton_clicked', self.on_propertiesButton_clicked)
        
        self.deleteButton = self.xml.get_widget ("deleteButton")
        self.xml.signal_connect ('on_deleteButton_clicked', self.on_deleteButton_clicked)

        self.serverSettingsButton = self.xml.get_widget ("serverSettingsButton")
        self.xml.signal_connect ('on_serverSettingsButton_clicked', self.on_serverSettingsButton_clicked)

        self.helpButton = self.xml.get_widget ("helpButton")
        self.xml.signal_connect ('on_helpButton_clicked', self.on_helpButton_clicked)

        self.xml.signal_connect ('on_serverSettings_changed', self.on_serverSettings_changed)

        self.propertiesMenu.set_sensitive(False)
        self.deleteMenu.set_sensitive(False)
        self.propertiesButton.set_sensitive(False)
        self.deleteButton.set_sensitive(False)

        self.server = nfsServer.nfsServer ()
        self.exports = self.server.exports
        self.exports.consolidateShares ()
        self.populateExportsList()

        if len (self.exports.warnings):
            dlg = self.xml.get_widget ('warningDialog')
            textview = self.xml.get_widget ('warningTextView')
            textbuffer = textview.get_buffer ()
            lines = '\n'.join (map (lambda x: "line %d: %s" % (x[0], x[1]), self.exports.warnings))
            textbuffer.set_text (lines)
            if dlg.run () == gtk.RESPONSE_CANCEL:
                sys.exit ()
            dlg.destroy ()

        self.propWindow = propertiesWindow.propertiesWindow(self, self.exports, self.exportsStore, self.exportsView)
        self.serverSettingsWindow = self.xml.get_widget ("serverSettingsDialog")
        for entry in self.entries_varnames.keys ():
            setattr (self, entry, self.xml.get_widget (entry))
        self.serverSettingsOKButton = self.xml.get_widget ('serverSettingsOKButton')

        #self.mainWindow.set_size_request(600, 500)

        self.selectedRow = -1
        self.changed = False
        
        self.createHandler = None
        self.modifyHandler = None

#        self.exportsList.columns_autosize()
        self.mainWindow.show_all()

        self.exportsView.get_selection().connect("changed", self.on_exportsList_select_row)
        self.exportsView.get_selection().unselect_all()

#        self.exportsList.sort()
        if gtk.__dict__.has_key ('main'):
            gtk.main ()
        else:
            gtk.mainloop()

    def populateExportsList(self):
        shares = self.exports.getShares ()
        for share in shares:
            for client in share.clients:
                #Iterate through the entries and populate the exportsStore
                iter = self.exportsStore.append()
                self.exportsStore.set_value(iter, self.SHARE_PATH, share.path)
                self.exportsStore.set_value(iter, self.SHARE_CLIENT, client.client)
                if client.get ('ro'):
                    self.exportsStore.set_value(iter, self.SHARE_PERM, (_("Read")))
                else:
                    self.exportsStore.set_value(iter, self.SHARE_PERM, (_("Read/Write")))
                self.exportsStore.set_value (iter, self.SHARE_SHARE_OBJ, share)
                self.exportsStore.set_value (iter, self.SHARE_CLIENT_OBJ, [client])

    #--------Event handlers for mainWindow-----#
    def on_helpButton_clicked(self, *args):
        help_page = "ghelp:system-config-nfs"
        paths = ["/usr/bin/yelp", None]

        for path in paths:
            if path and os.access (path, os.X_OK):
                break
        
        if path == None:
            dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK,
                                    (_("The help viewer could not be found. To be able to view help you need to install the 'yelp' package.")))
            dlg.set_position(gtk.WIN_POS_CENTER)
            dlg.run()
            dlg.destroy()
            return
		
        pid = os.fork()
        if not pid:
            os.execv(path, [path, help_page])

    def on_exportsList_select_row(self, *args):
        store, iter = self.exportsView.get_selection().get_selected()
        if iter:
            self.propertiesButton.set_sensitive(True)
            self.deleteButton.set_sensitive(True)
            self.propertiesMenu.set_sensitive(True)
            self.deleteMenu.set_sensitive(True)
        else:
            self.propertiesButton.set_sensitive(False)
            self.deleteButton.set_sensitive(False)
            self.propertiesMenu.set_sensitive(False)
            self.deleteMenu.set_sensitive(False)

    def on_addButton_clicked(self, *args):
        self.propWindow.new_share (_("Add NFS Share"))
        self.desensitizeWidgets ()

    def on_propertiesButton_clicked(self, *args):
        store, iter = self.exportsView.get_selection().get_selected()
        if iter != None:
            self.propWindow.edit_share(_("Edit NFS Share"), iter)
        self.desensitizeWidgets()
        
    def on_deleteButton_clicked(self, *args):
        self.changed = True
        store, iter = self.exportsView.get_selection().get_selected()

        if iter != None:
            share = self.exportsStore.get_value (iter, self.SHARE_SHARE_OBJ)
            clients = self.exportsStore.get_value (iter, self.SHARE_CLIENT_OBJ)
            self.exports.remove (share, clients)
            self.exportsStore.remove(iter)
        self.desensitizeWidgets()
        self.apply_changes()

    def on_serverSettingsButton_clicked (self, *args):
        self.serverSettingsWindow_populate ()
        self.serverSettingsWindow.set_transient_for (self.mainWindow)
        result = self.serverSettingsWindow.run ()
        if result == gtk.RESPONSE_OK:
            self.serverSettingsWindow_getvars ()
            self.apply_changes ()
        self.serverSettingsWindow.hide ()

    def on_serverSettings_changed (self, *args):
        valid = True
        for entry in self.entries_varnames.keys ():
            value = getattr (self, entry).get_text ()
            if value != '':
                try:
                    value = int (value)
                    if value < 1 or value > 65536:
                        raise ValueError ()
                except ValueError:
                    valid = False
                    break
        self.serverSettingsOKButton.set_sensitive (valid)

    def serverSettingsWindow_populate (self):
        for entry, varname in self.entries_varnames.iteritems ():
            value = self.server.settings.get (varname)
            if value:
                getattr (self, entry).set_text (value)
        self.on_serverSettings_changed ()

    def serverSettingsWindow_getvars (self):
        for entry, varname in  self.entries_varnames.iteritems ():
            value = getattr (self, entry).get_text ()
            if value != '':
                self.server.settings.set (varname, value)
            else:
                self.server.settings.unset (varname)

    def apply_changes(self, *args):
        self.changed = False

        self.exports.writeFile ()
        self.server.settings.write ()
        self.server.startNfs ()
        self.server.exportFs ()

    def desensitizeWidgets(self, *args):
        self.exportsView.get_selection().unselect_all()
        self.propertiesButton.set_sensitive(False)
        self.deleteButton.set_sensitive(False)
        self.propertiesMenu.set_sensitive(False)
        self.deleteMenu.set_sensitive(False)        

    def on_aboutButton_clicked(self, *args):
        if not self.__dict__.has_key ('aboutDialog'):
            self.aboutDialogPrepare ()
        self.aboutDialog.set_transient_for (self.mainWindow)
        self.aboutDialog.show ()
        self.aboutDialogShown = True

    def on_aboutDialog_close (self, *args):
        self.aboutDialog.hide ()
        self.aboutDialogShown = False
        return True

    def aboutDialogPrepare (self):
        holders = [
            # year(s), holder, optional email
            [ "2002-2008", "Red Hat, Inc." ],
            [ "2002-2004", "Brent Fox", "bfox@redhat.com" ],
            [ "2002-2003", "Tammy Fox", "tfox@redhat.com" ],
            [ "2004-2006", "Nils Philippsen", "nphilipp@redhat.com" ]
        ]
        holders_strings = []
        for holderinfo in holders:
            (year, holder) = holderinfo[0:2]
            try:
                email = holderinfo[2]
                holders_strings.append (_('Copyright (c) %s %s <%s>') % (year, holder, email))
            except IndexError:
                holders_strings.append (_('Copyright (c) %s %s') % (year, holder))

        holders_label_string = "\n".join (holders_strings)
        label = self.xml.get_widget ('copyrightHolderLabel')
        label.set_text (holders_label_string)

        self.aboutDialog = self.xml.get_widget ('aboutDialog')
        self.aboutDialog.set_icon(iconPixbuf)
        self.xml.signal_connect ('on_aboutDialog_delete_event', self.on_aboutDialog_close)
        self.xml.signal_connect ('on_aboutDialogCloseButton_clicked', self.on_aboutDialog_close)
        self.aboutDialogShown = False
