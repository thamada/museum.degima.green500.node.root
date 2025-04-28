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

from setroubleshoot.util import *
from setroubleshoot.Plugin import Plugin
from setroubleshoot.log import *

class plugin(Plugin):
    summary =_('''
    SELinux is preventing $SOURCE_PATH from executing $TARGET_PATH.
    ''')

    problem_description = _('''
    SELinux has denied the $SOURCE from executing $TARGET_PATH.
    If $SOURCE is supposed to be able to execute $TARGET_PATH, this could be a labeling problem.  Most confined domains are allowed to execute files labeled bin_t.  So you could change the labeling on this file to bin_t and retry the application.  If this $SOURCE is not supposed to execute $TARGET_PATH, this could signal an intrusion attempt.   
    ''')

    fix_description = _('''
    If you want to allow $SOURCE to execute $TARGET_PATH:
    
    chcon -t bin_t '$TARGET_PATH'

    If this fix works, please update the file context on disk, with the following command:

    semanage fcontext -a -t bin_t '$FIX_TARGET_PATH'

    Please specify the full path to the executable, Please file a bug report
to make sure this becomes the default labeling.      
    ''')

    fix_cmd = ''
    
    def __init__(self):
        Plugin.__init__(self, __name__)
        self.set_priority(60)

    def analyze(self, avc):
        if avc.matches_target_types(['usr_t', 'etc_t', 'var_t', 'var_lib_t', 'default_t']) and \
           avc.all_accesses_are_in(['execute', 'execute_no_trans', 'transition']):
            # MATCH
            return self.report(avc, _("File Label"),
                               self.summary, self.problem_description,
                               self.fix_description, self.fix_cmd)
        return None





