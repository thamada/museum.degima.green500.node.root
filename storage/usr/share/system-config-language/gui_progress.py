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
import logging
import rpm

import gtk
import gtk.glade
import gtk.gdk as gdk

import gettext
_ = lambda x: gettext.ldgettext("system-config-language", x)

from yum.constants import *
from gui_errors import *

if os.access("data/yumhelpers.glade", os.R_OK):
    gygladefn = "data/yumhelpers.glade"
else:
    gygladefn = "/usr/share/system-config-language/yumhelpers.glade"

def _runGtkMain(*args):
    while gtk.events_pending():
        gtk.main_iteration()

class GuiTransactionProgress:    
    def __init__(self, progress):
        self.progress = progress

        self.rpmFD = None
        self.total = None
        self.num = 0
        
        self.installed_pkg_names = []
        self.tsInfo = None

    def callback(self, what, amount, total, h, user):        
        PREP = 0.25
        logmsg = ""
        
        if what == rpm.RPMCALLBACK_TRANS_START:
            if amount == 6:
                self.total = float(total)
                self.progress.set_markup("<i>%s</i>"
                                         %(_("Preparing transaction")))
        elif what == rpm.RPMCALLBACK_TRANS_PROGRESS:
            self.progress.set_fraction(amount * PREP / total)
        elif what == rpm.RPMCALLBACK_TRANS_STOP:
            self.progress.set_fraction(PREP) 
            self.progress.set_markup("")
        elif what == rpm.RPMCALLBACK_INST_OPEN_FILE:
            if h is not None:
                hdr, rpmloc = h
                try:
                    self.rpmFD = os.open(rpmloc, os.O_RDONLY)
                except OSError, e:
                    raise GuiError, "Unable to open %s: %s" %(rpmloc, e)
                self.progress.set_markup("<i>%s</i>"
                                         %(_("Updating %s") %(hdr['name'])))
                self.installed_pkg_names.append(hdr['name'])
                _runGtkMain()
                return self.rpmFD
        elif what == rpm.RPMCALLBACK_INST_CLOSE_FILE:
            os.close(self.rpmFD)
            self.progress.set_markup("")
            self.num += 1
            self.progress.set_fraction(self.num / self.total * (1 - PREP) + PREP)
            self.rpmFD = None

            hdr, rpmloc = h            
            if hdr['epoch'] is not None:
                epoch = "%s" %(hdr['epoch'],)
            else:
                epoch = "0"
            (n,a,e,v,r) = hdr['name'], hdr['arch'], epoch, hdr['version'], hdr['release']
            pkg = "%s.%s %s-%s" %(n,a,v,r)
            if self.tsInfo:
                txmbr = self.tsInfo.getMembers(pkgtup = (n,a,e,v,r))[0]
                if txmbr.output_state == TS_UPDATE:
                    logmsg = "Updated: %s" %(pkg,)
                else:
                    logmsg = "Installed: %s" %(pkg,)                
            
        elif what == rpm.RPMCALLBACK_INST_PROGRESS:
            cur = self.progress.get_fraction()
            perpkg = 1 / self.total * (1 - PREP)
            pct = amount/float(total)
            new = self.num / self.total * (1 - PREP) + PREP + (perpkg * pct)
            if new - cur > 0.05:
                self.progress.set_fraction(new)
        elif what == rpm.RPMCALLBACK_UNINST_START:
            self.progress.set_markup("<i>%s</i>"
                                          %(_("Cleanup %s") %(h,),))
        elif what == rpm.RPMCALLBACK_UNINST_PROGRESS:
            cur = self.progress.get_fraction()
            perpkg = 1 / self.total * (1 - PREP)
            pct = amount/float(total)
            new = self.num / self.total * (1 - PREP) + PREP + (perpkg * pct)
            if new - cur > 0.05:
                self.progress.set_fraction(new)
        elif what == rpm.RPMCALLBACK_UNINST_STOP:
            self.num += 1
            self.progress.set_fraction(self.num / self.total * (1 - PREP) + PREP)
            if h not in self.installed_pkg_names:
                logmsg = "Erased: %s" %(h,)
                
        _runGtkMain()
        if len(logmsg) > 0:
            log = logging.getLogger("yum.filelogging")
            log.info(logmsg)

class GuiProgress:
    def __init__(self, title, parent = None):
        self.xml = gtk.glade.XML(gygladefn, domain="pirut")
        self.dialog = self.xml.get_widget("graphicalYumProgressDialog")
        if parent:
            self.dialog.set_modal(True)
            self.dialog.set_transient_for(parent)
            self.dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

        self.dialog.set_title(title)
        t = self.xml.get_widget("graphicalYumProgressTitle")
        t.set_markup("<span weight=\"bold\" size=\"x-large\">" + title +
                     "</span>")

        self.pbar = self.xml.get_widget("graphicalYumProgressBar")
        self.set_fraction(0.0)

        self.label = self.xml.get_widget("graphicalYumProgressLabel")
        self.set_markup("")

    def show(self):
        self.dialog.show()
        self.dialog.window.set_cursor(gdk.Cursor(gdk.WATCH))
        _runGtkMain()

    def destroy(self):
        if self.dialog.window is not None:
            self.dialog.window.set_cursor(None)
        self.dialog.destroy()

    def set_fraction(self, fract):
        self.pbar.set_fraction(fract)

    def get_fraction(self):
        return self.pbar.get_fraction()

    def set_markup(self, txt):
        self.label.set_markup(txt)

    def set_pbar_text(self, txt):
        self.pbar.set_text(txt)

class GuiProgressCallback(GuiProgress):
    def __init__(self, title, parent = None, num_tasks = 1):
        GuiProgress.__init__(self, title, parent)
        
        self.num_tasks = float(num_tasks)
        self.cur_task = 0
        self.this_task = 1

    def progressbar(self, current, total, name = None):
        pct = float(current) / total
        curval = self.pbar.get_fraction()
        newval = (pct * 1/self.num_tasks) * self.this_task + \
                 (self.cur_task / self.num_tasks)
        if newval > curval + 0.001:
            self.set_fraction(newval)
            _runGtkMain()            

    def next_task(self, incr = 1, next = 1):
        self.cur_task += incr
        self.this_task = next
        self.set_pbar_text("")
        self.set_fraction(self.cur_task / self.num_tasks)
        _runGtkMain()
