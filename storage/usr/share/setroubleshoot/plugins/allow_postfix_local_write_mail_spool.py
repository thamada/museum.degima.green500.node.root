#
# Authors: Dan Walsh <dwalsh@redhat.com>
#
# Copyright (C) 2007 Red Hat, Inc.
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
    SELinux prevented $SOURCE from $ACCESS files stored mail spool directory.
    ''')
    
    problem_description = _('''
    SELinux prevented $SOURCE from $ACCESS files stored in the mail spool directory.
    
    $SOURCE attempted to write one or more files or directories, postfix
    ordinarily does not need this access.  However it can be setup to allow 
    this.    

    If you have not configured $SOURCE to write to the mail spool
    this access attempt could signal an intrusion attempt.
    ''')
    
    fix_description = _('''
    Changing the "$BOOLEAN" boolean to true will allow this access:
    "setsebool -P $BOOLEAN=1"
    ''')
    
    fix_cmd = 'setsebool -P $BOOLEAN=1'
    
    def __init__(self):
        Plugin.__init__(self, __name__)
        self.set_priority(75)

    def analyze(self, avc):
        if avc.matches_source_types(['postfix_local_t']) and \
           avc.matches_target_types(['mail_spool_t'])    and \
           avc.has_any_access_in(['write'])              and \
           avc.has_tclass_in(['file','dir']):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="allow_postfix_local_write_mail_spool",
                                           ACCESS="writing")
            return self.report(avc, _("Mail"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd,
                               level="green")
        else:
            return None
