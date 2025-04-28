## nfsExports.py - Code for dealing with /etc/exports in system-config-nfs
## Copyright (C) 2005 - 2006, 2009 Red Hat, Inc.
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
import copy

# Exceptions
class InstantiateError (Exception):
    pass

class ParseError (Exception):
    '''a parse error'''
    pass

# Classes
class opaqueChunk:
    '''any chunk of text that isn't a known object, in most cases a syntax error,
    but can also be e.g. an unknown NFS option'''
    def __init__ (self, chunk):
        self.names = [chunk]
        self.chunk = chunk

    def __str__ (self):
        return self.chunk

class nfsOptionType:
    '''generic NFS option type'''
    def __init__ (self, default = None, printdefault = False):
        self.default = default
        self.printdefault = printdefault

    def getOption (self, optionspec):
        if not optionspec:
            return self.default
        else:
            return optionspec

    def getOptionNormalized (self, optionspec):
        return self.getOption (optionspec)

    def getValue (self, optionspec, dummy = None):
        return self.getOption (optionspec)

    def isDefault (self, optionspec):
        return (optionspec == self.default)

    def isValidOptionSpec (self, optionspec):
        return False

class nfsOptionTypeAliasable (nfsOptionType):
    '''generic NFS option type with alias names'''
    def __init__ (self, genericName, *aliasLists, **kargs):
        if kargs.has_key ('default'):
            default = kargs['default']
        else:
            default = None
        if kargs.has_key ('printdefault'):
            printdefault = kargs['printdefault']
        else:
            printdefault = False
        self.genericName = genericName
        nfsOptionType.__init__ (self, default = default, printdefault = printdefault)
        allNames = []
        aliasLists = list (aliasLists)
        for i in range (len (aliasLists)):
            if isinstance (aliasLists[i], list):
                pass
            elif isinstance (aliasLists[i], tuple):
                aliasLists[i] = list (aliasLists[i])
            elif isinstance (aliasLists[i], str) or isinstance (aliasLists[i], unicode):
                aliasLists[i] = [ aliasLists[i] ]
            else:
                raise TypeError ("I don't understand type '%s'" % (type (aliasLists[i])))
            allNames.extend (aliasLists[i])
        self.aliasLists = aliasLists
        self.allNames = allNames
        if default and not self.isValidOptionSpec (default):
            raise KeyError ("default %s not found in names" % (default))

    def getOptionNormalized (self, optionspec):
        for aliases in self.aliasLists:
            if optionspec in aliases:
                return aliases[0]
        raise KeyError (optionspec)

    def isValidOptionSpec (self, optionspec):
        return optionspec in self.allNames

    def isResponsibleFor (self, optionname):
        if optionname == self.genericName:
            return True
        else:
            return self.isValidOptionSpec (optionname)

class nfsOptionTypeNState (nfsOptionTypeAliasable):
    '''n-state NFS option type'''

    def getOptionIndex (self, optionspec):
        for i in range (len (self.aliasLists)):
            if optionspec in self.aliasLists[i]:
                return i
        raise KeyError (optionspec)

    def getOptionNormalized (self, optionspec):
        return self.aliasLists[self.getOptionIndex (optionspec)][0]

    def isDefault (self, optionspec):
        return (self.getOptionNormalized (optionspec) == self.getOptionNormalized (self.default))

class nfsOptionTypeBoolean (nfsOptionTypeNState):
    '''boolean NFS option type'''
    def __init__ (self, trueNames, falseNames, default, printdefault = False):
        if isinstance (trueNames, str):
            genericName = trueNames
        else:
            genericName = trueNames[0]
        nfsOptionTypeNState.__init__ (self, genericName, trueNames, falseNames, default = default, printdefault = printdefault)

    def getValue (self, optionspec, alias):
        optionspec = nfsOptionType.getOption (self, optionspec)
        aliasspec = nfsOptionType.getOption (self, alias)
        i = self.getOptionIndex (optionspec)
        j = self.getOptionIndex (aliasspec)
        if i == j:
            return True
        else:
            return False

    def getOption (self, optionspec):
        if optionspec == True:
            return self.aliasLists[0][0]
        elif optionspec == False:
            return self.aliasLists[1][0]
        else:
            return nfsOptionTypeNState.getOption (self, optionspec)

class nfsOptionTypeParameter (nfsOptionTypeAliasable):
    '''parametrized NFS option type'''
    def __init__ (self, names, default = None):
        if isinstance (names, str):
            genericName = names
        else:
            genericName = names[0]
        nfsOptionTypeAliasable.__init__ (self, genericName, names, default = default)

    def _getNameValue (self, optionspec):
        (name, value) = optionspec.split ('=', 1)
        return (name, value)

    def getNameValue (self, optionspec):
        if self.isValidOptionSpec (optionspec):
            return self._getNameValue (optionspec)
        elif self.isResponsibleFor (optionspec):
            return (self.aliasLists[0][0], self.default)
        else:
            raise KeyError ("can't handle option specification '%s'" % (optionspec))

    def getOption (self, optionspec):
        if not len (optionspec) or (optionspec[0] != '!' and optionspec.find ('=') == -1):
            raise ValueError (optionspec)
        return self._getOption (optionspec)

    def _getOption (self, optionspec):
        if len (optionspec) and optionspec[0] == "!":
            option = False
        else:
            option = nfsOptionTypeAliasable.getOption (self, optionspec)
        if option == True:
            option = self.aliasLists[0][0]
        elif option == False:
            option = ''
        return option

    def getValue (self, optionspec, alias = None):
        if optionspec:
            return self.getNameValue (optionspec)[1]
        else:
            return self.default

    def isValidOptionSpec (self, optionspec):
        try:
            return nfsOptionTypeAliasable.isValidOptionSpec (self, self._getNameValue (optionspec)[0])
        except (ValueError, TypeError):
            return False

    def isResponsibleFor (self, optionname):
        return self.isValidOptionSpec (optionname + '=')

class nfsOptionTypeParameterOptional (nfsOptionTypeParameter):
    def __init__ (self, names, default = False):
        nfsOptionTypeParameter.__init__ (self, names, default)
    
    def _getNameValue (self, optionspec):
        if isinstance (optionspec, bool):
            if optionspec:
                return (self.aliasLists[0][0], True)
            else:
                return (self.aliasLists[0][0], False)
        elif isinstance (optionspec, str):
            try:
                return nfsOptionTypeParameter._getNameValue (self, optionspec)
            except ValueError:
                if len (optionspec) > 0 and optionspec[0] != '!':
                    return (optionspec, True)
                else:
                    return (optionspec[1:], False)
    
    def getOption (self, optionspec):
        return self._getOption (optionspec)

nfsKnownOptionTypes = [
    nfsOptionTypeBoolean ('secure', 'insecure', 'secure'),
    nfsOptionTypeBoolean ('rw', 'ro', 'ro', printdefault = True),
    nfsOptionTypeBoolean ('sync', 'async', 'sync', printdefault = True),
    nfsOptionTypeBoolean ('wdelay', 'no_wdelay', 'wdelay'),
    nfsOptionTypeBoolean ('hide', 'nohide', 'hide'),
    nfsOptionTypeBoolean ('subtree_check', 'no_subtree_check', 'subtree_check'),
    nfsOptionTypeBoolean (['secure_locks', 'auth_nlm'], ['insecure_locks', 'no_auth_nlm'], 'secure_locks'),
    nfsOptionTypeParameterOptional (['mp', 'mountpoint']),
    nfsOptionTypeParameter ('fsid'),
    nfsOptionTypeNState ('squash', 'root_squash', 'no_root_squash', 'all_squash', default = 'root_squash'),
    nfsOptionTypeParameter ('anonuid'),
    nfsOptionTypeParameter ('anongid')
]

def nfsOptionTypeLookup (name):
    foundtype = None
    for type in nfsKnownOptionTypes:
        if type.isResponsibleFor (name):
            foundtype = type
            break
    return foundtype

class nfsOption:
    '''an actual NFS option (of a client and share)'''
    def __init__ (self, optionspec):
        if len (optionspec) and optionspec[0] == '!':
            _optionspec = optionspec[1:]
        else:
            _optionspec = optionspec
        self.type = nfsOptionTypeLookup (_optionspec.split ('=')[0])
        if not self.type:
            raise ParseError ("unknown option specification '%s'" % (optionspec))
        try:
            self.set (optionspec)
        except ValueError:
            raise ParseError (_("illegal option specification '%s'") % (optionspec))

    def __str__ (self):
        if self.type.printdefault or not self.type.isDefault (self.option):
            return self.option
        else:
            return ''

    def set (self, optionspec):
        self.option = self.type.getOption (optionspec)

    def get (self, alias = None):
        return self.type.getValue (self.option, alias)

class nfsClient:
    '''a specific NFS client of a share with its options'''
    re_clientspec = re.compile ('^(?P<client>[^\(\)]+)(?:\((?P<options>[^\(\)]+)\))?$')
    def __init__ (self, clientspec, sep = ""):
        self.sep = sep
        self.warnings = []
        match = nfsClient.re_clientspec.match (clientspec)
        if not match:
            raise ParseError (clientspec)
        self.client = match.group ('client')
        try:
            options = match.group ('options')
            if not options:
                options = ''
        except IndexError:
            options = ''

        self.options = []
        self.options_by_type = {}
        if len (options) > 0:
            for optionspec in options.split (','):
                try:
                    option = opaqueChunk (optionspec)
                    option = nfsOption (optionspec)
                    if not self.options_by_type.has_key (option.type):
                        self.options_by_type[option.type] = option
                    else:
                        self.warnings.append (_("duplicate option '%s'") % (optionspec))
                except ParseError:
                    if isinstance (option, opaqueChunk):
                        self.warnings.append (_("unknown option '%s'") % (optionspec))
                self.options.append (option)

    def __str__ (self):
        __str = self.client
        if self.options:
            options_strs = map (str, self.options)
            while '' in options_strs:
                options_strs.remove ('')
            __str += '(%s)' % (','.join (options_strs))
        return __str + self.sep

    def get (self, name):
        type = nfsOptionTypeLookup (name)
        if self.options_by_type.has_key (type):
            #print "client.get (%s) = %s" % (name, self.options_by_type[type].get (name))
            return self.options_by_type[type].get (name)
        else:
            # default
            #print "client.get (%s) = %s <- default" % (name, type.getValue (None, name))
            return type.getValue (None, name)

    def set (self, optionspec):
        option = nfsOption (optionspec)
        if self.options_by_type.has_key (option.type):
            oldoption = self.options_by_type[option.type]
            self.options_by_type[oldoption.type] = option
            self.options[self.options.index (oldoption)] = option
        else:
            self.options.append (option)
            self.options_by_type[option.type] = option

class nfsShareLine:
    '''an arbitrary (eventually continued) line in /etc/exports'''
    re_comment = re.compile (r'\A(?P<line>[^#]*?)(?P<comment>\s*#.*)\Z', re.MULTILINE | re.DOTALL)
    
    def __init__ (self, line):
        self.warnings = []
        self.line, self.comment = self.parseComment (line.strip ())
        self.parse ()

    def parseComment (self, line):
        '''parse and strip off comments from lines'''
        match = nfsShareLine.re_comment.match (line)
        if match:
            line = match.group ('line')
            comment = match.group ('comment')
        else:
            comment = None
        return line, comment

    def parse (self):
        pass

    def __str__ (self):
        __str = self.line
        if self.comment:
            __str += self.comment
        # add continuation backslashes
        return __str.replace ('\n', '\\\n')

class nfsShareLineEmpty (nfsShareLine):
    '''an empty (or comment only) line in /etc/exports'''
    def parse (self):
        nfsShareLine.parse (self)
        if len (self.line.strip ()) > 0:
            raise ParseError (str (self))

class nfsShare (nfsShareLine):
    '''an NFS share specification in /etc/exports'''
    re_spec = re.compile (r'\A(?P<path>/\S*)(?P<sep>\s+)(?P<clientspecs>.*)\Z', re.MULTILINE | re.DOTALL)
    re_cspec = re.compile (r'^(?P<clientspec>\S+)(?P<sep>\s*)(?P<rest>.*)$')

    def __len__ (self):
        return len (self.clients)

    def __str__ (self):
        __str = self.path + self.sep + ' '.join (map (str, self.clients))
        if self.comment:
            __str += self.comment
        # add continuation backslashes
        return __str.replace ('\n', '\\\n')

    def parse (self):
        '''parse the NFS share specification line'''
        match = nfsShare.re_spec.match (self.line)
        if not match:
            raise ParseError (nfsShareLine.__str__ (self))
        self.path = match.group ('path')
        self.sep = match.group ('sep')
        cspecstr = match.group ('clientspecs')
        self.clients = []
        while len (cspecstr) > 0:
            m = nfsShare.re_cspec.match (cspecstr)
            if not m:
                raise ParseError (nfsShareLine.__str__ (self))
            clientspec = m.group ('clientspec')
            sep = m.group ('sep')
            client = nfsClient (clientspec, sep)
            self.warnings.extend (client.warnings)
            self.clients.append (client)
            cspecstr = m.group ('rest')

    def remove (self, client):
        if isinstance (client, str):
            client = self.getClient (client)
        if client in self.clients:
            self.clients.remove (client)
        else:
            raise KeyError (client)

    def getClient (self, clientstr):
        for client in self.clients:
            if client.client == clientstr:
                return client
        return None

class nfsExports:
    '''class holding all information about /etc/exports'''
    instantiated = False
    filename = '/etc/exports'
    def __init__ (self):
        if nfsExports.instantiated:
            raise InstantiateError ("this class can't be instantiated more than one time")
        nfsExports.instantiated = True
        self.readFile ()

    def __del__ (self):
        nfsExports.instantiated = False

    def __len__ (self):
        return len (self.lineobjs)

    def __str__ (self):
        return "".join (map (lambda x: str (x) + "\n", self.lineobjs))

    def readFile (self):
        '''read and parse /etc/exports'''
        try:
            fd = open('/etc/exports', 'r')
            lines = fd.readlines()
            fd.close ()
        except IOError:
            lines = []

        self.lineobjs = []
        self.warnings = []
        linenr=0
        line = ''
        for _line in lines:
            linenr += 1
            if _line[-1] == '\n':
                # remove trailing newline
                _line = _line[:-1]

            try:
                _line.decode ('string-escape')
                line += _line
            except ValueError:
                # trailing backslash -> continuation
                line += _line[:-1] + '\n'
                continue
            lineobj = None
            try:
                lineobj = nfsShareLine (line)
                try:
                    lineobj = nfsShare (line)
                except ParseError:
                    try:
                        lineobj = nfsShareLineEmpty (line)
                    except ParseError, p:
                        self.warnings.append ([linenr, _("couldn't parse line '%s'") % (line.rstrip ())])
            except ParseError:
                pass
            for w in lineobj.warnings:
                self.warnings.append ([linenr, w])
            self.lineobjs.append (lineobj)
            line = ''

    def writeFile (self):
        try:
            os.rename('/etc/exports', '/etc/exports.bak')
        except OSError:
            pass

        fd = open('/etc/exports', 'w')
        fd.write (str (self))
        fd.close ()

    def getShares (self, path = None):
        shares = []
        for lineobj in self.lineobjs:
            if isinstance (lineobj, nfsShare) and (not path or path == lineobj.path):
                shares.append (lineobj)
        return shares

    def consolidateShares (self):
        self.lineobjs = self.consolidatedShares (nonshares = True)

    def consolidatedShares (self, lineobjs = None, nonshares = False):
        if not lineobjs:
            lineobjs = self.lineobjs
        newlineobjs = []
        newlineobjs_by_path = {}

        for o in lineobjs:
            if not isinstance (o, nfsShare):
                if nonshares:
                    newlineobjs.append (o)
            elif not newlineobjs_by_path.has_key (o.path):
                newlineobjs.append (o)
                newlineobjs_by_path[o.path] = o
            else:
                newlineobjs_by_path[o.path].clients.extend (o.clients)

        return newlineobjs

    def remove (self, share, clients):
        if isinstance (clients, nfsClient):
            clients = [clients]
        if share in self.lineobjs:
            for client in clients:
                share.remove (client)
            if len (share) <= 0:
                self.lineobjs.remove (share)

    def add (self, share, client):
        if not share in self.lineobjs:
            self.lineobjs.append (share)
        if not client in share.clients:
            share.clients.append (client)

    def startNfs (self):
        if os.system ("/sbin/chkconfig portmap") == 0:
            os.system('/sbin/service portmap restart > /dev/null')
        else:
            os.system('/sbin/service rpcbind restart > /dev/null')
        os.system('/sbin/service nfs restart > /dev/null')

    def exportFs (self):
        os.system('/usr/sbin/exportfs -r')
