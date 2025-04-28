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

relay_ports = ['gopher_port_t', 'ftp_port_t', 'http_port_t', 'http_cache_port_t']

class plugin(Plugin):
    summary =_('''
    SELinux is preventing the http daemon from connecting to itself or the relay ports
    ''')

    problem_description = _('''
    SELinux has denied the http daemon from connecting to itself or
    the relay ports. An httpd script is trying to make a network connection 
    to an http/ftp port. If you did not setup httpd to make network
    connections, this could signal an intrusion attempt.
    ''')

    fix_description = _('''
    If you want httpd to connect to httpd/ftp ports you need to turn
    on the $BOOLEAN boolean: "setsebool -P
    $BOOLEAN=1"
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'
    
    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['httpd_t', 'httpd_sys_script_t']) and \
           avc.matches_target_types(relay_ports)                       and \
           avc.has_any_access_in(['name_connect']):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="httpd_can_network_relay")
            return self.report(avc, _("Web Server"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd,
                               level="green")

        return None




