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
    SELinux is preventing the nfs daemon from allowing clients to write to public directories.
    ''')

    problem_description = _('''
    SELinux has preventing the nfs daemon (nfsd) from writing to
    directories marked as public. Usually these directories are
    shared between multiple network daemons, like nfs, apache, ftp
    etc.  If you have not exported any public file systems for
    writing, this could signal an intrusion.
    ''')

    fix_description = _('''
    If you want to export a public file systems using nfs you need to
    turn on the $BOOLEAN boolean: "setsebool -P
    $BOOLEAN=1".
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'

    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['nfsd_t'])                                   and \
           avc.matches_target_types(['public_content_t', 'public_content_rw_t'])  and \
           avc.all_accesses_are_in(avc.create_file_access):
            # MATCH
            avc.set_template_substitutions(BOOLEAN="allow_nfsd_anon_write")
            return self.report(avc, _("File System"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd,
                               level="green")
        return None

