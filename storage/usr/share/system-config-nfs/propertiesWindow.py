## propertiesWindow.py - Contains the UI for the system-config-nfs share properties window
## Copyright (C) 2002 - 2007 Red Hat, Inc.
## Copyright (C) 2002, 2003 Brent Fox <bfox@redhat.com>

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

import gtk
import gobject
import mainWindow
import nfsExports
import string
import os

class propertiesWindow:
       
    def __init__(self, parent, exports, store, view):
        self.parent = parent
        self.xml = parent.xml
        self.exports = exports
        self.exportsStore = store
        self.exportsView = view
        self.bb = None

        self.notebook = self.xml.get_widget ('shareDialogNotebook')

        self.dirEntry = self.xml.get_widget ('dirEntry')
        self.hostEntry = self.xml.get_widget ('hostEntry')
        self.readRadio = self.xml.get_widget ('readRadio')
        self.writeRadio = self.xml.get_widget ('writeRadio')
    
        self.inSecureCheckButton = self.xml.get_widget ('inSecureCheckButton')
        self.insecureLockCheckButton = self.xml.get_widget ('insecureLockCheckButton')
        self.subtreeCheckButton = self.xml.get_widget ('subtreeCheckButton')
        self.syncCheckButton = self.xml.get_widget ('syncCheckButton')
        self.forceSyncCheckButton = self.xml.get_widget ('forceSyncCheckButton')

        self.hideCheckButton = self.xml.get_widget ('hideCheckButton')
        self.mpCheckButton = self.xml.get_widget ('mpCheckButton')
        self.xml.signal_connect ('on_mpCheckButton_toggled', self.on_mpCheckButton_toggled)
        self.mpEntry = self.xml.get_widget ('mpEntry')
        self.mpBrowseButton = self.xml.get_widget ('mpBrowseButton')
        self.xml.signal_connect ('on_mpBrowseButton_clicked', self.on_mpBrowseButton_clicked)
        self.fsidEntry = self.xml.get_widget ('fsidEntry')

        self.noRootSquashCheckButton = self.xml.get_widget ('noRootSquashCheckButton')
        self.userSquashCheckButton = self.xml.get_widget ('userSquashCheckButton')
        self.uidEntry = self.xml.get_widget ('uidEntry')
        self.gidEntry = self.xml.get_widget ('gidEntry')
 
        self.dialog = self.xml.get_widget ('shareDialog')
        self.xml.signal_connect ("on_shareDialog_delete_event", self.on_cancelButton_clicked)
        self.dialog.set_icon(mainWindow.iconPixbuf)
        self.dialog.set_transient_for (parent.mainWindow)

        self.okButton = self.xml.get_widget ('shareDialogOkButton')
        self.cancelButton = self.xml.get_widget ('shareDialogCancelButton')
        self.xml.signal_connect('on_shareDialogCancelButton_clicked', self.on_cancelButton_clicked)

        # basic page
        self.browseButton = self.xml.get_widget ('browseButton')
        self.xml.signal_connect ('on_browseButton_clicked', self.on_browseButton_clicked)
        # general options page
        self.xml.signal_connect ("on_syncCheckButton_toggled", self.on_syncCheckButton_toggled)
        self.forceSyncCheckButton.set_sensitive(False)
        # user page
        self.xml.signal_connect ('on_noRootSquashCheckButton_toggled', self.on_noRootSquashCheckButton_toggled)
        self.xml.signal_connect ('on_userSquashCheckButton_toggled', self.on_userSquashCheckButton_toggled)

        self.toggle_box(False)
        self.on_mpCheckButton_toggled ()
        self.reset()

    def on_cancelButton_clicked(self, *args):
        self.reset()
        return True

    def on_browseButton_clicked(self, *args):
        dlg = gtk.FileChooserDialog (title = _("Select a directory"),
                parent = self.dialog,
                action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                    gtk.STOCK_OK, gtk.RESPONSE_OK))
        filename = self.dirEntry.get_text ()
        if filename.strip () != "":
            dlg.set_filename (filename)
        
        result = dlg.run()
        
        if result == gtk.RESPONSE_OK:
            filename = dlg.get_filename()
            self.dirEntry.set_text(dlg.get_filename())

        dlg.destroy()

    def on_noRootSquashCheckButton_toggled(self, *args):
        state = self.noRootSquashCheckButton.get_active()
        self.userSquashCheckButton.set_sensitive(not state)

    def toggle_box(self, state):
        self.uidEntry.set_sensitive(state)
        self.gidEntry.set_sensitive(state)

    def on_userSquashCheckButton_toggled(self, *args):
        if self.userSquashCheckButton.get_active() == False:
            self.toggle_box(False)
            self.noRootSquashCheckButton.set_sensitive(True)
        else:
            state = self.userSquashCheckButton.get_active()
            self.noRootSquashCheckButton.set_sensitive(not state)
            self.uidEntry.set_sensitive(state)
            self.gidEntry.set_sensitive(state)

    def on_syncCheckButton_toggled(self, *args):
        self.forceSyncCheckButton.set_sensitive(self.syncCheckButton.get_active())

    def on_mpCheckButton_toggled (self, *args):
        self.mpEntry.set_sensitive (self.mpCheckButton.get_active ())
        self.mpBrowseButton.set_sensitive (self.mpCheckButton.get_active ())

    def on_mpBrowseButton_clicked (self, *args):
        dlg = gtk.FileChooserDialog (parent = self.dialog,
                action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                        gtk.STOCK_OK, gtk.RESPONSE_OK))

        mp = self.mpEntry.get_text ()
        if len (mp) and os.path.isdir (mp):
            dlg.set_filename (mp)
        else:
            mp = self.dirEntry.get_text ()
            if len (mp) and os.path.isdir (mp):
                dlg.set_filename (mp)
            else:
                dlg.set_filename ("/")

        if dlg.run () == gtk.RESPONSE_OK:
            self.mpEntry.set_text (dlg.get_filename ())

        dlg.destroy ()

    def new_share(self, title):
        #Make okButton connect to on_addButton_clicked
        self.okButtonHandler = self.okButton.connect('clicked', self.on_addButton_clicked)
        self.show_win(title)
        
    def edit_share(self, title, iter):
        #Make okButton connect to on_editButton_clicked
        self.okButtonHandler = self.okButton.connect('clicked', self.on_editButton_clicked, iter)
        self.show_win(title, iter)

    def check_dir_hosts (self, dir, hoststring, check_duplicate):
        if dir == "" or hoststring == "":
            dlg = gtk.MessageDialog (self.dialog, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     (_("You must specify a directory and a host")))
            dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
            dlg.set_icon (mainWindow.iconPixbuf)
            dlg.set_modal (True)
            dlg.set_transient_for (self.dialog)
            dlg.run ()
            dlg.destroy ()
            return False

        #Check and see if the filename is a valid directory
        try:
            os.listdir(dir)
        except:
            warn = gtk.MessageDialog (self.dialog, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                      (_("%s is not a valid directory." % dir)))
            warn.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
            warn.set_icon (mainWindow.iconPixbuf)
            warn.set_modal (True)
            warn.set_transient_for (self.dialog)
            warn.run ()
            warn.destroy ()                
            return False

        # avoid duplicate clients for a share
        hosttokens = string.split (hoststring)
        #print "hosttokens:", hosttokens
        try:
            share = self.exports.getShares (dir)[0]
        except IndexError:
            share = None

        foundhosts = []
        for curhost in hosttokens:
            if curhost in foundhosts:
                # avoid duplication of hosts in error message
                continue
            if check_duplicate and share and curhost in map (lambda y: y.client, share.clients):
                # share already is exported to curhost
                foundhosts.append (curhost)
            else:
                # check for duplicate hosts in entry
                found = 0
                for comphost in hosttokens:
                    if comphost == curhost:
                        found += 1
                if found > 1:
                    foundhosts.append (curhost)

        if len (foundhosts):
            if len (foundhosts) == 1:
                host = foundhosts[0]
                if host == '*':
                    warnstring = _("Share '%s' must only be exported once to all clients.") % (dir)
                elif host.find ('*') >= 0 or host.find ('?') >= 0:
                    warnstring = _("Share '%s' must only be exported once to clients '%s'.") % (dir, host)
                else:
                    warnstring = _("Share '%s' must only be exported once to client '%s'.") % (dir, foundhosts[0])
            else:
                # "'host1', 'host2'" ..,
                firsthosts = ', '.join (map (lambda x: "'%s'" % (x), foundhosts[:-1]))
                # "... and 'host3'"
                lasthost = "'%s'" % (foundhosts[-1])
                warnstring = _("Share '%s' must only be exported once to clients %s and %s.") % (dir, firsthosts, lasthost)
            warn = gtk.MessageDialog (self.dialog, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, warnstring)
            warn.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
            warn.set_icon(mainWindow.iconPixbuf)
            warn.set_modal(True)
            warn.set_transient_for(self.dialog)
            warn.run()
            warn.destroy()
            return False

        return True


    def on_editButton_clicked(self, widget, iter):
        dir = self.dirEntry.get_text()
        hoststring = self.hostEntry.get_text()

        if not self.check_dir_hosts (dir, hoststring, False):
            return
            
        self.process_options(iter, dir, hoststring)
        self.reset()
        self.parent.apply_changes()
        self.parent.changed = True

    def on_addButton_clicked(self, *args):
        curhost = ""

        dir = self.dirEntry.get_text()
        hoststring = self.hostEntry.get_text()

        if not self.check_dir_hosts (dir, hoststring, True):
            return

        hosttokens = string.split(hoststring)
        for curhost in hosttokens:
            iter = self.exportsStore.append()
            self.process_options(iter, dir, curhost)

        self.reset()
        self.parent.apply_changes()
        self.parent.changed = True

    def process_options(self, iter, dir, hosts_string):
        try:
            share = self.exports.getShares (dir)[0]
        except IndexError:
            share = None

        hosts = hosts_string.split ()

        if share:
            map (share.remove, filter (lambda x: x in hosts, map (lambda y: y.client, share.clients)))
        else:
            share = nfsExports.nfsShare ("% -25s      %s" % (dir, hosts_string))
            self.exports.lineobjs.append (share)

        self.exportsStore.set_value(iter, self.parent.SHARE_PATH, dir)
        self.exportsStore.set_value(iter, self.parent.SHARE_CLIENT, hosts_string)

        newclients = []
        for host in hosts:
            client = share.getClient (host)
            if not client:
                client = nfsExports.nfsClient (host)
                share.clients.append (client)
            newclients.append (client)

            if self.readRadio.get_active() == True:
                self.exportsStore.set_value(iter, self.parent.SHARE_PERM, _("Read"))
                client.set ("ro")
            else:
                self.exportsStore.set_value(iter, self.parent.SHARE_PERM, _("Read/Write"))
                client.set ("rw")

            if self.inSecureCheckButton.get_active() == True:
                client.set ("insecure")
            else:
                client.set ("secure")

            if self.syncCheckButton.get_active() == True:
                client.set ("sync")

                if self.forceSyncCheckButton.get_active() == True:
                    client.set ("no_wdelay")
                else:
                    client.set ("wdelay")

            else:
                client.set ("async")
                client.set ("wdelay")

            if self.subtreeCheckButton.get_active() == True:
                client.set ("no_subtree_check")
            else:
                client.set ("subtree_check")

            if self.insecureLockCheckButton.get_active() == True:
                client.set ("insecure_locks")
            else:
                client.set ("secure_locks")

            if self.hideCheckButton.get_active () == True:
                client.set ("hide")
            else:
                client.set ("nohide")

            if self.mpCheckButton.get_active () == True:
                if len (self.mpEntry.get_text ()) == 0:
                    client.set ("mp")
                else:
                    client.set ("mp=%s" % self.mpEntry.get_text ())
            else:
                client.set ("!mp")

            if len (self.fsidEntry.get_text ()):
                client.set ("fsid=%s" % self.fsidEntry.get_text ())
            else:
                client.set ("!fsid")

            if self.noRootSquashCheckButton.get_active() == True:
                client.set ("no_root_squash")

            elif self.userSquashCheckButton.get_active() == True:
                client.set ("all_squash")

                if len (self.uidEntry.get_text ()):
                    client.set ("anonuid=" + self.uidEntry.get_text())
                else:
                    client.set ("!anonuid")

                if len (self.gidEntry.get_text ()):
                    client.set ("anongid=" + self.gidEntry.get_text())
                else:
                    client.set ("!anongid")
            else:
                client.set ("root_squash")

        self.exportsStore.set_value(iter, self.parent.SHARE_SHARE_OBJ, share)
        self.exportsStore.set_value(iter, self.parent.SHARE_CLIENT_OBJ, newclients)

    def show_win(self, title, iter=None):
        self.dialog.set_title(title)
        self.syncCheckButton.set_active(True)

        if iter:
            self.dirEntry.set_text(self.exportsStore.get_value(iter, self.parent.SHARE_PATH))
            self.hostEntry.set_text(self.exportsStore.get_value(iter, self.parent.SHARE_CLIENT))

            share = self.exportsStore.get_value(iter, self.parent.SHARE_SHARE_OBJ)
            client = self.exportsStore.get_value(iter, self.parent.SHARE_CLIENT_OBJ)[0]

            if client.get ("ro"):
                self.readRadio.set_active(True)
            else:
                self.writeRadio.set_active(True)

            if  client.get ("insecure"):
                self.inSecureCheckButton.set_active(True)

            if client.get ("sync"):
                    self.syncCheckButton.set_active(True)
            else:
                    self.syncCheckButton.set_active(False)
                
            if client.get ("no_wdelay"):
                self.forceSyncCheckButton.set_active(True)

            if client.get ("no_subtree_check"):
                self.subtreeCheckButton.set_active(True)

            if client.get ("insecure_locks"):
                self.insecureLockCheckButton.set_active(True)

            if client.get ("hide"):
                self.hideCheckButton.set_active (True)
            else:
                self.hideCheckButton.set_active (False)

            mp = client.get ("mp")
            if mp != False:
                self.mpCheckButton.set_active (True)
                if isinstance (mp, str):
                    self.mpEntry.set_text (mp)
                else:
                    self.mpEntry.set_text ('')
            else:
                self.mpCheckButton.set_active (False)
                self.mpEntry.set_text ('')

            self.on_mpCheckButton_toggled ()

            fsid = client.get ("fsid")
            if fsid:
                self.fsidEntry.set_text (fsid)
            else:
                self.fsidEntry.set_text ('')

            if client.get ("squash") == "no_root_squash":
                self.noRootSquashCheckButton.set_active(True)

            elif client.get ("squash") == "all_squash":
                self.userSquashCheckButton.set_active(True)

                if client.get ('anonuid'):
                    self.uidEntry.set_text(client.get ('anonuid'))

                if client.get ('anongid'):
                    self.gidEntry.set_text(client.get ('anongid'))

        self.dialog.show_all()
        self.dirEntry.grab_focus()

    def reset(self):
        self.notebook.set_current_page(0)
        self.dirEntry.set_text("")
        self.hostEntry.set_text("")
        self.readRadio.set_active(True)

        self.inSecureCheckButton.set_active(False)
        self.insecureLockCheckButton.set_active(False)
        self.subtreeCheckButton.set_active(False)
        self.syncCheckButton.set_active(False)
        self.forceSyncCheckButton.set_active(False)
        self.hideCheckButton.set_active (True)
        self.mpCheckButton.set_active (False)
        self.mpEntry.set_text ("")
        self.fsidEntry.set_text ("")

        self.noRootSquashCheckButton.set_active(False)
        self.userSquashCheckButton.set_active(False)
        self.uidEntry.set_text("")
        self.gidEntry.set_text("")

        #Remove event handler from the button because it will
        #be reassigned when the window is launched again
        try:
            self.okButton.disconnect(self.okButtonHandler)
            self.dialog.hide()
        except AttributeError:
            pass

