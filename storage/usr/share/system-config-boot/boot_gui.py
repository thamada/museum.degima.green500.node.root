# boot_gui.py - GUI front end code for boot configuration
#
# -*- coding: utf-8 -*-
#
## Copyright (C) 2001-2007 Red Hat, Inc.
## Copyright (C) 2001-2007 Harald Hoyer <harald@redhat.com>

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

import string
import gtk
import gobject
import sys
import os

from grub import (readBootDB, writeBootFile)


def gui_error_dialog ( message, parent_dialog=None,
                      message_type=gtk.MESSAGE_ERROR,
                      widget=None, page=0, broken_widget=None ):

    dialog = gtk.MessageDialog( parent_dialog,
                               gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                               message_type, gtk.BUTTONS_OK,
                               message )

    if widget != None:
        if isinstance (widget, gtk.CList):
            widget.select_row (page, 0)
        elif isinstance (widget, gtk.Notebook):
            widget.set_current_page (page)
    if broken_widget != None:
        broken_widget.grab_focus ()
        if isinstance (broken_widget, gtk.Entry):
            broken_widget.select_region (0, -1)

    if parent_dialog:
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.set_transient_for(parent_dialog)
    else:
        dialog.set_position (gtk.WIN_POS_CENTER)

    ret = dialog.run ()
    dialog.destroy()
    return ret


class BootWindow:
    #You must specify a runPriority for the order in which you wish your module to run
    icon = None
    toplevel = None
    runPriority = 30
    moduleName = N_("Boot")
    moduleClass = "reconfig"
    windowTitle = N_("Boot Configuration")
    htmlTag = "boot"
    commentTag = N_("A configuration tool for the boot loader")
    shortMessage = N_("Please select the default boot entry for the system.")

    def getNext(self):
        pass
    
    def destroy(self, args):
        gtk.main_quit()
    
    def okClicked(self, *args):
        if self.apply():
            gtk.main_quit()
        else:
            #apply failed for some reason, so don't exit the gtk main loop
            pass

    def setupScreen(self):
        try:
            (self.probedBoot, self.probedTimeout, kernels) = readBootDB()
        except:
            gui_error_dialog(_("Error reading /boot/grub/grub.conf."))
            sys.exit(10)


        self.bootStore = gtk.ListStore(gobject.TYPE_STRING)

        #Add icon to the top frame
        p = None
        try:
            p = gtk.gdk.pixbuf_new_from_file("../pixmaps/gnome-boot.png")
        except:
            try:
                p = gtk.gdk.pixbuf_new_from_file("/usr/share/system-config-boot/pixmaps/gnome-boot.png")
            except:
                pass

        if p:
            self.icon = gtk.Image()
            self.icon.set_from_pixbuf(p)

        self.bootView = gtk.TreeView(self.bootStore)
        self.col = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=0)
        self.bootView.append_column(self.col)
        self.bootView.set_property("headers-visible", False)

        self.bootViewSW = gtk.ScrolledWindow()
        self.bootViewSW.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.bootViewSW.set_shadow_type(gtk.SHADOW_IN)
        self.bootViewSW.add(self.bootView)

        self.myHbox = gtk.HBox()
        self.myHbox.set_spacing(5)
        self.timeoutLabel = gtk.Label(_("Timeout (in seconds):"))
        adj = gtk.Adjustment(15, 1, 1000, 1, 5)
        self.timeoutEntry = gtk.SpinButton(adj, 1, 0)
        self.myHbox.pack_start(self.timeoutLabel, False)
        self.myHbox.pack_start(self.timeoutEntry, False)

        self.probedBoot = 0
        self.probedTimeout = 15
        
        for k in kernels:
            self.bootStore.append([k])

        self.setDefault()

        tooltips = gtk.Tooltips()
        tooltips.set_tip(self.timeoutEntry, _("Set a timeout, in seconds, before automatically booting the selected entry."))
        tooltips.enable()
        
        self.myVbox = gtk.VBox()
        self.myVbox.set_spacing(5)
        self.myVbox.pack_start(self.bootViewSW, True)
        self.myVbox.pack_start(self.myHbox, False)        
        #self.myVbox.pack_start(self.Xemu3CheckButton, False, 3)

    def setDefault(self):
        parent = None
        iter = self.bootStore.get_iter_root()
        next = 1
        num = 0
        while iter:
            if num == self.probedBoot:
                selection = self.bootView.get_selection()
                selection.unselect_all()
                selection.select_iter(iter)
                path = self.bootStore.get_path(iter)
                self.bootView.set_cursor(path, self.col, False)
                self.bootView.scroll_to_cell(path, self.col, True, 0.5, 0.5)
                break
            iter = self.bootStore.iter_next(iter)
            num += 1

        self.timeoutEntry.set_value(self.probedTimeout)
        
 
    def launch(self, doDebug=None):
        self.doDebug = doDebug
        if doDebug:
            self.setupScreen()
        return FirstbootModuleWindow.launch(self)

    def apply(self, *args):
        data, iter = self.bootView.get_selection().get_selected()

        if not iter:
            return 1
        
        title = self.bootStore.get_value(iter, 0)
        
        iter = self.bootStore.get_iter_root()
        next = 1
        num = 0
        while iter:            
            if self.bootStore.get_value(iter, 0) == title:
                break
            iter = self.bootStore.iter_next(iter)
            num += 1
            
        writeBootFile(self.timeoutEntry.get_value(), num)
        try:
            # If we're in reconfig mode, this will fail
            # because there is no self.mainWindow            
            self.mainWindow.destroy()
        except:
            pass            
        return 1
        
    def stand_alone(self, doDebug = None):
        self.doDebug = doDebug
        self.setupScreen()

        title = BootWindow.windowTitle
        iconPixbuf=None

        self.mainWindow = gtk.Dialog()
        self.mainWindow.connect("destroy", self.destroy)
        self.mainWindow.set_border_width(10)
        self.mainWindow.set_size_request(400, 350)
        self.mainWindow.set_position(gtk.WIN_POS_CENTER)

        if iconPixbuf:
            self.mainWindow.set_icon(iconPixbuf)

        if title:
            self.mainWindow.set_title(_(title))

        okButton = self.mainWindow.add_button('gtk-ok', 0)
        okButton.connect("clicked", self.okClicked)

        toplevel = gtk.VBox()
        toplevel.set_spacing(5)
        iconBox = gtk.HBox(False, 5)
        if self.icon:
            iconBox.pack_start(self.icon, False)

        if not self.shortMessage:
            self.shortMessage = ""
        msgLabel = gtk.Label(_(self.shortMessage))
        msgLabel.set_line_wrap(True)
        msgLabel.set_alignment(0.0, 0.5)            
        iconBox.pack_start(msgLabel)

        toplevel.pack_start(iconBox, False)
        toplevel.pack_start(self.myVbox, True)

        #Remove the hsep from the dialog.  It's ugly
        hsep = self.mainWindow.get_children()[0].get_children()[0]
        self.mainWindow.get_children()[0].remove(hsep)
        self.mainWindow.vbox.pack_start(toplevel)
        self.mainWindow.show_all()
        gtk.main()


childWindow = BootWindow


