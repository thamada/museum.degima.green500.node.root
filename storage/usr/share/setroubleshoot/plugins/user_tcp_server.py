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
    SELinux is preventing the users from running TCP servers in the usedomain.
        ''')

    problem_description = _('''
    SELinux has denied the $SOURCE program from binding to a network port $PORT_NUMBER which does not have an SELinux type associated with it.
    $SOURCE does not have an SELinux policy defined for it when run by the user, so it runs in the users domain.  SELinux is currently setup to
    deny TCP servers to run within the user domain. If you do not expect programs like $SOURCE to bind to a network port, then this could signal
    an intrusion attempt. If this system is running as an NIS Client, turning on the allow_ypbind boolean may fix the problem.
    setsebool -P allow_ypbind=1.
    ''')

    fix_description = _('''
    If you want to allow user  programs to run as TCP Servers, you can turn on the user_tcp_server boolean, by executing:
    setsebool -P $BOOLEAN=1
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'
    
    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['user_t', 'staff_t', 'sysadm_t'])  and \
           avc.matches_target_types(['port_t'])                         and \
           avc.has_any_access_in(['name_bind']):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="user_tcp_server")
            return self.report(avc, _("Network Ports"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd)

        return None

