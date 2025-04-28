## nfsServerSettings.py - Code for dealing with /etc/sysconfig/nfs
##                        in system-config-nfs
## Copyright (C) 2005, 2008, 2009 Red Hat, Inc.
## Copyright (C) 2005 Nils Philippsen <nils@redhat.com>

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

## Authors:
## Nils Philippsen <nils@redhat.com>

import os
import re

class varNotKnown (Exception):
    pass

class varValueFound (Exception):
    pass

class nfsServerSettings:
    filename = '/etc/sysconfig/nfs'
    knownvars = ['LOCKD_TCPPORT', 'LOCKD_UDPPORT', 'MOUNTD_PORT', 'STATD_PORT', 'RQUOTAD_PORT']
    name_value_re = re.compile ('^(?P<varname>[A-Za-z_][A-Za-z0-9_]*)=(?P<varvalue>.*)$')

    def __init__ (self):
        self.read ()

    def read (self):
        self.lines = []

        try:
            f = open (self.filename, 'r')
            if f:
                line = None
                while True:
                    
                    line = f.readline ()
                    if line == '':
                        break
                    line = line.strip ()
                    try:
                        m = self.name_value_re.match (line)
                        if m:
                            varname = m.group ('varname')
                            varvalue = m.group ('varvalue')
                            if varname in self.knownvars:
                                self.lines.append ([varname, varvalue])
                                raise varValueFound ()
                        self.lines.append (line)
                    except varValueFound:
                        pass
                f.close ()
        except IOError:
            pass

    def __str__ (self):
        s = ''
        for line in self.lines:
            if isinstance (line, str):
                s += line + '\n'
            elif isinstance (line, list):
                s += "%s=%s\n" % (line[0], line[1])
            else:
                raise Exception ()
        return s

    def write (self):
        if os.access (self.filename, os.F_OK):
            os.rename (self.filename, self.filename + ".bak")
        else:
            if len (str (self)) == 0:
                # no need to write
                return

        f = open (self.filename, "w")
        f.write (str (self))
        f.close ()

    def set (self, name, value):
        found = False
        if name not in self.knownvars:
            raise varNotKnown (name)
        for line in self.lines:
            if isinstance (line, list):
                if line[0] == name:
                    line[1] = value
                    found = True
                    break
        if not found:
            self.lines.append ([name, value])

    def get (self, name):
        if name not in self.knownvars:
            raise varNotKnown (name)
        for line in self.lines:
            if isinstance (line, list):
                if line[0] == name:
                    return line[1]
        return None

    def unset (self, name):
        if name not in self.knownvars:
            raise varNotKnown (name)
        for i in range (len (self.lines)):
            if isinstance (self.lines[i], list):
                if self.lines[i][0] == name:
                    del (self.lines[i])
                    break
