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
    SELinux is preventing the ftp daemon from reading users home directories ($TARGET_PATH).
    ''')

    problem_description = _('''
    SELinux has denied the ftp daemon access to users home directories
    ($TARGET_PATH). Someone is attempting to login via your ftp daemon
    to a user account. If you only setup ftp to allow anonymous ftp,
    this could signal an intrusion attempt.
    ''')

    fix_description = _('''
    If you want ftp to allow users access to their home directories
    you need to turn on the $BOOLEAN boolean: "setsebool -P
    $BOOLEAN=1"
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'
    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['ftpd_t']) and \
           avc.matches_target_types(['home_root_t', '.*_`home_t', '.*_home_dir_t']):
            # MATCH
            avc.set_alt_path("HOME_DIRECTORY")
            avc.set_template_substitutions(BOOLEAN="ftp_home_dir")
            return self.report(avc, _("FTP"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd, level="green")
        else:
            return None




