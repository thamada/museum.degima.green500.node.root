#
# Copyright (C) 2006 Red Hat, Inc.
#
# Authors: Dan Walsh <dwalsh@redhat.com>
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
    SELinux is preventing the ftp daemon from writing files outside the home directory ($TARGET_PATH).
    ''')

    problem_description = _('''
    SELinux has denied the ftp daemon write access to directories outside
    the home directory ($TARGET_PATH). Someone has logged in via
    your ftp daemon and is trying to create or write a file. If you only setup
    ftp to allow anonymous ftp, this could signal an intrusion attempt.
    ''')

    fix_description = _('''
    If you do not want SELinux preventing ftp from writing files anywhere on
    the system you need to turn on the $BOOLEAN boolean: "setsebool -P
    $BOOLEAN=1"
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'
    def __init__(self):
        Plugin.__init__(self, __name__)
	self.set_priority(55)

    def analyze(self, avc):
        if avc.matches_source_types(['ftpd_t']) and \
           avc.has_any_access_in(['add_name', 'write', 'create']):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="allow_ftpd_full_access")
            return self.report(avc, _("FTP"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd)
        else:
            return None




