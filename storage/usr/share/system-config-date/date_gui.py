# -*- coding: utf-8 -*-
#
# date_gui - Program creates a user interface
#            that allows the system time, system date,
#            time zone, and ntpd configuration to be easily set
#
# Copyright © 2002-2006, 2009, 2010 Red Hat, Inc.
# Copyright © 2001-2003 Brent Fox <bfox@redhat.com>
#                       Tammy Fox <tfox@redhat.com>
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Authors:
# Brent Fox <bfox@redhat.com>
# Tammy Fox <tfox@redhat.com>
# Nils Philippsen <nphilipp@redhat.com>

import gtk
import gtk.glade
import gobject
import time
import string
import scdMainWindow

from scdate.core.util import _

##
## compat
##
gobject.timeout_add = getattr (gobject, "timeout_add", gtk.timeout_add)
gobject.source_remove = getattr (gobject, "source_remove", gtk.timeout_remove)

class datePage(object):
    def __init__(self, dateBackend, xml):
        self.xml = xml
        self.mainWindow = self.xml.get_widget ("window")
        self.dateBackend = dateBackend

        self.modal_dialog = None

        self.flag = False
        times = scdMainWindow.dateBackend.getDate()

        # current date and time
        self.dateTimeLabel = self.xml.get_widget ("dateTimeLabel")
        self.updateDateTime ()
        gobject.timeout_add (1000, self.updateDateTime)

        self.ntpCheckButton = self.xml.get_widget ("ntp_check")
        self.ntpCheckButton.connect("clicked", self.ntpCheckButtonClicked)

        # hidden manual date and time/NTP notebook
        self.manualNtpNotebook = self.xml.get_widget ("manualNtpNotebook")
        self.manualNtpNotebook.set_show_tabs (False)

        # manual page
        self.date_frame = self.xml.get_widget ("date_frame")
        self.time_frame = self.xml.get_widget ("time_frame")

        # calendar to set date
        self.cal = self.xml.get_widget ("calendar")
        self.cal.select_month(times[1]-1, times[0])
        self.cal.select_day(times[2])

        # controls to set time
        self.hourEntry = self.xml.get_widget ("hour_entry")
        self.hourEntry.connect("changed", self.filter, 23)
        hourAdj = gtk.Adjustment(times[3], 0, 24, 1)
        self.hourEntry.set_adjustment(hourAdj)
        self.hourEntry.set_value(times[3])
        self.hourEntry.set_data ('last_value', times[3])

        self.minEntry = self.xml.get_widget ("min_entry")
        self.minEntry.connect("changed", self.filter, 59)
        minAdj = gtk.Adjustment(times[4], 0, 59, 1)
        self.minEntry.set_adjustment(minAdj)
        self.minEntry.set_value(times[4])
        self.minEntry.set_data ('last_value', times[4])

        self.secEntry = self.xml.get_widget ("sec_entry")
        self.secEntry.connect("changed", self.filter, 59)
        secAdj = gtk.Adjustment(times[5], 0, 60, 1)
        self.secEntry.set_adjustment(secAdj)
        self.secEntry.set_value(times[5])
        self.secEntry.set_data ('last_value', times[5])

        # NTP page
        self.ntpFrame = self.xml.get_widget ("ntp_frame")

        self.ntpLabel = self.xml.get_widget ("ntp_label")

        self.ntpAdvOptionsExpander = self.xml.get_widget ("ntp_adv_options_expander")
        self.ntpAdvOptionsExpanderLabel = self.xml.get_widget ("ntp_adv_options_expander_label")
        self.ntpIburstButton = self.xml.get_widget ("ntp_iburst")
        self.ntpLocalTimeSourceButton = self.xml.get_widget ("ntp_local_timesource_check")
        self.ntpBroadcastClientCheckButton = self.xml.get_widget ("ntp_broadcast_check")

        self.srv_frame = self.xml.get_widget ("srv_frame")

        self.ntpSrvButtonbox = self.xml.get_widget ("ntp_srv_buttonbox")
        self.ntpSrvAddButton = self.xml.get_widget ("ntp_srv_add_button")
        self.ntpSrvEditButton = self.xml.get_widget ("ntp_srv_edit_button")
        self.ntpSrvDelButton = self.xml.get_widget ("ntp_srv_del_button")

        self.NTPSERVER = 0

        self.added_row_reference = None

        self.ntpListStore = gtk.ListStore (gobject.TYPE_STRING, gobject.TYPE_BOOLEAN)
        self.ntpListStore.set_sort_func (self.NTPSERVER, self.list_sort)
        self.ntpListStore.set_sort_column_id (self.NTPSERVER, gtk.SORT_ASCENDING)
        self.ntpServersTreeView = self.xml.get_widget ("ntp_servers_view")
        self.ntpServersTreeView.set_model (self.ntpListStore)
        self.ntpServersTreeView.columns_autosize ()
        self.cellrend = gtk.CellRendererText ()
        self.cellrend.set_property ("editable", True)
        self.cellrend.connect ("edited", self.cell_edited)
        self.cellrend.connect ("editing-canceled", self.cell_editing_canceled)
        col = gtk.TreeViewColumn (_("Server"), self.cellrend, text = self.NTPSERVER)
        self.ntpServersTreeView.append_column (col)

        selection = self.ntpServersTreeView.get_selection ()
        selection.set_mode (gtk.SELECTION_MULTIPLE)
        selection.connect ("changed", self.ntpServersTreeViewSelectRow)

        self.ntpSrvAddButton.connect ("clicked", self.ntpSrvAddButtonClicked)
        self.ntpSrvAddButton.set_sensitive (True)
        self.ntpSrvEditButton.connect ("clicked", self.ntpSrvEditButtonClicked)
        self.ntpSrvEditButton.set_sensitive (False)
        self.ntpSrvDelButton.connect ("clicked", self.ntpSrvDelButtonClicked)
        self.ntpSrvDelButton.set_sensitive (False)

        #Find out if ntpd is currently running.  If so, activate checkbox
        ntpStatus = scdMainWindow.dateBackend.isNtpRunning()
        if ntpStatus == 1:
            self.ntpCheckButton.set_active(True)
        elif ntpStatus == None:
            text = (_("The NTP initscript (%s) does not seem to be functioning "
                      "properly.  Try running 'rpm -V ntp' to see if the initscript "
                      "has been modified.  system-config-date will exit now.")
                      % '/etc/rc.d/init.d/ntpd')
            dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, text)

            dlg.set_title(_("Error"))
            dlg.set_default_size(100, 100)
            dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
            dlg.set_border_width(2)
            dlg.set_modal(True)
            rc = dlg.run()
            dlg.destroy()

            import os
            os._exit(1)

        ntpBroadcastClient = scdMainWindow.dateBackend.getNtpBroadcastClient()
        #print "ntpBroadcastClient = " + str (ntpBroadcastClient)
        self.ntpBroadcastClientCheckButton.set_active(ntpBroadcastClient)

        (self.ntpServers, self.ntpLocalTimeSource) = scdMainWindow.dateBackend.getNtpServers ()

        self.ntpLocalTimeSourceButton.set_active (self.ntpLocalTimeSource)

        self.ntpIburst = scdMainWindow.dateBackend.getIburst ()

        self.ntpIburstButton.set_active (self.ntpIburst)

        self.ntpListStore.clear ()
        for ntpServer in self.ntpServers:
            iter = self.ntpListStore.append ()
            self.ntpListStore.set_value (iter, self.NTPSERVER, ntpServer)

        self.ntpCheckButtonClicked ()

        self.hourEntry.connect("changed", self.changed)
        self.minEntry.connect("changed", self.changed)
        self.secEntry.connect("changed", self.changed)

    def updateDateTime (self):
        self.dateTimeLabel.set_markup ("<tt>%s</tt>" % time.strftime ("%Ec"))
        return True

    def list_sort (self, store, iter1, iter2, *args):
        h1 = store.get_value (iter1, self.NTPSERVER).lower ()
        h2 = store.get_value (iter2, self.NTPSERVER).lower ()
        h1split = h1.split ('.')
        h1split.reverse ()
        h2split = h2.split ('.')
        h2split.reverse ()
        #print "h1split:", h1split, "h2split:", h2split
        for i in xrange (min (len (h1split), len (h2split))):
            if h1split[i] > h2split[i]:
                #print "%s > %s" % (h1split[i], h2split[i])
                return 1
            elif h1split[i] < h2split[i]:
                #print "%s < %s" % (h1split[i], h2split[i])
                return -1
        if len (h1split) < len (h2split):
            #print "%s shorter than %s" % (h1, h2)
            return 1
        elif len (h1split) > len (h2split):
            #print "%s longer than %s" % (h1, h2)
            return -1
        else:
            #print "%s == %s" % (h1, h2)
            return 0

    def filter(self, widget, max_value):
        num_text = widget.get_text ()

        # permit temporary empty values (for pasting, gets treated as "0")
        if num_text == "":
            return

        # check for non-digits
        for char in num_text:
            if (char not in string.digits):
                widget.set_text (str (widget.get_data ('last_value')))
                return

        # convert to int
        try:
            num = int (num_text)
        except ValueError:
            widget.set_text (str (widget.get_data ('last_value')))
            return

        # check for max value
        if num > max_value:
            widget.set_text (str (widget.get_data ('last_value')))
            return

        widget.set_data ('last_value', num)

    def getDate(self):
        return self.cal.get_date()

    def getTime(self):
        if self.flag == True:
            hour = self.hourEntry.get_text()
            min = self.minEntry.get_text()
            sec = self.secEntry.get_text()
        else:
            lt = time.localtime ()
            hour, min, sec = lt.tm_hour, lt.tm_min, lt.tm_sec

        return hour, min, sec

    def getNtpEnabled (self):
        return self.ntpCheckButton.get_active ()

    def getNtpServers (self):
        return self.ntpServers

    def getNtpBroadcastClient (self):
        return self.ntpBroadcastClientCheckButton.get_active ()

    def getNtpLocalTimeSource (self):
        return self.ntpLocalTimeSourceButton.get_active ()

    def getNtpIburst (self):
        return self.ntpIburstButton.get_active ()

    def ntpCheckButtonClicked (self, *args):
        use_ntp = self.ntpCheckButton.get_active ()

        self.manualNtpNotebook.set_current_page (use_ntp and 1 or 0)

    def ntpSrvList (self):
        list = []
        iter = self.ntpListStore.get_iter_first ()
        while iter:
            list.append (self.ntpListStore.get_value (iter, self.NTPSERVER))
            iter = self.ntpListStore.iter_next (iter)
        return list

    def ntpSrvValidAdd (self, host):
        return len (host) > 0 and host not in self.ntpSrvList ()

    def ntpSrvReachable_cb (self, pid, status, *args):
        if status != 0:
            self.modal_dialog.response (gtk.RESPONSE_REJECT)
        else:
            self.modal_dialog.response (gtk.RESPONSE_OK)

    def progress_pulse (self, progress_bar):
        if self.modal_dialog:
            progress_bar.pulse ()
            return True
        else:
            return False

    def ntpSrvReachable (self, host):
        argv = ["/usr/sbin/ntpdate", "-d", host]
        #debug: argv = ["/bin/sleep", "10"]
        (pid, stdin, stdout, stderr) = gobject.spawn_async (argv, flags = gobject.SPAWN_STDOUT_TO_DEV_NULL | gobject.SPAWN_STDERR_TO_DEV_NULL  | gobject.SPAWN_DO_NOT_REAP_CHILD)
        self.modal_dialog = gtk.MessageDialog (parent = self.mainWindow,
                flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                type = gtk.MESSAGE_INFO,
                buttons = gtk.BUTTONS_CANCEL,
                message_format = _("Checking whether NTP server '%s' is reachable...") % (host))
        progress_bar = gtk.ProgressBar ()
        self.modal_dialog.get_child ().add (progress_bar)
        progress_bar.show ()
        progress_bar.pulse ()
        pbar_id = gobject.timeout_add (100, self.progress_pulse, progress_bar)
        spawn_id = gobject.child_watch_add (pid, self.ntpSrvReachable_cb)
        result = self.modal_dialog.run ()
        gobject.source_remove (spawn_id)
        gobject.source_remove (pbar_id)
        md = self.modal_dialog
        self.modal_dialog = None
        md.destroy ()
        if result == gtk.RESPONSE_CANCEL or result == gtk.RESPONSE_DELETE_EVENT:
            #print "cancel, delete"
            self.modal_dialog = gtk.MessageDialog (parent = self.mainWindow,
                    flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                    type = gtk.MESSAGE_QUESTION,
                    buttons = gtk.BUTTONS_YES_NO,
                    message_format = _("You cancelled checking whether NTP server '%s' is reachable. Do you still want your changes to take effect?") % (host))
            result = self.modal_dialog.run ()
            self.modal_dialog.destroy ()
            self.modal_dialog = None
            if result == gtk.RESPONSE_YES:
                return True
            else:
                return False
        elif result == gtk.RESPONSE_REJECT:
            #print "reject"
            self.modal_dialog = gtk.MessageDialog (parent = self.mainWindow,
                flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                type = gtk.MESSAGE_QUESTION,
                buttons = gtk.BUTTONS_YES_NO,
                message_format = _("Host '%s' is not reachable or doesn't act as an NTP server. Do you still want your changes to take effect?") % (host))
            result = self.modal_dialog.run ()
            self.modal_dialog.destroy ()
            self.modal_dialog = None
            if result == gtk.RESPONSE_YES:
                return True
            else:
                return False
        else:
            #print "ok"
            return True

    def ntpServersTreeViewSelectRow (self, *args):
        store, iter = self.ntpServersTreeView.get_selection ().get_selected_rows ()
        if iter and len (iter):
            self.ntpSrvDelButton.set_sensitive (True)
        else:
            self.ntpSrvDelButton.set_sensitive (False)
        if iter and len (iter) == 1:
            self.ntpSrvEditButton.set_sensitive (True)
        else:
            self.ntpSrvEditButton.set_sensitive (False)
        if self.added_row_reference != None:
            # canceled adding a host
            #print self.added_row_reference.get_path ()
            row_ref = self.added_row_reference
            self.added_row_reference = None
            self.ntpListStore.remove (self.ntpListStore.get_iter (row_ref.get_path ()))

    def ntpSrvAddButtonClicked (self, args):
        iter = self.ntpListStore.append ()
        self.ntpListStore.set_value (iter, self.NTPSERVER, _('New NTP Server'))
        path = self.ntpListStore.get_path (iter)
        self.ntpServersTreeView.set_cursor (path, self.ntpServersTreeView.get_column (self.NTPSERVER), True)
        self.ntpSrvButtonbox.set_sensitive (False)
        self.added_row_reference = gtk.TreeRowReference (self.ntpListStore, self.ntpListStore.get_path (iter))

    def ntpSrvEditButtonClicked (self, *args):
        store, rows = self.ntpServersTreeView.get_selection ().get_selected_rows ()
        if rows and len (rows) == 1:
            path, column = self.ntpServersTreeView.get_cursor ()
            self.ntpServersTreeView.set_cursor (path, column, True)

    def cell_edited (self, cell, path, new_text, *args):
        #print "cell:", cell, "path:", path, "new_text:", new_text, "args:", args
        #print "before:", self.ntpListStore[path][0]
        if self.ntpSrvValidAdd (new_text) and self.ntpSrvReachable (new_text):
            if self.added_row_reference == None:
                old_text = self.ntpListStore[path][0]
                self.ntpListStore[path][0] = new_text
                if old_text in self.ntpServers:
                    self.ntpServers[self.ntpServers.index (old_text)] = new_text
            else:
                self.ntpListStore[path][0] = new_text
                self.added_row_reference = None
                self.ntpServers.append (new_text)
        else:
            if self.added_row_reference != None:
                row_ref = self.added_row_reference
                self.added_row_reference = None
                self.ntpListStore.remove (self.ntpListStore.get_iter (row_ref.get_path ()))

        self.ntpSrvButtonbox.set_sensitive (True)

    def cell_editing_canceled (self, *args):
        if self.added_row_reference != None:
            # canceled adding a host
            row_ref = self.added_row_reference
            self.added_row_reference = None
            self.ntpListStore.remove (self.ntpListStore.get_iter (row_ref.get_path ()))

        self.ntpSrvButtonbox.set_sensitive (True)

    def ntpSrvDelButtonClicked (self, *args):
        store, rows = self.ntpServersTreeView.get_selection ().get_selected_rows ()
        rows.reverse ()
        for row in rows:
            iter = store.get_iter (row)
            if iter:
                host = self.ntpListStore.get_value (iter, self.NTPSERVER)
                self.ntpListStore.remove (iter)
                self.ntpServers.remove (host)

    def changed(self, *args):
        self.flag = True

    def getVBox(self):
        return self.mainVBox

# vim: et ts=4
