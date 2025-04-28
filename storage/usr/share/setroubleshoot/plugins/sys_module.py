# @author Thomas Liu <tliu@redhat.com>
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

class plugin(Plugin):
    summary =_('''
    Your system may be seriously compromised! $SOURCE_PATH tried to load a kernel module.
    ''')

    problem_description = _('''
    SELinux has prevented $SOURCE from loading a kernel module.
    All confined programs that need to load kernel modules should have already had policy
    written for them. If a compromised application 
    tries to modify the kernel this AVC will be generated. This is a serious 
    issue. Your system may very well be compromised.
    ''')

    fix_description = "Contact your security administrator and report this issue." 
    fix_cmd = ""
    def __init__(self):
        Plugin.__init__(self, __name__)
        self.set_priority(53)

    def analyze(self, avc):
        if avc.has_any_access_in(['sys_module']):
            # MATCH
            return self.report(avc, None,
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd, level="red")
        return None
