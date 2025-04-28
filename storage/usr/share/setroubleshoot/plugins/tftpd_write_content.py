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
    SELinux is preventing the tftp daemon from modify $TARGET_PATH.
    ''')

    problem_description = _('''
    SELinux prevented the tftp daemon from writing to $TARGET_PATH. Usually 
    tftpd is setup only to read content and is not allowed to modify it.  If
    you setup tftpd to modify $TARGET_PATH need to change its label.  If you  
    did not setup tftp to modify $TARGET_PATH, this could signal an intrusion attempt.
    ''')

    fix_description = _('''
    If you want to change the file context of $TARGET_PATH so that the tftp
    daemon can modify it, you need to execute it using<br>
    <b># semanage fcontext -m tftpdir_rw_t '/tftpboot(/.*)?'</b>
    <br><b># restorecon -R -v /tftpboot</b></br>
    ''')

    fix_cmd = ""

    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['tftpd_t'])    and \
           avc.matches_target_types(['tftpdir_t'])  and \
           avc.has_any_access_in(['add_name','create','write']):
            # MATCH
            return self.report(avc, _("TFTP"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd,
                               level="green")
        return None

