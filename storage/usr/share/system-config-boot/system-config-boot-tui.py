# -*- coding: utf-8 -*-

## Copyright (C) 2001-2007 Red Hat, Inc.
## Copyright (C) 2001-2007 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2009 Kishan Goyal <kishan@fedoraproject.org>
## Copyright (C) 2009 Meejanur Rahaman <realmeejan@gmail.com>

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

import sys
from snack import *

PROGNAME="system-config-boot"

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
from grub import (readBootDB, writeBootFile)

def main(entry_value='1',kernels=[]):
    try:
        (default_value, entry_value, kernels)=readBootDB()
    except:
        print >> sys.stderr, _("Error reading /boot/grub/grub.conf.")
	sys.exit(10)

    screen=SnackScreen()

    while True:
        g=GridForm(screen, _("Boot configuration"),1,5)
        if len(kernels)>0 :
            li=Listbox(height=len(kernels), width=20, returnExit=1)
            for i, x in enumerate(kernels):
                li.append(x,i)
            g.add(li, 0, 0)
            li.setCurrent(default_value)

        bb = ButtonBar(screen, ((_("Ok"), "ok"), (_("Cancel"), "cancel")))

        e=Entry(3, str(entry_value))
        l=Label(_("Timeout (in seconds):"))
        gg=Grid(2,1)
        gg.setField(l,0,0)
        gg.setField(e,1,0)

        g.add(Label(''),0,1)
        g.add(gg,0,2)
        g.add(Label(''),0,3)
        g.add(bb,0,4,growx=1)
        result = g.runOnce()
        if bb.buttonPressed(result) == 'cancel':
            screen.finish()
            sys.exit(0)
        else:
            entry_value = e.value()
            try :
                c = int(entry_value)
                break
            except ValueError:
                continue

    writeBootFile(c, li.current())
    screen.finish()

if __name__== '__main__':
    main()
