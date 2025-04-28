# -*- coding: utf-8 -*-
#
# preferences.py - handle application preferences in system-config-users
# Copyright © 2006 - 2007 Red Hat, Inc.
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# Authors:
# Nils Philippsen <nils@redhat.com>

class Preferences:
    defaults = {
        'FILTER': True,
        'ASSIGN_HIGHEST_UID': True,
        'ASSIGN_HIGHEST_GID': True,
        'PREFER_SAME_UID_GID': True
    }
    
    descriptions = {
        'FILTER': 'Filter out system users',
        'ASSIGN_HIGHEST_UID': 'Automatically assign highest UID for new users',
        'ASSIGN_HIGHEST_GID': 'Automatically assign highest GID for new groups',
        'PREFER_SAME_UID_GID': 'Prefer to have same UID and GID for new users'
    }
    
    def __init__ (self, filename = '/etc/sysconfig/system-config-users'):
        self.preferences = self.defaults.copy ()
        self.filename = filename
        self.configFile = None

    def __getitem__ (self, item):
        return self.preferences[item]

    def __setitem__ (self, item, value):
        if not self.has_key (item):
            raise KeyError
        self.preferences[item] = value

    def __delitem__ (self, item):
        self.preferences[item] = self.defaults[item]

    def keys (self):
        return self.defaults.keys ()

    def has_key (self, key):
        return self.defaults.has_key (key)

    def load (self):
        oldprefs = self.preferences
        self.preferences = self.defaults.copy ()

        try:
            fd = open (self.filename, 'r')
            configFile = fd.readlines ()
            fd.close ()

            linenr = 0
            for line in configFile:
                line = line.strip ()
                linenr += 1
                if line != '' and line.lstrip ()[0] != '#':
                    tokens = line.split ('=')
                    try:
                        key = tokens[0]
                        value = tokens[1]
                        if key in self.keys ():
                            if value.lower () == "true":
                                self.preferences[key] = True
                            else:
                                self.preferences[key] = False
                    except IndexError:
                        print '%s[%d]: Syntax error ("%s")' % (self.configFile, linenr, line.strip ())
            self.configFile = configFile
        except IOError:
            # no config file found, assume previous values
            self.preferences = oldprefs

    def save (self):
        found = []

        fd = open (self.filename, 'w')

        if self.configFile:
            for line in self.configFile:
                line_str = line.strip ()
                if line_str == '' or (len (line_str) and line_str[0] == '#'):
                    fd.write (line)
                else:
                    tokens = line_str.split ('=')
                    key = tokens[0].lstrip ()
                    if key in self.keys ():
                        found.append (key)
                        if self[key] == True:
                            fd.write ("%s=true\n" % (key))
                        else:
                            fd.write ("%s=false\n" % (key))

        else:
            # previously no configuration file, write standard header
            fd.write("# Configuration file for system-config-users\n")
            fd.write("\n")

        # write out defaults for non-set preferences
        for key in self.keys ():
            if key not in found:
                fd.write ("# %s\n" % self.descriptions[key])
                if self.defaults[key] == True:
                    fd.write ("%s=true\n" % (key))
                else:
                    fd.write ("%s=false\n" % (key))

        fd.close ()
