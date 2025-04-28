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
    SELinux is preventing the modification of the running policy.
    ''')
    
    problem_description = _('''
    SELinux has denied the management tools from modifying the way the
    SELinux policy runs. This machine is hardened, so if you did not run
    any SELinux tools, this probably signals an intrusion.
    ''')
    
    fix_description = _('''
    If you want to modify the way SELinux is running on your machine
    you need to bring the machine to single user mode with enforcing
    turned off.  The turn off the secure_mode_policyload boolean:
    "setsebool -P secure_mode_policyload=0".
    ''')

    def __init__(self):
        Plugin.__init__(self,__name__)

    def analyze(self, avc):
        if avc.has_any_access_in(['setenforce', 'load_policy', 'setsebool']):
            # MATCH
            return self.report(avc, None,
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd)
        else:
            return None

