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
    SELinux is preventing the zebra daemon from writing its configuration files
    ''')

    problem_description = _('''
    SELinux has denied the zebra daemon from writing out its
    configuration files. Ordinarily, zebra is not required to write
    its configuration files.  If zebra was not setup to write the
    config files, this could signal an intrusion attempt.
    ''')

    fix_description = _('''
    If you want to allow zebra to overwrite its configuration you must
    turn on the $BOOLEAN boolean: "setsebool -P
    $BOOLEAN=1"
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'
    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['zebra_t'])      and \
           avc.matches_target_types(['zebra_conf_t']) and \
           avc.has_any_access_in(avc.create_file_perms):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="allow_zebra_write_config")
            return self.report(avc, _("Zebra"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd,
                               level="green")
        return None




