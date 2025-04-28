# -*- python -*-
# -*- coding: utf-8 -*-
## Copyright (C) 2001-2004 Red Hat, Inc.
## Copyright (C) 2001-2004 Harald Hoyer <harald@redhat.com>

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# Import all subpackages of our netconfpkg directory. This code is a real
# dirty hack but does the job(tm). It basically finds all .py files in the
# package directory and imports from all found files (except __init__.py that
# is) ;). Nice for plugin mechanism.
PRG_VERSION = "1.6.1"
PRG_NAME = "system-config-network"
PRG_AUTHORS = ["Harald Hoyer <harald@redhat.com>",
               "Than Ngo <than@redhat.com>",
               "Philipp Knirsch <pknirsch@redhat.com>",
               "Trond Eivind Glomsrød <teg@redhat.com>",
              ]
PRG_DOCUMENTERS = ["Tammy Fox <tfox@redhat.com>"]
