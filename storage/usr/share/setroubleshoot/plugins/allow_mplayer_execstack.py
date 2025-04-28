#
# Authors: Dan Walsh <dwalsh@redhat.com>
# Borrowed from Karl MacMillan <kmacmillan@mentalrootkit.com>
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
    SELinux prevented a mplayer plugin ($SOURCE_TYPE) from making the stack executable.
    ''')

    problem_description = _('''
    SELinux prevented the mplayer plugin ($SOURCE_TYPE) from making the stack
    executable.  An executable stack should not be required by any
    software (see <a href="http://people.redhat.com/drepper/selinux-mem.html">SELinux Memory Protection Tests</a>
    for more information). However, some versions of the mplayer plugin are known
    to require this access to work properly. You should check for updates
    to the software before allowing this access.
    ''')

    fix_description = _('''
    Changing the "$BOOLEAN" boolean to true will allow this access:
    "setsebool -P $BOOLEAN=1."
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'
    
    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['.*mplayer_t$']) and \
           avc.has_any_access_in(['execstack']):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="allow_mplayer_execstack")
            return self.report(avc, _("Media"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd)
        else:
            return None
