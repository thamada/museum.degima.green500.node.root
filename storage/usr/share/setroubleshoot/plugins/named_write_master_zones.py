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
    SELinux is preventing the named daemon from writing to the zone directory''')

    problem_description = _('''
    SELinux has denied the named daemon from writing zone
    files. Ordinarily, named is not required to write to these files.
    Only secondary servers should be required to write to these
    directories.  If this machine is not a secondary server, this
    could signal an intrusion attempt.
    ''')

    fix_description = _('''
    If you want named to run as a secondary server and accept zone
    transfers you need to turn on the $BOOLEAN boolean: "setsebool -P
    $BOOLEAN=1"
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'
    
    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['named_t'])      and \
           avc.matches_target_types(['named_zone_t']) and \
           avc.has_any_access_in(['add_name', 'write', 'create']):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="named_write_master_zones")
            return self.report(avc, _("Domain Name Service"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd,
                               level="green")

        return None




