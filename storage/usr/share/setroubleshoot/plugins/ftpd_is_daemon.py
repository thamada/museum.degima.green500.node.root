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
    SELinux prevented $SOURCE from correctly running as a daemon.
    ''')

    problem_description = _('''
    SELinux prevented $SOURCE from correctly running as a daemon.
    FTP servers can be configured to either run through xinetd or as a
    stand-alone daemon. Each configuration requires slightly different
    access. If you have configured your FTP server to run as a daemon
    you should allow this access. Otherwise this may signal an intrusion
    attempt.
    ''')

    fix_description = _('''
    Changing the "$BOOLEAN" boolean to true will allow this access:
    "setsebool -P $BOOLEAN=1."
    ''')

    fix_cmd = 'setsebool -P $BOOLEAN=1'
    def __init__(self):
        Plugin.__init__(self, __name__)

    def analyze(self, avc):
        if avc.matches_source_types(['ftpd_t']):

            if (avc.matches_target_types(['ftpd_lock_t'])     and \
                avc.has_any_access_in(avc.create_file_perms)  and \
                avc.has_tclass_in(['file']))                      \
            or \
               (avc.matches_target_types(['var_t'])           and \
                avc.has_any_access_in(['search'])             and \
                avc.has_tclass_in(['dir']))                       \
            or \
               (avc.matches_target_types(['var_lock_t'])      and \
                avc.has_any_access_in(avc.rw_dir_perms)       and \
                avc.has_tclass_in(['dir']))                       \
            or \
               (avc.matches_target_types(['ftpd_t'])          and \
                avc.has_any_access_in(['net_bind_service'])):

                # MATCH
                avc.set_template_substitutions(BOOLEAN="ftp_is_daemon")
                return self.report(avc, _("FTP"),
                                   self.summary, self.problem_description,
                                   self.fix_description, self.fix_cmd)

        elif avc.matches_source_types(['inetd_t']):

            if (avc.matches_target_types(['ftpd_exec_t'])     and \
                avc.has_any_access_in(['getattr', 'execute']) and \
                avc.has_tclass_in(['file'])):

                # MATCH
                avc.set_template_substitutions(BOOLEAN="ftp_is_daemon")
                return self.report(avc, _("FTP"),
                                   self.summary, self.problem_description,
                                   self.fix_description, self.fix_cmd)
        return None
