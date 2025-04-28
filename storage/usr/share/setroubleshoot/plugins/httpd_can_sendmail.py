#
# Copyright (C) 2006,2009 Red Hat, Inc.
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
import re

class plugin(Plugin):
    summary =_('''
    SELinux is preventing the http daemon from sending mail.
    ''')

    problem_description = _('''
    SELinux has denied the http daemon from sending mail. An
    httpd script is trying to connect to a mail port or execute the 
    sendmail command. If you did not setup httpd to sendmail, this could 
    signal a intrusion attempt.
    ''')

    fix_description = _('''
    If you want httpd to send mail you need to turn on the
    $BOOLEAN boolean: "setsebool -P
    $BOOLEAN=1"
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'
    
    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['httpd_t', 'httpd_sys_script_t']):
            if (avc.matches_target_types(['mail_port_t', 'pop_port_t'])  and \
                    avc.has_any_access_in(['name_connect'])) or \
                    re.search('sendmail', avc.source):
                # MATCH
                avc.set_template_substitutions(BOOLEAN="httpd_can_sendmail")
                return self.report(avc, _("Web Server"),
                                   self.summary, self.problem_description,
                                   self.fix_description, self.fix_cmd,
                                   level="green")

        return None
