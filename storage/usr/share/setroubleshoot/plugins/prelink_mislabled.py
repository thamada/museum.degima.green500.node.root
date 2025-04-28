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

class plugin(Plugin):
    summary =_('''
    SELinux is preventing $SOURCE_PATH "$ACCESS" access to $TARGET_PATH.
    ''')

    problem_description = _('''
    SELinux denied prelink $ACCESS on $TARGET_PATH.
    The prelink program is only allowed to manipulate files that are identified as
    executables or shared libraries by SELinux.  Libraries that get placed in
    lib directories get labeled by default as a shared library.  Similarly,
    executables that get placed in a bin or sbin directory get labeled as executables by SELinux.  However, if these files get installed in other directories
    they might not get the correct label.  If prelink is trying
    to manipulate a file that is not a binary or share library this may indicate an
    intrusion attack.  

    ''')

    fix_description = _('''
    You can alter the file context by executing "chcon -t bin_t '$TARGET_PATH'" or
    "chcon -t lib_t '$TARGET_PATH'" if it is a shared library.  If you want to make these changes permanent you must execute the semanage command.
    "semanage fcontext -a -t bin_t '$FIX_TARGET_PATH'" or
    "semanage fcontext -a -t lib_t '$FIX_TARGET_PATH'".
    If you feel this executable/shared library is in the wrong location please file a bug against the package that includes the file.  If you feel that SELinux should know about this file and label it correctly please file a bug against SELinux policy.

    ''')

    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['prelink_t'])         and \
           avc.all_accesses_are_in(avc.create_file_perms)  and \
           avc.has_tclass_in(['file']):
            # MATCH
            return self.report(avc, _("File Label"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd)
        else:
            return None

