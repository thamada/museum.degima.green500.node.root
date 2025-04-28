
#
# Authors: Dan Walsh <dwalsh@redhat.com>
#
# Copyright (C) 2008 Red Hat, Inc.
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
import seobject

class plugin(Plugin):
    summary = _('''
    SELinux is preventing $SOURCE_PATH "$ACCESS" access on $TARGET_PATH.
    ''')

    problem_description = _('''

    SELinux denied access requested by $SOURCE. The current boolean 
    settings do not allow this access.  If you have not setup $SOURCE to
    require this access this may signal an intrusion attempt. If you do intend 
    this access you need to change the booleans on this system to allow 
    the access.
    ''')

    fix_description = _('''
    Confined processes can be configured to run requiring different access, SELinux provides booleans to allow you to turn on/off 
    access as needed.

    ''')

    fix_cmd = ''

    def __init__(self):
        Plugin.__init__(self, __name__)
        self.set_priority(60)

    def analyze(self, avc):
        if  len(avc.bools) > 0:
            fix = self.fix_description
            fix_cmd = ""
            bools = avc.bools
            if  len(bools) > 1:
                l = []
                for b in bools:
                    l.append(b[0])
                fix =  _("One of the following booleans is set incorrectly: <b>%s</b>") % ", ".join(l)

                fix_cmd += _("Choose one of the following to allow access:<br> " )
                for b in bools:
                    fix_cmd += "<br>%s<br><br>" % seobject.boolean_desc(b[0])
                    fix_cmd += "<b># setsebool -P %s %d</b><br>"  % (b[0], b[1])

            else:
                fix += _('The boolean <b>%s</b> is set incorrectly. ') % bools[0][0]
                fix += _("<br><br>Boolean Description:<br>%s<br><br>") % seobject.boolean_desc(bools[0][0])
                fix_cmd  += '<b># setsebool -P %s %d</b>'  % (bools[0][0], bools[0][1])
            return self.report(avc, None,
                               self.summary, self.problem_description,
                               fix, fix_cmd, level="green")
        return None
