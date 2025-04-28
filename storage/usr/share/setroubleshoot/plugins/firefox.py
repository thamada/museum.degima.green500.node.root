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
    SELinux is preventing firefox from making its memory writable and executable.
    ''')
    
    problem_description = _('''
    The $SOURCE application attempted to change the access protection
    of memory (e.g., allocated using malloc).  This is a potential
    security problem.  Firefox is probably not the problem here ,but one of its plugins.  You could remove the plugin and the app would no longer require the access.  If you figure out which plugin is causing the access request, please open a bug report on the plugin.
    ''')
    
    fix_description = _('''
There are two ways to fix this problem, you can install the nsspluginwrapper package, which will cause firefox to run its plugins under a separate process.  This process will allow the execmem access.  This is the safest choice.  You could also turn off the allow_unconfined_nsplugin_transition boolean.  
<br>
setsebool -P allow_unconfined_nsplugin_transition=0
</br>
    ''')

    fix_cmd = "yum install nspluginwrapper"
    
    def __init__(self):
        Plugin.__init__(self,__name__)

    def analyze(self, avc):
        if avc.matches_source_types(['unconfined_t']) and \
           avc.has_any_access_in(['execmem']) and \
           avc.source == "firefox":
            # MATCH
            return self.report(avc, _("Memory"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd)
        else:
            return None

