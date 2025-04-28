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

import signal
import sys
import os

from exception import handleMyException

os.environ["PYgtk_FATAL_EXCEPTIONS"] = '1'
PROGNAME="system-config-boot"
from version import PRG_VERSION

from exception import installExceptionHandler
    
installExceptionHandler(PROGNAME, PRG_VERSION)

import locale
try:
    locale.setlocale (locale.LC_ALL, "")
except locale.Error, e:
    import os
    os.environ['LC_ALL'] = 'C'
    locale.setlocale (locale.LC_ALL, "")
import gettext
gettext.bind_textdomain_codeset(PROGNAME,locale.nl_langinfo(locale.CODESET))
gettext.bindtextdomain(PROGNAME, '/usr/share/locale')
gettext.textdomain(PROGNAME)
_ = lambda x: gettext.lgettext(x)
import __builtin__
__builtin__.__dict__['_'] = _
__builtin__.__dict__['N_'] = _

if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)

    import boot_gui

    if os.getuid() != 0:
        boot_gui.gui_error_dialog(_("Please run %s as root!") % PROGNAME, None)
        sys.exit(10)
    
    app = boot_gui.childWindow()
    app.stand_alone()

