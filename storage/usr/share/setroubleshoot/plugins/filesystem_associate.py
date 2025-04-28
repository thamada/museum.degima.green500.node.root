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
    SELinux is preventing $SOURCE_PATH from creating a file with a context of $SOURCE_TYPE on a filesystem.
    ''')

    problem_description = _('''
    SELinux is preventing $SOURCE from creating a file with a context of $SOURCE_TYPE on a filesystem.
    Usually this happens when you ask the cp command to maintain the context of a file when
    copying between file systems, "cp -a" for example.  Not all file contexts should be maintained
    between the file systems.  For example, a read-only file type like iso9660_t should not be placed
    on a r/w system.  "cp -P" might be a better solution, as this will adopt the default file context
    for the destination.  
    ''')

    fix_description = _('''
    Use a command like "cp -P" to preserve all permissions except SELinux context.
    ''')

    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_target_types(['.*fs_t'])    and \
           avc.all_accesses_are_in(['associate'])  and \
           avc.has_tclass_in(['filesystem']):
            # MATCH
            return self.report(avc, _("File Label"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd)
        else:
            return None

