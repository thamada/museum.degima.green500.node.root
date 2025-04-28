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
    SELinux policy is preventing the samba daemon from writing to a public
    directory.
    ''')

    problem_description = _('''
    SELinux policy is preventing the samba daemon from writing to a public
    directory.  If samba is not setup to allow anonymous writes, this
    could signal an intrusion attempt.
    ''')

    fix_description = _('''
    If samba should be allowed to write to this directory you need to turn
    on the $BOOLEAN boolean and change the file context of
    the public directory to public_content_rw_t.  Read the samba_selinux
    man page for further information:
    "setsebool -P $BOOLEAN=1; chcon -t public_content_rw_t <path>"
    You must also change the default file context files on the system in order to preserve them even on a full relabel.  "semanage fcontext -a -t public_content_rw_t <path>"
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'
    
    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['smbd_t'])                                   and \
           avc.matches_target_types(['public_content_t', 'public_content_rw_t'])  and \
           avc.all_accesses_are_in(avc.create_file_perms):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="allow_smbd_anon_write")
            return self.report(avc, _("SAMBA"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd,
                               level="green")
        return None




