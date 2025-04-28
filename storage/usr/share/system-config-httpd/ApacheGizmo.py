#!/usr/bin/python -i

## ui-setup - A Python Apache configuration utility for:
## Copyright (C) 2000 Red Hat, Inc.
## Copyright (C) 2000 Jonathan Blandford <jrb@redhat.com>,
##                    Philipp Knirsch   <pknirsch@redhat.com>

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


## Thoughts on rewriting the gizmo
## doesn't actually work.
## I don't really know how the proxy elements are going to work yet.  But it should be fairly straightforward.


import sys
import signal
import copy
import string
import re

from UserList import UserList

import ApacheBase

##
## I18N
##
import gettext
gettext.bindtextdomain ("system-config-httpd", "/usr/share/locale")
gettext.textdomain ("system-config-httpd")
_=gettext.gettext

class TestError(Exception):
    pass

##
## StateStack
class StateStack (UserList):
    def __init__ (self, base):
        UserList.__init__(self)
        self.apache = base

    def push_state (self):
        # Save original state of current config state
        orig_ctx          = ApacheBase.ctx
        orig_dr           = ApacheBase.dr
        orig_apachebase   = ApacheBase.apachebase
        orig_apache       = self.apache

        # Create a working copy of the current config state
        ApacheBase.ctx    = orig_ctx.copy()
        ApacheBase.dr     = ApacheBase.ctx.getDataRoot().getChildByIndex(0)
        ApacheBase.apachebase = ApacheBase.apache(ApacheBase.dr, None)
        self.apache = Apache()

        # Append original state to our internal list.
        self.append ( (orig_ctx, orig_dr, orig_apachebase, orig_apache ))

    def pop_restore (self):
        # Get the last known state from our internal list.
        (orig_ctx, orig_dr, orig_apachebase, orig_apache) = self[len (self) - 1]

        # Restore the affected variables
        ApacheBase.ctx = orig_ctx
        ApacheBase.dr = orig_dr
        ApacheBase.apachebase = orig_apachebase
        self.apache = orig_apache

        # Remove the currently now active state from the list
        self.pop ()

##
## Directory
class Directory:
    ALL_HOSTS=1
    DENY_FIRST=2
    ALLOW_FIRST=3

    DENY_ALLOW='Deny,Allow'
    ALLOW_DENY='Allow,Deny'
    FROM_ALL='all'
    def __init__ (self, directory):
        self.__directory = directory

    def __cmp__ (self, dir2):
        return self.Dir == dir2


    def __getattr__ (self, attr):
        if attr[0] == '_':
            return self.__dict__[attr]

        if Directory.__dict__.has_key ("get"+attr):
            return apply (Directory.__dict__["get"+attr], (self, ))

        if ApacheBase.directory.__dict__.has_key ("get"+attr):
            return apply (ApacheBase.directory.__dict__["get"+attr], (self.__directory, ))

        raise AttributeError, attr


    def __setattr__ (self, attr, value):
        if attr[0] == '_':
            self.__dict__[attr] = value
            return

        self.test_attr (attr, value)

        if Directory.__dict__.has_key ("set"+attr):
            apply (Directory.__dict__["set"+attr], (self, value))
            return

        if ApacheBase.directory.__dict__.has_key ("set"+attr):
            apply (ApacheBase.directory.__dict__["set"+attr], (self.__directory, value))
            return

        raise AttributeError, attr

    def setMode (self, value):
        if value == Directory.ALL_HOSTS:
            self.__directory.delOrder ()
            self.__directory.delDeny ()
            self.__directory.delAllow ()
        elif value == Directory.DENY_FIRST:
            self.__directory.setOrder (Directory.DENY_ALLOW)
        elif value == Directory.ALLOW_FIRST:
            self.__directory.setOrder (Directory.ALLOW_DENY)
        else:
            raise ValueError

    def getMode (self):
        order = self.__directory.getOrder ()
        if order == Directory.ALLOW_DENY:
            return Directory.ALLOW_FIRST
        elif order == Directory.DENY_ALLOW:
            return Directory.DENY_FIRST
        return Directory.ALL_HOSTS

    def setOptions (self, value):
        str = apply (VirtualHost.__dict__['_option_list_to_string'], (None, value))
        self.__directory.setOptions (str)

    def getOptions (self):
        options = self.__directory.getOptions ()
        return apply (VirtualHost.__dict__['_option_string_to_list'], (None, options))

    def testDeny (self, str):
        if str == "" or str == None:
            raise TestError, _("Directory Deny list cannot be empty.")

    def testAllow (self, str):
        if str == "" or str == None:
            raise TestError, _("Directory Allow list cannot be empty.")

    def testDir (self, dir):
        if dir == "" or dir == None:
            raise TestError, _("You must include a directory name.")
        if dir[0] != '/':
            raise TestError, _("Only absolute directories are allowed.")

        if self.__directory.getDir () == dir:
            return
        directories = self.__directory.getParent ()

        for i in xrange (directories.getNumdirectory ()):
            if directories.getdirectory (i).getDir () == dir:
                raise TestError, (_("A directory named %s already exists.") % dir)

    def test_attr (self, attr, value):
        if attr == '_attr' or attr == '_set':
            #stop people from being cute
            raise ValueError
        if Directory.__dict__.has_key ('test' + attr):
            apply (Directory.__dict__['test' + attr], (self, value))



##
## VirtualHost
class VirtualHost:
    HOST_TYPE_IP='ip'
    HOST_TYPE_NAME='name'
    HOST_TYPE_DEFAULT='default'

    DEFAULT='_default_'

    SSL_LOG_LEVELS = ['none', 'error', 'warn', 'info', 'trace','debug']
    LOG_LEVELS = ['emerg', 'alert', 'crit', 'error', 'warn', 'notice', 'info', 'debug' ]

    SERVER_SIGNATURE_OFF='off'
    SERVER_SIGNATURE_ON='on'
    SERVER_SIGNATURE_EMAIL='email'

    SERVER_HOST_NAME_LOOKUP_OFF='off'
    SERVER_HOST_NAME_LOOKUP_ON='on'
    SERVER_HOST_NAME_LOOKUP_DOUBLE='double'

    DIRECTORY_OPTIONS = [ "ExecCGI", "FollowSymLinks", "Includes", "IncludesNOEXEC", "Indexes", "MultiViews", "SymLinksIfOwnerMatch" ]
    SSL_OPTIONS = [ "FakeBasicAuth", "ExportCertData", "CompatEnvVars", "StrictRequire", "OptRenegotiate" ]

    def __init__ (self, vhost):
        self.__vhost = vhost
        self.__dict__['directories'] = Directories (vhost)
        self.__dict__['ErrorDocuments'] = ErrorDocuments (vhost)

    def __getattr__ (self, attr):
        if attr[0] == '_':
            return self.__dict__[attr]

        if VirtualHost.__dict__.has_key ("get"+attr):
            return apply (VirtualHost.__dict__["get"+attr], (self, ))

        retval = None
        if ApacheBase.virtualhost.__dict__.has_key ("get"+attr):
            retval = apply (ApacheBase.virtualhost.__dict__["get"+attr], (self.__vhost, ))

        if retval != None:
            return retval

        vhostdefault = ApacheBase.apachebase.getvhostdefault ()
        if ApacheBase.vhostdefault.__dict__.has_key ("get"+attr):
            return apply (ApacheBase.vhostdefault.__dict__["get"+attr], (vhostdefault, ))

        raise AttributeError, attr


    def __setattr__ (self, attr, value):
        if attr[0] == '_':
            self.__dict__[attr] = value
            return

        if VirtualHost.__dict__.has_key ("set"+attr):
            apply (VirtualHost.__dict__["set"+attr], (self, value))
            return

        vhostdefault = ApacheBase.apachebase.getvhostdefault ()

        if value == None:
            if ApacheBase.virtualhost.__dict__.has_key ("del"+attr):
                apply (ApacheBase.virtualhost.__dict__["del"+attr], (self.__vhost, ))
                return
            else:
                raise AttributeError, attr

        self.test_attr (attr, value)

        def_val = None
        if ApacheBase.vhostdefault.__dict__.has_key ("get"+attr):
            def_val = apply (ApacheBase.vhostdefault.__dict__["get"+attr], (vhostdefault, ))

        if ApacheBase.virtualhost.__dict__.has_key ("set"+attr):
            apply (ApacheBase.virtualhost.__dict__["set"+attr], (self.__vhost, value))
        else:
            raise AttributeError, attr

    def getAliases (self):
        aliases = self.__vhost.getserveraliases ()
        if aliases == None:
            return []

        retval = []
        for i in xrange (aliases.getNumServerAlias ()):
            retval.append (aliases.getServerAlias (i))
        return retval

    def setAliases (self, value):
        self.__vhost.delserveraliases ()
        aliases = None
        for alias in value:
            if aliases == None:
                aliases = self.__vhost.createserveraliases ()
            i = aliases.addServerAlias ()
            aliases.setServerAlias (i, alias)

    def setVHName (self, value):
        if self.VHName == value:
            return

        virtualhosts = ApacheBase.apachebase.getvirtualhosts ()
        for i in xrange (virtualhosts.getNumvirtualhost ()):
            if virtualhosts.getvirtualhost (i).getVHName() == value:
                raise TestError, _("A virtual host named \"%s\" already exists.\nPlease use a different name for this virtual host.") % value
        apply (ApacheBase.virtualhost.__dict__["setVHName"], (self.__vhost, value))

    def getErrorDocuments (self):
        docs = self.__vhost.geterrordocuments ()
        return {}

    def setErrorDocuments (self):
        pass

    def _option_string_to_list (self, options):
        if options == None or options == "":
            return []
        if string.lower (options) == Apache.ALL:
            return [ "ExecCGI", "FollowSymLinks", "Includes", "IncludesNOEXEC", "Indexes", "SymLinksIfOwnerMatch" ]
        tmpdict = {}
        list = string.split (options)
        for opt in list:
            if opt in VirtualHost.DIRECTORY_OPTIONS:
                tmpdict[opt] = None
        retval = tmpdict.keys ()
        retval.sort ()
        return retval

    def _option_list_to_string (self, list):
        # remove all values/non-options
        tmpdict = {}
        for opt in list:
            if opt in VirtualHost.DIRECTORY_OPTIONS:
                tmpdict[opt] = None
        newlist = tmpdict.keys ()
        newlist.sort ()
        if len (newlist) == len (VirtualHost.DIRECTORY_OPTIONS)-1 and "MultiViews" not in newlist:
            return Apache.ALL
        first = True
        retval = ""
        for i in newlist:
            if first:
                retval = i
                first = False
            else:
                retval = retval + " " + i
        return retval

    def setOptions (self, value):
        vhostdefault = ApacheBase.apachebase.getvhostdefault ()
        str = self._option_list_to_string (value)
        if string.lower (str) == string.lower (vhostdefault.getOptions ()):
            self.__vhost.delOptions ()
            return
        self.__vhost.setOptions (str)

    def getOptions (self):
        options = self.__vhost.getOptions ()
        if options == None:
            vhostdefault = ApacheBase.apachebase.getvhostdefault ()
            options = vhostdefault.getOptions ()
        return self._option_string_to_list (options)

    def setNameBased (self, value):
        if value == VirtualHost.HOST_TYPE_IP:
            self.__vhost.delserveraliases ()
        elif value == VirtualHost.HOST_TYPE_NAME:
            pass
        else:
            self.__vhost.delserveraliases ()
            self.__vhost.delAddress ()
        self.__vhost.setNameBased (value)

    def testServerName (self, value):
        if self.__vhost.getNameBased () == VirtualHost.HOST_TYPE_DEFAULT:
            if value == None or value == "":
                raise TestError, _("The server name must be set.")
            if value == '_default_':
                return
            if value[:9] != '_default_':
                raise TestError, _("Default virtual hosts must have Server Name of _default_ or _default_:port")
            if not re.match ('_default_:[0-9]+', value):
                raise TestError, _("Ports must only contain numeric characters")

    def getSetEnv (self):
        environment = self.__vhost.getenvironment ()
        retval = stack.apache.default_vhost.SetEnv

        if environment != None:
            for i in xrange (environment.getNumenv ()):
                env = environment.getenv (i)
                if env.getEnvType () != 'set':
                    continue

                retval[env.getVar ()] = env.getValue ()

        return retval

    def setSetEnv (self, value):
        environment = self.__vhost.getenvironment ()

        if environment == None:
            environment = self.__vhost.createenvironment ()


        for i in xrange (environment.getNumenv () - 1, -1, -1):
            env = environment.getenv (i)
            if env.getEnvType () == 'set':
                env = None
                environment.delenv(i)

        default_value = stack.apache.default_vhost.SetEnv
        for var in value.keys ():
            if var in default_value.keys() and default_value[var] == value[var]:
                continue
            env = environment.addenv ()
            env.setEnvType ('set')
            env.setVar (var)
            env.setValue (value[var])

    def getPassEnv (self):
        environment = self.__vhost.getenvironment ()
        retval = stack.apache.default_vhost.PassEnv

        if environment != None:
            for i in xrange (environment.getNumenv ()):
                env = environment.getenv (i)
                if env.getEnvType () != 'pass':
                    continue

                retval.append (env.getVar ())

        return retval

    def setPassEnv (self, value):
        environment = self.__vhost.getenvironment ()

        if environment == None:
            environment = self.__vhost.createenvironment ()


        for i in xrange (environment.getNumenv () - 1, -1, -1):
            env = environment.getenv (i)
            if env.getEnvType () == 'pass':
                env = None
                environment.delenv(i)

        default_value = stack.apache.default_vhost.PassEnv
        for var in value:
            if var in default_value:
                continue
            env = environment.addenv ()
            env.setEnvType ('pass')
            env.setVar (var)

    def getUnsetEnv (self):
        environment = self.__vhost.getenvironment ()
        retval = stack.apache.default_vhost.UnsetEnv

        if environment != None:
            for i in xrange (environment.getNumenv ()):
                env = environment.getenv (i)
                if env.getEnvType () != 'unset':
                    continue

                retval.append (env.getVar ())

        return retval

    def setUnsetEnv (self, value):
        environment = self.__vhost.getenvironment ()

        if environment == None:
            environment = self.__vhost.createenvironment ()

        for i in xrange (environment.getNumenv () - 1, -1, -1):
            env = environment.getenv (i)
            if env.getEnvType () == 'unset':
                env = None
                environment.delenv(i)

        default_value = stack.apache.default_vhost.UnsetEnv
        for var in value:
            if var in default_value:
                continue
            env = environment.addenv ()
            env.setEnvType ('unset')
            env.setVar (var)

    def testSSLCACertificateFile (self, value):
        if value == None or value == "":
            raise TestError, _("Empty Certificate Authority are not allowed")
        if value[0] != '/':
            raise TestError, _("Only absolute Certificate Authorities are allowed")
        if value[-1] == '/':
            raise TestError, _("Only Certificate Authority Files are allowed, not directories")

    def testOptions (self, value):
        for opt in value:
            if opt not in VirtualHost.DIRECTORY_OPTIONS:
                raise TestError, _("%s is not a valid Option") % opt

    def test_attr (self, attr, value):
        if attr == '_attr' or attr == '_set':
            #stop people from being cute
            raise ValueError
        if VirtualHost.__dict__.has_key ('test' + attr):
            apply (VirtualHost.__dict__['test' + attr], (self, value))

    def get_readable_address (self):
        if self.NameBased == VirtualHost.HOST_TYPE_IP:
            return self.Address
        elif self.NameBased == VirtualHost.HOST_TYPE_NAME:
            return (_("%s on %s") % (self.ServerName, self.Address))
        if self.ServerName == '_default_':
            return _("Default virtual host")
        return (_("Default virtual host on port %s") % self.ServerName[10:])


##
## DefaultVirtualHost
class DefaultVirtualHost (VirtualHost):

    def __init__ (self):
        self.__vhost = ApacheBase.apachebase.getvhostdefault ()
        self.__dict__['directories'] = Directories (self.__vhost)
        self.__dict__['ErrorDocuments'] = DefaultErrorDocuments (self.__vhost)

    def __getattr__ (self, attr):
        if attr[0] == '_':
            return self.__dict__[attr]

        if DefaultVirtualHost.__dict__.has_key ("get"+attr):
            return apply (DefaultVirtualHost.__dict__["get"+attr], (self, ))

        if ApacheBase.vhostdefault.__dict__.has_key ("get"+attr):
            return apply (ApacheBase.vhostdefault.__dict__["get"+attr], (self.__vhost, ))

        raise AttributeError, attr


    def __setattr__ (self, attr, value):
        if attr[0] == '_':
            self.__dict__[attr] = value
            return

        self.test_attr (attr, value)

        if DefaultVirtualHost.__dict__.has_key ("set"+attr):
            apply (DefaultVirtualHost.__dict__["set"+attr], (self, value))
            return

        if ApacheBase.vhostdefault.__dict__.has_key ("set"+attr):
            apply (ApacheBase.vhostdefault.__dict__["set"+attr], (self.__vhost, value))
        else:
            raise AttributeError, attr

    def getErrorDocuments (self):
        docs = self.__vhost.geterrordocuments ()
        return {}

    def setErrorDocuments (self):
        pass

    def getSetEnv (self):
        environment = self.__vhost.getenvironment ()

        retval = {}

        if environment != None:
            for i in xrange (environment.getNumenv ()):
                env = environment.getenv (i)
                if env.getEnvType () != 'set':
                    continue

                retval[env.getVar ()] = env.getValue ()

        return retval

    def setSetEnv (self, value):
        environment = self.__vhost.getenvironment ()

        if environment == None:
            environment = self.__vhost.createenvironment ()

        for i in xrange (environment.getNumenv () - 1, -1, -1):
            env = environment.getenv (i)
            if env.getEnvType () == 'set':
                env = None
                environment.delenv(i)

        for var in value.keys ():
            env = environment.addenv ()
            env.setEnvType ('set')
            env.setVar (var)
            env.setValue (value[var])

    def getPassEnv (self):
        environment = self.__vhost.getenvironment ()

        if environment == None:
            return []

        retval = []
        for i in xrange (environment.getNumenv ()):
            env = environment.getenv (i)
            if env.getEnvType () != 'pass':
                continue

            retval.append (env.getVar ())

        return retval

    def setPassEnv (self, value):
        environment = self.__vhost.getenvironment ()

        if environment == None:
            environment = self.__vhost.createenvironment ()

        for i in xrange (environment.getNumenv () - 1, -1, -1):
            env = environment.getenv (i)
            if env.getEnvType () == 'pass':
                env = None
                environment.delenv(i)

        for var in value:
            env = environment.addenv ()
            env.setEnvType ('pass')
            env.setVar (var)

    def getUnsetEnv (self):
        environment = self.__vhost.getenvironment ()

        if environment == None:
            return []

        retval = []
        for i in xrange (environment.getNumenv ()):
            env = environment.getenv (i)
            if env.getEnvType () != 'unset':
                continue

            retval.append (env.getVar ())

        return retval

    def setUnsetEnv (self, value):
        environment = self.__vhost.getenvironment ()

        if environment == None:
            environment = self.__vhost.createenvironment ()

        for i in xrange (environment.getNumenv () - 1, -1, -1):
            env = environment.getenv (i)
            if env.getEnvType () == 'unset':
                env = None
                environment.delenv(i)

        for var in value:
            env = environment.addenv ()
            env.setEnvType ('unset')
            env.setVar (var)

    def setOptions (self, value):
        str = self._option_list_to_string (value)
        self.__vhost.setOptions (str)

    def getOptions (self):
        options = self.__vhost.getOptions ()
        return self._option_string_to_list (options)


    def setSSLCACertificate (self, value):
        if value[-1] == '/':
            self.__vhost.setSSLCACertificatePath (value)
            self.__vhost.delSSLCACertificateFile ()
        else:
            self.__vhost.setSSLCACertificateFile (value)
            self.__vhost.delSSLCACertificatePath ()

    def getSSLCACertificate (self):
        retval = self.__vhost.getSSLCACertificateFile ()
        if retval:
            return retval
        retval = self.__vhost.getSSLCACertificatePath ()


##
## Apache
class Apache:
    TRUE='true'
    FALSE='false'
    ON='on'
    OFF='off'
    ALL='all'
    NONE='none'

    def __init__(self):
        self.__dict__['vhosts'] = VirtualHosts ()
        self.__dict__['default_vhost'] = DefaultVirtualHost ()
        self.__dict__['listener'] = Listener ()
        vhostdefault = ApacheBase.apachebase.getvhostdefault ()
        ApacheBase.vhostdefault.delDirectoryIndex(vhostdefault)

    def __setattr__ (self, attr, value):
        if attr[0] == '_':
            self.__dict__[attr] = value
            return

        serveroptions = ApacheBase.apachebase.getserveroptions ()
        vhostdefault = ApacheBase.apachebase.getvhostdefault ()

        self.test_attr (attr, value)

        if Apache.__dict__.has_key ("set"+attr):
            apply (Apache.__dict__["set"+attr], (self, value))
            return

        if ApacheBase.serveroptions.__dict__.has_key ("set"+attr):
            apply (ApacheBase.serveroptions.__dict__["set"+attr], (serveroptions, value))
        elif ApacheBase.vhostdefault.__dict__.has_key ("set"+attr):
            apply (ApacheBase.vhostdefault.__dict__["set"+attr], (vhostdefault, value))
        else:
            raise AttributeError, attr


    def __getattr__ (self, attr):
        if attr[0] == '_':
            return self.__dict__[attr]

        serveroptions = ApacheBase.apachebase.getserveroptions ()
        vhostdefault = ApacheBase.apachebase.getvhostdefault ()

        if Apache.__dict__.has_key ("get"+attr):
            return apply (Apache.__dict__["get"+attr], (self, ))

        if ApacheBase.serveroptions.__dict__.has_key ("get"+attr):
            return apply (ApacheBase.serveroptions.__dict__["get"+attr], (serveroptions, ))
        elif ApacheBase.vhostdefault.__dict__.has_key ("get"+attr):
            return apply (ApacheBase.vhostdefault.__dict__["get"+attr], (vhostdefault, ))

        raise AttributeError, attr

    def getNameVirtualHosts (self):
        nvhlist = ApacheBase.apachebase.getnamevirtualhosts ()

        if nvhlist == None:
            return []

        retval = []
        for i in xrange (nvhlist.getNumNameVirtualHost ()):
            retval.append (nvhlist.getNumVirtualHost (i))

        return retval

    def setNameVirtualHosts (self, value):
        ApacheBase.apachebase.getserveroptions ().delnamevirtualhosts ()
        nvhlist = ApacheBase.apachebase.getserveroptions ().createnamevirtualhosts ()

        for var in value:
            nvhlist.setNameVirtualHost (nvhlist.addNameVirtualHost (), var)

    def testServerName (self, value):
        if value == "":
            raise TestError, "The server name cannot be blank"
        if not re.match("^[a-z0-9][a-z0-9\.\-]*[a-z0-9]$", value):
            raise TestError, "The server name may only contain alphanumeric characters"

    def test_attr (self, attr, value):
        if attr == '_attr' or attr == '_set':
            #stop people from being cute
            raise ValueError
        if Apache.__dict__.has_key ('test' + attr):
            apply (Apache.__dict__['test' + attr], (self, value))

    def testLogFormat (self, value):
        if value == "borp":
            raise ValueError, "Log cannot be \"borp\""

    def write (self, force=False):
        return ApacheBase.write (force)



###
### Meta classes for handling sub classes
###


##
## VirtualHosts
class VirtualHosts:
    def __init__ (self):
        self.__virtualhosts = ApacheBase.apachebase.getvirtualhosts ()

    def __getitem__ (self, key):
        for i in xrange (len (self)):
            vhost = self.__virtualhosts.getvirtualhost (i)
            if vhost.getVHName() == key:
                return VirtualHost (vhost)
        return None

    def __setitem__ (self, key, value):
        raise TypeError, "Unable to explicitly set a vhost.  Use VirtualHosts::add instead"

    def __delitem__ (self, key):
        for i in xrange (len (self)):
            vhost = self.__virtualhosts.getvirtualhost (i)
            if vhost.getVHName() == key:
                self.__virtualhosts.delvirtualhost (i)
                return
        raise KeyError, key

    def __len__ (self):
        return self.__virtualhosts.getNumvirtualhost ()

    def keys (self):
        if self.__virtualhosts == None:
            return []

        retval = []
        for i in xrange (len (self)):
            retval.append (self.__virtualhosts.getvirtualhost (i).getVHName())
        return retval

    def add (self, vhname=None):
        if self.__virtualhosts == None:
            self.__virtualhosts = ApacheBase.apachebase.createvirtualhosts ()
        keys = self.keys ()
        if vhname == None or vhname in keys:
            i = 0
            while 1:
                vhname = "Virtual Host %d" % i
                if not vhname in keys:
                    break
                i = i + 1
        vhost = self.__virtualhosts.addvirtualhost ()
        vhost.setVHName (vhname)

        return VirtualHost (vhost)

    def move (self, vhname, pos):
        for i in xrange (len (self)):
            vhost = self.__virtualhosts.getvirtualhost (i)
            if vhost.getVHName() == vhname:
                break;

        if i == len (self):
            return

        if i == pos or pos >= len (self) - 1:
            return

        self.__virtualhosts.movevirtualhost(i, pos)

##
## Listener
class Listener:
    def __init__ (self):
        self.__listener = ApacheBase.apachebase.getserveroptions ().getlistener ()

    def __getitem__ (self, key):
        return self.__listener.getListen (key)

    def __setitem__ (self, key, value):
        raise TypeError, "Unable to explicitly set a Listen.  Use Listener::add instead"

    def __delitem__ (self, key):
        self.__listener.delListen (key)

    def __len__ (self):
        return self.__listener.getNumListen ()

    def add (self, listen):
        if self.__listener == None:
            self.__listener = ApacheBase.apachebase.getserveroptions ().createlistener ()
        l = self.__listener.setListen (self.__listener.addListen (), listen)

        return l

    def clear (self):
        ApacheBase.apachebase.getserveroptions ().dellistener ()
        self.__listener = ApacheBase.apachebase.getserveroptions ().createlistener ()

##
## Directories
class Directories:
    def __init__ (self, vhost):
        self.__vhost = vhost
        self.__directories = vhost.getdirectories ()

    def __getitem__ (self, key):
        for i in xrange (len (self)):
            dir = self.__directories.getdirectory (i)
            if dir.getDir() == key:
                return Directory (dir)
        return None

    def __setitem__ (self, key, value):
        raise TypeError, "Unable to explicitly set a directory.  Use Directories::add instead"

    def __delitem__ (self, key):
        for i in xrange (len (self)):
            dir = self.__directories.getdirectory (i)
            if dir.getDir() == key:
                self.__directories.deldirectory (i)
                return
        raise KeyError, key

    def __len__ (self):
        if self.__directories == None:
            return 0
        return self.__directories.getNumdirectory ()

    def keys (self):
        if self.__directories == None:
            return []

        retval = []
        for i in xrange (len (self)):
            retval.append (self.__directories.getdirectory (i).getDir())
        return retval

    def add (self, dirname):
        if self.__directories == None:
            self.__directories = self.__vhost.createdirectories ()
        keys = self.keys ()
        if dirname in keys:
            raise KeyError, dirname
        dir = self.__directories.adddirectory ()
        dir.setDir (dirname)

        return Directory (dir)

##
## ErrorDocuments
class ErrorDocuments:
    ERROR_CODE_DATA =  {
        400 : (_("Bad Request"), _("The request could not be understood by this server.")),
        401 : (_("Authorization Required"), _("The request cannot be processed without authorization.")),
        403 : (_("Forbidden"), _("The request was refused by this server.")),
        404 : (_("Not Found"), _("The requested document was not found on this server")),
        405 : (_("Method Not Allowed"), _("The specified method was not allowed for this resource.")),
        406 : (_("Not Acceptable"), _("The request is not acceptable as stated.")),
        407 : (_("Proxy Authentication Required"), _("The request cannot be processed without authorization with the proxy.")),
        408 : (_("Request Time-out"), _("The client did not produce a request in time for this server.")),
        409 : (_("Conflict"), _("The request could not be completed due to a conflict within the resource.")),
        410 : (_("Gone"), _("The requested resource is no longer available at this server.")),
        411 : (_("Length Required"), _("this server requires a defined Content-Length.")),
        412 : (_("Precondition Failed"), _("A necessary precondition has failed.")),
        413 : (_("Request Entity Too Large"), _("The request cannot be processed because the entity is larger than this server's capabilities.")),
        414 : (_("Request-URI Too Large"), _("The URI is too long for this server to interpret.")),
        415 : (_("Unsupported Media Type"), _("The format of the requested entity is not supported.")),
        416 : (_("Requested Range Not Satisfiable"), _("The requested range is not acceptable to this server.")),
        417 : (_("Expectation Failed"), _("The expectation cannot be met by this server.")),
        500 : (_("Internal Server Error"), _("An unexpected condition prevents this server from fulfilling the request.")),
        501 : (_("Method Not Implemented"), _("This server does not support the method required to fulfill the request.")),
        502 : (_("Bad Gateway"), _("An invalid response was received.")),
        503 : (_("Service Temporarily Unavailable"), _("This server is temporarily overloaded or under maintenance.")),
        504 : (_("Gateway Time-out"), _("No response was given within the alloted time.")),
        505 : (_("HTTP Version Not Supported"), _("This server does not support the HTTP protocol version of the request.")) }

    def __init__ (self, vhost):
        self.__vhost = vhost
        self.__errdocs = vhost.geterrordocuments ()

    def __getitem__ (self, key):
        if not key in ErrorDocuments.ERROR_CODE_DATA.keys ():
            raise KeyError, key

        for i in xrange (len (self)):
            errdoc = self.__errdocs.geterrordocument (i)
            if errdoc.getCode () == key:
                return errdoc.getDocument ()

        return stack.apache.default_vhost.ErrorDocuments[key]

    def __setitem__ (self, key, value):
        if not key in ErrorDocuments.ERROR_CODE_DATA.keys ():
            raise KeyError, key

        def_value = stack.apache.default_vhost.ErrorDocuments[key]
        if def_value == value:
            del (self[key])
            return

        if self.__errdocs == None:
            self.__errdocs = self.__vhost.createerrordocuments ()

        for i in xrange (len (self)):
            errdoc = self.__errdocs.geterrordocument (i)
            if errdoc.getCode () == key:
                errdoc.setDocument (value)
                return

        doc = self.__errdocs.adderrordocument ()
        doc.setCode (key)
        doc.setDocument (value)

    def __delitem__ (self, key):
        if not key in ErrorDocuments.ERROR_CODE_DATA.keys ():
            raise KeyError, key
        for i in xrange (len (self)):
            errdoc = self.__errdocs.geterrordocument (i)
            if errdoc.getCode () == key:
                self.__errdocs.delerrordocument (i)
                return

    def __len__ (self):
        if self.__errdocs == None:
            return 0
        return self.__errdocs.getNumerrordocument ()

    def keys (self):
        retval = stack.apache.default_vhost.ErrorDocuments.keys ()
        for i in xrange (len (self)):
            code = self.__errdocs.geterrordocument (i).getCode ()
            if not code in retval:
                retval.append (code)

        retval.sort ()
        return retval


class DefaultErrorDocuments:
    def __init__ (self, vhost):
        self.__vhost = vhost
        self.__errdocs = vhost.geterrordocuments ()

    def __getitem__ (self, key):
        if not key in ErrorDocuments.ERROR_CODE_DATA.keys ():
            raise KeyError, key

        for i in xrange (len (self)):
            errdoc = self.__errdocs.geterrordocument (i)
            if errdoc.getCode () == key:
                return errdoc.getDocument ()
        return None

    def __setitem__ (self, key, value):
        if not key in ErrorDocuments.ERROR_CODE_DATA.keys ():
            raise KeyError, key

        if self.__errdocs == None:
            self.__errdocs = self.__vhost.createerrordocuments ()

        for i in xrange (len (self)):
            errdoc = self.__errdocs.geterrordocument (i)
            if errdoc.getCode () == key:
                errdoc.setDocument (value)
                return
        doc = self.__errdocs.adderrordocument ()
        doc.setCode (key)
        doc.setDocument (value)

    def __delitem__ (self, key):
        for i in xrange (len (self)):
            errdoc = self.__errdocs.geterrordocument (i)
            if errdoc.getCode () == key:
                self.__errdocs.delerrordocument (i)
                return

        # is this right?
        raise KeyError, key

    def __len__ (self):
        if self.__errdocs == None:
            return 0
        return self.__errdocs.getNumerrordocument ()

    def keys (self):
        retval = []
        for i in xrange (len (self)):
            errdoc = self.__errdocs.geterrordocument (i)
            retval.append (errdoc.getCode ())
        return retval


##
## Global code
##
stack = StateStack ( Apache())

if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
