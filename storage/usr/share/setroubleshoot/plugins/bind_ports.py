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
    SELinux is preventing $SOURCE_PATH from binding to port $PORT_NUMBER.
    ''')

    problem_description = _('''
    SELinux has denied the $SOURCE from binding to a network port $PORT_NUMBER which does not have an SELinux type associated with it.
    If $SOURCE should be allowed to listen on $PORT_NUMBER, use the <i>semanage</i> command to assign $PORT_NUMBER to a port type that $SOURCE_TYPE can bind to (%s). 
    <br><br>If $SOURCE is not supposed
    to bind to $PORT_NUMBER, this could signal an intrusion attempt.
    ''')

    fix_description = _('''
    If you want to allow $SOURCE to bind to port $PORT_NUMBER, you can execute <br>
    <b># semanage port -a -t PORT_TYPE -p %s $PORT_NUMBER</b>
    <br>where PORT_TYPE is one of the following: %s.

    <br><br>If this system is running as an NIS Client, turning on the allow_ypbind boolean may fix the problem.  setsebool -P allow_ypbind=1.
    ''')

    fix_cmd = ''
    
    def __init__(self):
        Plugin.__init__(self, __name__)
        self.set_priority(55)

    def analyze(self, avc):
        if avc.matches_target_types(['reserved_port_t', 'port_t']) and \
                avc.has_any_access_in(['name_bind']):
                # MATCH
            target_types = ", ".join(avc.allowed_target_types())
            problem_description = self.problem_description % target_types
            fix_description = self.fix_description % (avc.tclass.split("_")[0], target_types)
            return self.report(avc, _("Network Ports"),
                               self.summary, problem_description,
                               fix_description, self.fix_cmd)

        return None

