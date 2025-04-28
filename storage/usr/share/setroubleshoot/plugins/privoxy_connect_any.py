#
# Copyright (C) 2009 Red Hat, Inc.
#
# Authors: Miroslav Grepl <mgrepl@redhat.com>
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
    SELinux is preventing the privoxy daemon from connecting to network port $PORT_NUMBER''')

    problem_description = _('''
    SELinux has denied the privoxy daemon from connecting to network port
    $PORT_NUMBER. By default privoxy policy is setup to deny privoxy
    connections. If you did not setup privoxy to network connections,
    this could signal a intrusion attempt.
    ''')

    fix_description = _('''
    If you want privoxy to connect to network ports you need to turn on
    the $BOOLEAN boolean: "setsebool -P $BOOLEAN=1"
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'

    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['privoxy_t']) and \
           avc.has_any_access_in(['name_connect']):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="privoxy_connect_any")
            return self.report(avc, _("Networking"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd,
                               level="green")

        return None
