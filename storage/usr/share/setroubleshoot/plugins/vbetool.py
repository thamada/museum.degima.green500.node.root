# @author Dan Walsh <dwalsh@redhat.com>
#
# Copyright (C) 2009 Red Hat, Inc.
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
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import gettext
translation=gettext.translation('setroubleshoot-plugins', fallback=True)
_=translation.ugettext

from setroubleshoot.util import *
from setroubleshoot.Plugin import Plugin
import re
import os

class plugin(Plugin):
    summary =_('''
    SELinux has prevented vbetool from performing an unsafe memory operation.
    ''')

    problem_description = _('''
SELinux denied an operation requested by $SOURCE, a program used
to alter video hardware state.  This program is known to use
an unsafe operation on system memory but so are a number of
malware/exploit programs which masquerade as vbetool.  This tool is used to 
reset video state when a machine resumes from a suspend.  If your machine 
is not resuming properly your only choice is to allow this
operation and reduce your system security against such malware.

    ''')

    fix_description = _('''
If you decide to continue to run the program in question you will need
to allow this operation.  This can be done on the command line by
executing:

# setsebool -P mmap_low_allowed 1
''')

    fix_cmd = "/usr/sbin/setsebool -P mmap_low_allowed 1"

    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.has_any_access_in(['mmap_zero']) and \
                avc.matches_source_types(['vbetool_t']) and \
                os.stat(avc.spath).st_uid == 0:            

            # MATCH
            return self.report(avc, None,
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd, 
                               level="yellow", fixable=True, 
                               button_text=_("Turn off memory protection"))
        return None
