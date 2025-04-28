# Copyright 2007  Red Hat, Inc.
#
# Lingning Zhang <lizhang@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 only
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import yum.Errors

class GuiError(yum.Errors.YumBaseError):
    def __init__(self, *args):
        yum.Errors.YumBaseError.__init__(self)
        self.args = args     

class RepoErrors(yum.Errors.YumBaseError):
    def __init__(self, *args):
        yum.Errors.YumBaseError.__init__(self)
        self.args = args    

GuiVerifyError = GuiDependencyError = GuiDownloadError = GuiError

