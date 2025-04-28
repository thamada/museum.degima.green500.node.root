#
# Authors: Dan Walsh <dwalsh@redhat.com>
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
    SELinux prevented $SOURCE from writing $TARGET_PATH.
    ''')

    problem_description = _('''
    SELinux prevented $SOURCE from writing $TARGET_PATH. 
    If $TARGET_PATH is a core file, you may want to allow this.  If $TARGET_PATH is not a core file, this could signal an intrusion attempt.
    ''')

    fix_description = _('''
    Changing the "$BOOLEAN" boolean to true will allow this access:
    "setsebool -P $BOOLEAN=1."
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'
    
    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_target_types(['root_t'])          and \
           avc.has_any_access_in(['add_name', 'create']) and \
           avc.has_tclass_in(['dir']):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="allow_daemons_dump_core")
            return self.report(avc, None,
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd)
        else:
            return None
