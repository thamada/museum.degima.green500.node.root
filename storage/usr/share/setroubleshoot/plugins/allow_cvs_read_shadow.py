#
# Authors: Karl MacMillan <kmacmillan@mentalrootkit.com>
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
    summary = _('''
    SELinux prevented the CVS application from reading the shadow password file.
    ''')

    problem_description = _('''
    SELinux prevented the CVS application from reading the shadow password file.
    The CVS application requires this access when it is configured for direct
    connection (i.e., pserver) and to authenticate to the system password / shadow
    files without PAM. It is possible that this access request signals an intrusion
    attempt.

    It is recommended that CVS be configured to use PAM, authenticate to a separate
    user file, or use another protocol (e.g., SSH) instead of allowing this access.
    See the CVS manual for more details on why this access is potentially insecure: 
    (<a href="http://ximbiot.com/cvs/manual/cvs-1.11.22/cvs_2.html">http://ximbiot.com/cvs/manual/cvs-1.11.22/cvs_2.html</a>).
    ''')

    fix_description = _('''
    Changing the "$BOOLEAN" boolean to true will allow this access:
    "setsebool -P $BOOLEAN=1"
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'
                 
    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['cvs_t']) and \
           avc.matches_target_types(['shadow_t']):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="allow_cvs_read_shadow")
            return self.report(avc, _("CVS"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd,
                               level="green")
        else:
            return None
