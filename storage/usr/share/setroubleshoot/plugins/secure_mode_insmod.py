#
# Copyright (C) 2006 Red Hat, Inc. #
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
    SELinux is preventing the kernel modules from being loaded.
    ''')

    problem_description = _('''
    SELinux has denied kernel module utilities from modifying
    kernel modules. This machine is hardened to not allow the kernel to
    be modified, except in single user mode.  If you did not try to
    manage a kernel module, this probably signals an intrusion.
    ''')

    fix_description = _('''
    If you allow the management of the kernel modules on your machine,
    turn off the $BOOLEAN boolean: "setsebool -P
    $BOOLEAN=0".
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=0'
    
    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_target_types(['insmod_exec_t']) and \
           avc.has_any_access_in(['transition']):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="secure_mode_insmod")
            return self.report(avc, _("Kernel"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd)
        else:
            return None

