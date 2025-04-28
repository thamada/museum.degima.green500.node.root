#
# Copyright (C) 2006 Red Hat, Inc.
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

class plugin(Plugin):
    summary =_('''
    SELinux is preventing the http daemon from communicating with the terminal.
    ''')

    problem_description = _('''
    SELinux is not allowing the http daemon to communicate with the
    terminal.  Most daemons do not need to communicate
    with the terminal.  httpd can be setup to require information
    during the boot process which would require this access.  If you
    did not setup httpd to require access to the terminal, this may
    signal an intrusion attempt.
    ''')

    fix_description = _('''
    If you want the http daemon to be able to access the terminal, you
    must set the $BOOLEAN boolean: "setsebool -P
    $BOOLEAN=1"
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'

    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['httpd_t']) and \
           avc.matches_target_types(['devtty_t', 'sysadm_tty_device_t', 'tty_device_t']):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="httpd_tty_comm")
            return self.report(avc, _("Web Server"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd)
        return None

