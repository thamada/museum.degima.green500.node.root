# @author Miroslav Grepl<mgrepl@redhat.com>
#
# Copyright (C) 2010 Red Hat, Inc.
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
import os 
from stat import *

import selinux
class plugin(Plugin):
    summary = _('''
    SELinux is preventing $SOURCE_PATH "$ACCESS" access to $TARGET_PATH.
    ''')

    problem_description = _('''
    SELinux denied access requested by $SOURCE_PATH. $SOURCE_PATH is
    mislabeled. $SOURCE_PATH default SELinux type is
    <B>$DEFAULT_CONTYPE</B>, but its current type is <B>$CURRENT_CONTYPE</B>. Changing
    this file back to the default type, may fix your problem.
    <p>
    If you believe this is a bug, please file a bug report against this package.
    ''')

    fix_description = _('''
    You can restore the default system context to this file by executing the
    restorecon command.  restorecon '$SOURCE_PATH'.
    ''')

    fix_cmd = "/sbin/restorecon '$SOURCE_PATH'"
   
    
    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if not avc.query_environment: return None
        try:
            if avc.spath is None \
                or not os.path.exists(avc.spath): return None
            default_con = selinux.matchpathcon(avc.spath, S_IFREG)[1]
            default_contype = default_con.split(":")[2]
            current_con = selinux.getfilecon(avc.spath)[1]
            current_contype = current_con.split(":")[2]
            if default_con != current_con:
                # MATCH
                avc.set_template_substitutions(DEFAULT_CONTYPE=default_contype, CURRENT_CONTYPE=current_contype)
                return self.report(avc, _("File Label"),
                                   self.summary, self.problem_description,
                                   self.fix_description, self.fix_cmd, level="yellow", fixable=True, button_text=_("Restore Context"))
        except:
            pass

        return None
