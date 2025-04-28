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
    SELinux is preventing the samba daemon from reading nfs file systems.
    ''')

    problem_description = _('''
    SELinux has denied the samba daemon access to nfs file
    systems. Someone is attempting to access an nfs file system via
    your samba daemon. If you did not setup samba to share nfs file
    systems, this probably signals an intrusion attempt.
    ''')

    fix_description = _('''
    If you want samba to share nfs file systems you need to turn on
    the $BOOLEAN boolean: "setsebool -P $BOOLEAN=1"
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'
    
    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['smbd_t']) and \
           avc.matches_target_types(['nfs_t']):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="samba_share_nfs")
            return self.report(avc, _("SAMBA"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd,
                               level="green")
        else:
            return None

