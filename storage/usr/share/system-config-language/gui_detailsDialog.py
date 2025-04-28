# Copyright 2007  Red Hat, Inc.
#
# Lingning Zhang <lizhang@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 only
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import os

import gtk
import gtk.glade
import gobject


import gettext
_ = lambda x: gettext.ldgettext("system-config-language", x)

if os.access("data/yumhelpers.glade", os.R_OK):
    gygladefn = "data/yumhelpers.glade"
else:
    gygladefn = "/usr/share/system-config-language/yumhelpers.glade"

class GuiDetailsDialog:
    def __init__(self, parent = None, type = gtk.MESSAGE_INFO,
                 buttons = None, text = None, secondary = None):
        self.xml = gtk.glade.XML(gygladefn, domain="pirut")
        self.dialog = self.xml.get_widget("graphicalYumDetailsDialog")
        if parent:
            self.parent = parent
            self.dialog.set_transient_for(parent)
            self.dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.dialog.set_icon_name(self._get_stock_from_type(type))

        self.timeout = None
        self.countdownID = None
        self.timeoutID = None

        i = self.xml.get_widget("graphicalYumDetailsImage")
        i.set_from_stock(self._get_stock_from_type(type), 6)

        e = self.xml.get_widget("graphicalYumDetailsExpander")
        e.hide()

        if text:
            self.set_markup(text)
            self.dialog.set_title(text)
        if secondary:
            self.format_secondary_text(secondary)
        if buttons and buttons != gtk.BUTTONS_NONE:
            self.set_buttons(buttons)

    def _get_stock_from_type(self, type):
        if type == gtk.MESSAGE_ERROR:
            return 'gtk-dialog-error'
        elif type == gtk.MESSAGE_WARNING:
            return 'gtk-dialog-warning'
        elif type == gtk.MESSAGE_QUESTION:
            return 'gtk-dialog-question'
        elif type == gtk.MESSAGE_INFO:
            return 'gtk-dialog-info'
        else:
            return 'gtk-dialog-info'

    def set_markup(self, text):
        l = self.xml.get_widget("graphicalYumDetailsPrimaryLabel")
        l.set_markup("<span weight=\"bold\" size=\"large\">" + text + "</span>")
        
    def format_secondary_text(self, text):
        l = self.xml.get_widget("graphicalYumDetailsSecondaryLabel")
        l.set_markup(text)

    def format_secondary_markup(self, text):
        self.format_secondary_text(text)

    def set_buttons(self, button_list):
        buttons = map(lambda x: apply(self.add_button, x), button_list)
        last = button_list[-1]
        self.dialog.set_default_response(last[1])
        return buttons

    def add_button(self, text, rid, image = None):
        b = self.dialog.add_button(text, rid)
        if image:
            b.set_image(gtk.image_new_from_stock(image, gtk.ICON_SIZE_BUTTON))
        return b

    def set_default_response(self, rid):
        self.dialog.set_default_response(rid)

    def set_details(self, text = None, buffer = None):
        if buffer:
            b = buffer
        elif text:
            b = gtk.TextBuffer()
            b.set_text(text)
        else:            
            return 
        details = self.xml.get_widget("graphicalYumDetails")
        details.set_buffer(b)
        e = self.xml.get_widget("graphicalYumDetailsExpander")
        e.show()
        e.connect("activate", self._detailsActivated)

        l = self.xml.get_widget("detailsLabel")
        l.set_text("_Details")
        l.set_property("use-underline", True)

    def expand_details(self):
        e = self.xml.get_widget("graphicalYumDetailsExpander")
        e.activate()

    def _detailsActivated(self, *args):
        if self.timeout is not None:
            gobject.source_remove(self.timeoutID)            
            gobject.source_remove(self.countdownID)
            self.timeout = None
            self.l.hide()

    def _timedOut(self, default):
        if default:
            self.dialog.response(default)
        else:
            self.dialog.response(gtk.RESPONSE_OK)

    def _countdown(self):
        self.timeout -= 1
        if self.timeout >= 0:
            self.l.set_markup(_("<i>Will continue in %d seconds...</i>")
                              % (self.timeout,))
            return True
        return False

    def run(self, timeout = None, default = None):
        if timeout:
            self.timeout = timeout
            self.l = gtk.Label()
            self.l.set_property("xalign", 0.0)
            self.l.set_markup(_("<i>Will continue in %d seconds...</i>")
                              % (self.timeout,))
            v = self.xml.get_widget("vbox2")
            v.pack_start(self.l)
            self.countdownID = gobject.timeout_add(1000, self._countdown)
            self.timeoutID = gobject.timeout_add(timeout * 1000,
                                                 self._timedOut, default)
        self.dialog.show()
        rc = self.dialog.run()
        if self.timeout is not None:
            gobject.source_remove(self.countdownID)
            gobject.source_remove(self.timeoutID)            
        return rc

    def destroy(self):
        return self.dialog.destroy()
