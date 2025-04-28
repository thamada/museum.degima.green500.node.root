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
    SELinux is preventing $SOURCE_PATH from using potentially mislabeled files $TARGET_PATH.
    ''')

    problem_description = _('''
    SELinux has denied the $SOURCE access to potentially
    mislabeled files $TARGET_PATH.  This means that SELinux will not
    allow httpd to use these files. If httpd should be allowed this access to these files you should change the file context to one of the following types, %s.
    Many third party apps install html files
    in directories that SELinux policy cannot predict.  These directories
    have to be labeled with a file context which httpd can access.
    ''')

    fix_description = _('''
    If you want to change the file context of $TARGET_PATH so that the httpd
    daemon can access it, you need to execute it using
    semanage fcontext -a -t FILE_TYPE '$FIX_TARGET_PATH'.  
    <br><br>where FILE_TYPE is one of the following: %s. 

You can look at the httpd_selinux man page for additional information.
    ''')

    def __init__(self):
        Plugin.__init__(self, __name__)
        self.set_priority(61)

    def analyze(self, avc):
        if avc.matches_source_types(['httpd_t', 'httpd_.*_script_t'])        and \
           not avc.matches_target_types(['.*_home_t', '.*_tmp_t', 'tmp_t'])  and \
           avc.has_tclass_in(['dir', 'file', 'lnk_file', 'sock_file']):
            # MATCH
            target_types = ", ".join(avc.allowed_target_types())
            problem_description = self.problem_description % target_types
            fix_description = self.fix_description % target_types
            return self.report(avc, _("File Label"),
                               self.summary, problem_description,
                               fix_description, self.fix_cmd)
        return None

