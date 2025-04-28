#!/usr/bin/python

## system-config-nfs.py - Contains the startup script for system-config-nfs
## Copyright (C) 2002 - 2003, 2009 Red Hat, Inc.
## Copyright (C) 2002 - 2003 Brent Fox <bfox@redhat.com>

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

import sys
import signal

import locale
import gettext
gettext.install ('system-config-nfs', codeset = locale.getpreferredencoding (), names = ["gettext"])
signal.signal (signal.SIGINT, signal.SIG_DFL)

try:
    import gtk
except:
    print _("system-config-nfs requires a currently running X server.")
    sys.exit (0)

import mainWindow
mainWindow.mainWindow()
