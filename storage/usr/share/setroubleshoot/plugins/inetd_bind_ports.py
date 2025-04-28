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
    If $SOURCE is supposed to be allowed to listen on this port, you can use the semanage command to add this port to a inetd_child_port_t type.   If you think this is the default please file a bug report against the selinux-policy package.
If $SOURCE is not supposed
    to bind to this port, this could signal an intrusion attempt.
    ''')

    fix_description = _('''
    If you want to allow $SOURCE to bind to this port
    semanage port -a -t inetd_child_port_t -p PROTOCOL $PORT_NUMBER
    Where PROTOCOL is tcp or udp.
    ''')

    fix_cmd = ''
    
    def __init__(self):
        Plugin.__init__(self, __name__)
        self.set_priority(53)

    def analyze(self, avc):
        if avc.matches_source_types(['inetd_t'])                    and \
           avc.matches_target_types(['reserved_port_t', 'port_t'])  and \
           avc.has_any_access_in(['name_bind']):
            # MATCH
            return self.report(avc, _("Network Ports"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd)

        return None
