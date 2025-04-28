#
# Authors: Karl MacMillan <kmacmillan@mentalrootkit.com>
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
    SELinux prevented $SOURCE from reading from the urandom device.
    ''')

    problem_description = _('''
    SELinux prevented $SOURCE from reading from the urandom device.
    This access should be allowed for individual applications, but there
    are situations where all applications require the access (for example,
    when ProPolice/SSP stack smashing protection is used).  Allowing this
    access may allow malicious applications to drain the kernel entropy
    pool. This can compromise the ability of some software that is
    dependent on high quality random numbers (e.g., ssh-keygen) to operate
    effectively. The risk of this type of attack is relatively low.
    ''')

    fix_description = _('''
    Changing the "$BOOLEAN" boolean to true will allow this access:
    "setsebool -P $BOOLEAN=1."
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'
    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_target_types(['urandom_device_t'])  and \
           avc.all_accesses_are_in(avc.r_file_perms)       and \
           avc.has_tclass_in(['chr_file']):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="global_ssp")
            return self.report(avc, None,
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd)
        return None
