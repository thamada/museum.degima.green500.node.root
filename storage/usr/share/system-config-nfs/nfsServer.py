## nfsServer.py - Code for dealing with the NFS server in system-config-nfs
## Copyright (C) 2005, 2009 Red Hat, Inc.
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

import nfsServerSettings
import nfsExports

class InstantiateError (Exception):
    pass

class nfsServer:
    instantiated = False
    
    def __init__ (self):
        if nfsServer.instantiated:
            raise InstantiateError ("this class can't be instantiated more than one time")
        nfsServer.instantiated = True
        self.settings = nfsServerSettings.nfsServerSettings ()
        self.exports = nfsExports.nfsExports ()
    
    def __del__ (self):
        nfsServer.instantiated = False

    def startNfs (self):
        if os.system ("/sbin/chkconfig portmap") == 0:
            os.system('/sbin/service portmap restart > /dev/null')
        else:
            os.system('/sbin/service rpcbind restart > /dev/null')
        os.system('/sbin/service nfs restart > /dev/null')

    def exportFs (self):
        os.system('/usr/sbin/exportfs -r')
