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

import yum
import os
import rpm
import sys
import logging
import time
import signal
from yum.constants import *
from yum import logginglevels
from yum import plugins
from yum import Errors
from gui_errors import * 

def sigquit(signum, frame):
    print >> sys.stderr, "Quit signal sent - exiting immediately"
    sys.exit(1)

class RPMInstallCallback:
    def __init__(self, output=1):
        self.output = output
        self.callbackfilehandles = {}
        self.total_actions = 0
        self.total_installed = 0
        self.installed_pkg_names = []
        self.total_removed = 0
        self.mark = "#"
        self.marks = 27
        self.lastmsg = None
        #self.logger = logging.getLogger('yum.filelogging.RPMInstallCallback')
        self.filelog = False

        self.myprocess = { TS_UPDATE : 'Updating', 
                           TS_ERASE: 'Erasing',
                           TS_INSTALL: 'Installing', 
                           TS_TRUEINSTALL : 'Installing',
                           TS_OBSOLETED: 'Obsoleted',
                           TS_OBSOLETING: 'Installing'}
        self.mypostprocess = { TS_UPDATE: 'Updated', 
                               TS_ERASE: 'Erased',
                               TS_INSTALL: 'Installed', 
                               TS_TRUEINSTALL: 'Installed', 
                               TS_OBSOLETED: 'Obsoleted',
                               TS_OBSOLETING: 'Installed'}

        self.tsInfo = None # this needs to be set for anything else to work

    def _dopkgtup(self, hdr):
        tmpepoch = hdr['epoch']
        if tmpepoch is None: epoch = '0'
        else: epoch = str(tmpepoch)

        return (hdr['name'], hdr['arch'], epoch, hdr['version'], hdr['release'])

    def _makeHandle(self, hdr):
        handle = '%s:%s.%s-%s-%s' % (hdr['epoch'], hdr['name'], hdr['version'],
          hdr['release'], hdr['arch'])

        return handle

    def _localprint(self, msg):
        if self.output:
            print msg

    def _makefmt(self, percent, progress = True):
        l = len(str(self.total_actions))
        size = "%s.%s" % (l, l)
        fmt_done = "[%" + size + "s/%" + size + "s]"
        done = fmt_done % (self.total_installed + self.total_removed,
                           self.total_actions)
        marks = self.marks - (2 * l)
        width = "%s.%s" % (marks, marks)
        fmt_bar = "%-" + width + "s"
        if progress:
            bar = fmt_bar % (self.mark * int(marks * (percent / 100.0)), )
            fmt = "\r  %-10.10s: %-28.28s " + bar + " " + done
        else:
            bar = fmt_bar % (self.mark * marks, )
            fmt = "  %-10.10s: %-28.28s "  + bar + " " + done
        return fmt

    def _logPkgString(self, hdr):
        """return nice representation of the package for the log"""
        (n,a,e,v,r) = self._dopkgtup(hdr)
        if e == '0':
            pkg = '%s.%s %s-%s' % (n, a, v, r)
        else:
            pkg = '%s.%s %s:%s-%s' % (n, a, e, v, r)

        return pkg

    def callback(self, what, bytes, total, h, user):
        if what == rpm.RPMCALLBACK_TRANS_START:
            if bytes == 6:
                self.total_actions = total

        elif what == rpm.RPMCALLBACK_TRANS_PROGRESS:
            pass

        elif what == rpm.RPMCALLBACK_TRANS_STOP:
            pass

        elif what == rpm.RPMCALLBACK_INST_OPEN_FILE:
            self.lastmsg = None
            hdr = None
            if h is not None:
                hdr, rpmloc = h
                handle = self._makeHandle(hdr)
                fd = os.open(rpmloc, os.O_RDONLY)
                self.callbackfilehandles[handle]=fd
                self.total_installed += 1
                self.installed_pkg_names.append(hdr['name'])
                return fd
            else:
                self._localprint(_("No header - huh?"))

        elif what == rpm.RPMCALLBACK_INST_CLOSE_FILE:
            hdr = None
            if h is not None:
                hdr, rpmloc = h
                handle = self._makeHandle(hdr)
                os.close(self.callbackfilehandles[handle])
                fd = 0

                # log stuff
                pkgtup = self._dopkgtup(hdr)
                
                txmbrs = self.tsInfo.getMembers(pkgtup=pkgtup)
                for txmbr in txmbrs:
                    try:
                        process = self.myprocess[txmbr.output_state]
                        processed = self.mypostprocess[txmbr.output_state]
                    except KeyError:
                        pass

                    if self.filelog:
                        pkgrep = self._logPkgString(hdr)
                        msg = '%s: %s' % (processed, pkgrep)
                        #self.logger.info(msg)


        elif what == rpm.RPMCALLBACK_INST_PROGRESS:
            if h is not None:
                # If h is a string, we're repackaging.
                # Why the RPMCALLBACK_REPACKAGE_PROGRESS flag isn't set, I have no idea
                if type(h) == type(""):
                    if total == 0:
                        percent = 0
                    else:
                        percent = (bytes*100L)/total
                    if self.output and sys.stdout.isatty():
                        fmt = self._makefmt(percent)
                        msg = fmt % ('Repackage', h)
                        if bytes == total:
                            msg = msg + "\n"

                        if msg != self.lastmsg:
                            sys.stdout.write(msg)
                            sys.stdout.flush()
                            self.lastmsg = msg
                else:
                    hdr, rpmloc = h
                    if total == 0:
                        percent = 0
                    else:
                        percent = (bytes*100L)/total
                    pkgtup = self._dopkgtup(hdr)
                    
                    txmbrs = self.tsInfo.getMembers(pkgtup=pkgtup)
                    for txmbr in txmbrs:
                        try:
                            process = self.myprocess[txmbr.output_state]
                        except KeyError, e:
                            print "Error: invalid output state: %s for %s" % \
                               (txmbr.output_state, hdr['name'])
                        else:
                            if self.output and (sys.stdout.isatty() or bytes == total):
                                fmt = self._makefmt(percent)
                                msg = fmt % (process, hdr['name'])
                                if msg != self.lastmsg:
                                    sys.stdout.write(msg)
                                    sys.stdout.flush()
                                    self.lastmsg = msg
                                if bytes == total:
                                    print " "


        elif what == rpm.RPMCALLBACK_UNINST_START:
            pass

        elif what == rpm.RPMCALLBACK_UNINST_PROGRESS:
            pass

        elif what == rpm.RPMCALLBACK_UNINST_STOP:
            self.total_removed += 1
            if self.filelog and h not in self.installed_pkg_names:
                logmsg = _('Erased: %s' % (h))
                #self.logger.info(logmsg)
            
            if self.output and sys.stdout.isatty():
                if h not in self.installed_pkg_names:
                    process = "Removing"
                else:
                    process = "Cleanup"
                percent = 100
                fmt = self._makefmt(percent, False)
                msg = fmt % (process, h)
                sys.stdout.write(msg + "\n")
                sys.stdout.flush()

        elif what == rpm.RPMCALLBACK_REPACKAGE_START:
            pass
        elif what == rpm.RPMCALLBACK_REPACKAGE_STOP:
            pass
        elif what == rpm.RPMCALLBACK_REPACKAGE_PROGRESS:
            pass


class tuiInstall(yum.YumBase):
    def __init__(self, configfn = "/etc/yum.conf"):
        yum.YumBase.__init__(self)
        
        try:
            self.doConfigSetup(fn=configfn,
                               plugin_types=(yum.plugins.TYPE_CORE,)) 
        except yum.Errors.ConfigError, e:
            raise GuiError, e                      
        
        logging.basicConfig()
        
        try:
            self.reset()
        except yum.Errors.RepoError:            
            raise RepoErrors()          
            
        self.logger = logging.getLogger("yum.main")
        self.verbose_logger = logging.getLogger("yum.verbose.cli")  
            
    def reset(self):
        self.closeRpmDB()
        self.doTsSetup()
        self.doRpmDBSetup()   
      
    def reportDownloadSize(self, packages):
        """Report the total download size for a set of packages"""
        totsize = 0
        error = False
        for pkg in packages:
            # Just to be on the safe side, if for some reason getting
            # the package size fails, log the error and don't report download
            # size
            try:
                size = int(pkg.size)
                totsize += size
            except:
                 error = True
                 self.logger.error('There was an error calculating total download size')
                 break

        if (not error):
            self.verbose_logger.log(logginglevels.INFO_1, "Total download size: %s", 
                self.format_number(totsize))
            
    def listTransaction(self):
        """returns a string rep of the  transaction in an easy-to-read way."""
        
        self.tsInfo.makelists()
        if len(self.tsInfo) > 0:
            out = """
=============================================================================
 %-22s  %-9s  %-15s  %-16s  %-5s
=============================================================================
""" % ('Package', 'Arch', 'Version', 'Repository', 'Size')
        else:
            out = ""

        for (action, pkglist) in [('Installing', self.tsInfo.installed),
                            ('Updating', self.tsInfo.updated),
                            ('Removing', self.tsInfo.removed),
                            ('Installing for dependencies', self.tsInfo.depinstalled),
                            ('Updating for dependencies', self.tsInfo.depupdated),
                            ('Removing for dependencies', self.tsInfo.depremoved)]:
            if pkglist:
                totalmsg = "%s:\n" % action
            for txmbr in pkglist:
                (n,a,e,v,r) = txmbr.pkgtup
                evr = txmbr.po.printVer()
                repoid = txmbr.repoid
                pkgsize = float(txmbr.po.size)
                size = self.format_number(pkgsize)
                msg = " %-22s  %-9s  %-15s  %-16s  %5s\n" % (n, a,
                              evr, repoid, size)
                for obspo in txmbr.obsoletes:
                    appended = '     replacing  %s.%s %s\n\n' % (obspo.name,
                        obspo.arch, obspo.printVer())
                    msg = msg+appended
                totalmsg = totalmsg + msg
        
            if pkglist:
                out = out + totalmsg

        summary = """
Transaction Summary
=============================================================================
Install  %5.5s Package(s)         
Update   %5.5s Package(s)         
Remove   %5.5s Package(s)         
""" % (len(self.tsInfo.installed + self.tsInfo.depinstalled),
       len(self.tsInfo.updated + self.tsInfo.depupdated),
       len(self.tsInfo.removed + self.tsInfo.depremoved))
        out = out + summary
        
        return out
        
    def postTransactionOutput(self):
        out = ''
        
        self.tsInfo.makelists()

        for (action, pkglist) in [('Removed', self.tsInfo.removed), 
                                  ('Dependency Removed', self.tsInfo.depremoved),
                                  ('Installed', self.tsInfo.installed), 
                                  ('Dependency Installed', self.tsInfo.depinstalled),
                                  ('Updated', self.tsInfo.updated),
                                  ('Dependency Updated', self.tsInfo.depupdated),
                                  ('Replaced', self.tsInfo.obsoleted)]:
            
            if len(pkglist) > 0:
                out += '\n%s:' % action
                for txmbr in pkglist:
                    (n,a,e,v,r) = txmbr.pkgtup
                    msg = " %s.%s %s:%s-%s" % (n,a,e,v,r)
                    out += msg
        
        return out
        
    def format_number(self, number, SI=0, space=' '):
        """Turn numbers into human-readable metric-like numbers"""
        symbols = ['',  # (none)
                    'k', # kilo
                    'M', # mega
                    'G', # giga
                    'T', # tera
                    'P', # peta
                    'E', # exa
                    'Z', # zetta
                    'Y'] # yotta
    
        if SI: step = 1000.0
        else: step = 1024.0
    
        thresh = 999
        depth = 0
    
        # we want numbers between 
        while number > thresh:
            depth  = depth + 1
            number = number / step
    
        # just in case someone needs more than 1000 yottabytes!
        diff = depth - len(symbols) + 1
        if diff > 0:
            depth = depth - diff
            number = number * thresh**depth
    
        if type(number) == type(1) or type(number) == type(1L):
            format = '%i%s%s'
        elif number < 9.95:
            # must use 9.95 for proper sizing.  For example, 9.99 will be
            # rounded to 10.0 with the .1f format string (which is too long)
            format = '%.1f%s%s'
        else:
            format = '%.0f%s%s'
    
        return(format % (number, space, symbols[depth]))
    
    def is_group_installed(self, grpid):
        if not self.comps.has_group(grpid):
            raise Errors.GroupsError, "No Group named %s exists" % grpid
            
        thisgroup = self.comps.return_group(grpid)

        if not thisgroup:
            raise Errors.GroupsError, "No Group named %s exists" % grpid

        if thisgroup.installed:
            return True
        else:
            return False            
            
    def gpgsigcheck(self, pkgs):
        '''Perform GPG signature verification on the given packages, installing
        keys if possible

        Returns non-zero if execution should stop (user abort).
        Will raise YumBaseError if there's a problem
        '''
        for po in pkgs:
            result, errmsg = self.sigCheckPkg(po)

            if result == 0:
                # Verified ok, or verify not req'd
                continue            

            elif result == 1:
               if not sys.stdin.isatty() and not self.conf.assumeyes:
                  raise yum.Errors.YumBaseError, \
                        'Refusing to automatically import keys when running ' \
                        'unattended.\nUse "-y" to override.'

               # the callback here expects to be able to take options which
               # userconfirm really doesn't... so fake it
               #self.getKeyForPackage(po, lambda x, y, z: self.userconfirm())

            else:
                # Fatal error
                raise yum.Errors.YumBaseError, errmsg

        return 0  
	    
    def checkDeps(self):
        self.verbose_logger.log(logginglevels.INFO_2, 'Resolving Dependencies')
        self.verbose_logger.debug(time.time())        
        self.buildTransaction() 
        self.verbose_logger.log(logginglevels.INFO_2, '\nDependencies Resolved')
        self.verbose_logger.debug(time.time())
        
    def doTransaction(self):
        """takes care of package downloading, checking, user confirmation and actually
           RUNNING the transaction"""

        # output what will be done:
        self.verbose_logger.log(yum.logginglevels.INFO_1,
            self.listTransaction())
        
        # Check which packages have to be downloaded
        downloadpkgs = []
        stuff_to_download = False
        for txmbr in self.tsInfo.getMembers():
            if txmbr.ts_state in ['i', 'u']:
                stuff_to_download = True
                po = txmbr.po
                if po:
                    downloadpkgs.append(po)

        # Close the connection to the rpmdb so that rpm doesn't hold the SIGINT
        # handler during the downloads. self.ts is reinitialised later in this
        # function anyway (initActionTs). 
        self.ts.close()

        # Report the total download size to the user, so he/she can base
        # the answer on this info
        if stuff_to_download:
            self.reportDownloadSize(downloadpkgs)        

        self.verbose_logger.log(yum.logginglevels.INFO_2,
            'Downloading Packages:')
        problems = self.downloadPkgs(downloadpkgs) 

        if len(problems.keys()) > 0:
            errstring = ''
            errstring += 'Error Downloading Packages:\n'
            for key in problems.keys():
                errors = yum.misc.unique(problems[key])
                for error in errors:
                    errstring += '  %s: %s\n' % (key, error)
            raise yum.Errors.YumBaseError, errstring

        # Check GPG signatures
        if self.gpgsigcheck(downloadpkgs) != 0:
            return 1
        
        self.verbose_logger.log(yum.logginglevels.INFO_2,
            'Running Transaction Test')
        tsConf = {}
        for feature in ['diskspacecheck']: # more to come, I'm sure
            tsConf[feature] = getattr(self.conf, feature)
        
        testcb = RPMInstallCallback(output=0)
        testcb.tsInfo = self.tsInfo
        
        self.initActionTs()
        # save our dsCallback out
        dscb = self.dsCallback
        self.dsCallback = None # dumb, dumb dumb dumb!
        self.populateTs(keepold=0) # sigh
        tserrors = self.ts.test(testcb, conf=tsConf)
        del testcb
        
        self.verbose_logger.log(yum.logginglevels.INFO_2,
            'Finished Transaction Test')
        if len(tserrors) > 0:
            errstring = 'Transaction Check Error:\n'
            for descr in tserrors:
                errstring += '  %s\n' % descr 
            
            raise yum.Errors.YumBaseError, errstring + '\n' + \
                 self.errorSummary(errstring)
        self.verbose_logger.log(yum.logginglevels.INFO_2,
             'Transaction Test Succeeded')
        del self.ts
        
        # unset the sigquit handler
        signal.signal(signal.SIGQUIT, signal.SIG_DFL)
        
        self.initActionTs() # make a new, blank ts to populate
        self.populateTs(keepold=0) # populate the ts
        self.ts.check() #required for ordering
        self.ts.order() # order

        # put back our depcheck callback
        self.dsCallback = dscb

        output = 1
        if self.conf.debuglevel < 2:
            output = 0
        cb = RPMInstallCallback(output=output)
        cb.filelog = True
        cb.tsInfo = self.tsInfo

        self.verbose_logger.log(yum.logginglevels.INFO_2, 'Running Transaction')
        self.runTransaction(cb=cb)

        # close things
        self.verbose_logger.log(yum.logginglevels.INFO_1,
            self.postTransactionOutput())
        
        # put back the sigquit handler
        signal.signal(signal.SIGQUIT, sigquit)
        
        return 0   

    def install_language(self, grpid):
        self.selectGroup(grpid)
        self.checkDeps()        
        self.doTransaction()        

        self.verbose_logger.log(logginglevels.INFO_2, 'Complete!')
        self.closeRpmDB()
        self.doUnlock()       



	
	
	
	
	
	

    
    	
    	
	
	
       


 






