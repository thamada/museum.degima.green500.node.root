#
# Copyright (C) 2006, 2008 Red Hat, Inc.
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
    SELinux is preventing $SOURCE "$ACCESS" access to files with the default label, default_t.
    The default_t label is the default label for new directories created under the / directory.  No confined applications are allowed to access files labeled default_t.  This probably indicates a labeling problem, especially if the files being referred
    to  are not top level directories. Any files/directories under standard system directories, /usr,
    /var. /dev, /tmp, ..., should not be labeled with the default_t. If you create a new directory in / it will get this label.
    ''')
    
    fix_description = _('''
    If you created a directory in / and want $SOURCE to use these files you must tell SELinux about it by changing the labels.  Execute the following commands: <br>
    <b># semanage fcontext -t FILE_TYPE '$FIX_TARGET_PATH%s' </b>
    <br>where FILE_TYPE is one of the following: %s.
    <br><b># restorecon -v $TARGET_PATH</b>
    <br><br>If the $TARGET_PATH is not in / you probably need to relabel the system. Execute: 
    <br><b>"touch /.autorelabel; reboot"</b>
    ''')

    def __init__(self):
        Plugin.__init__(self,__name__)
        self.set_priority(60)

    def analyze(self, avc):
        if avc.matches_target_types(['default_t']):
            # MATCH
            target_types = ", ".join(avc.allowed_target_types())
            ext = '' 
	    if avc.tclass == "DIR":
                ext = '(/.*?)' 
            
            fix_description = self.fix_description % (ext, target_types)
	    
            return self.report(avc, _("File Label"),
                               self.summary, problem_description,
                               fix_description, self.fix_cmd)
        else:
            return None
