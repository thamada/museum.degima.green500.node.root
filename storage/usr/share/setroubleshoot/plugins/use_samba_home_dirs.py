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
    SELinux prevented $SOURCE from $ACCESS files stored on a Windows SMB/CIFS (Samba) filesytem.
    ''')
    
    problem_description = _('''
    SELinux prevented $SOURCE from $ACCESS files stored on a Windows SMB/CIFS (Samba) filesystem.
    CIFS is a network filesystem commonly used on Windows systems.
    
    $SOURCE attempted to read one or more files or directories from
    a mounted filesystem of this type.  As CIFS filesystems do not support
    fine-grained SELinux labeling, all files and directories in the
    filesystem will have the same security context.
    
    If you have not configured $SOURCE to read files from a CIFS filesystem
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
        if avc.matches_target_types(['cifs_t']) and \
           avc.has_tclass_in(['file', 'dir']):
            if avc.all_accesses_are_in(avc.r_file_perms + avc.r_dir_perms):
                # MATCH
                avc.set_template_substitutions(BOOLEAN="use_samba_home_dirs", ACCESS="reading")
                return self.report(avc, _("SAMBA"),
                                   self.summary, self.problem_description,
                                   self.fix_description, self.fix_cmd)
            elif avc.all_accesses_are_in(avc.create_file_perms + avc.rw_dir_perms):
                # MATCH
                avc.set_template_substitutions(BOOLEAN="use_samba_home_dirs", ACCESS="reading and writing")
                return self.report(avc, _("SAMBA"),
                                   self.summary, self.problem_description,
                                   self.fix_description, self.fix_cmd)
            else:
                # MATCH
                avc.set_template_substitutions(BOOLEAN="use_samba_home_dirs")
                return self.report(avc, _("SAMBA"),
                                   self.summary, self.problem_description,
                                   self.fix_description, self.fix_cmd,
                                   level="green")
        return None
