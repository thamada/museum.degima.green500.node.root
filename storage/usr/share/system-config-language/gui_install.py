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

import language_backend
import lang_dict
import string
import os, sys
import gtk
import pango
import urlgrabber, urlgrabber.progress
import urllib2
import time

import yum
import yum.Errors
from yum.constants import *

import gui_progress    
from gui_errors import *
import gui_detailsDialog

import gettext
_ = lambda x: gettext.ldgettext("system-config-language", x)
N_ = lambda x: x


GuiDetailsDialog = gui_detailsDialog.GuiDetailsDialog
GuiTransactionProgress = gui_progress.GuiTransactionProgress
GuiProgress = gui_progress.GuiProgress
GuiProgressCallback = gui_progress.GuiProgressCallback

def _runGtkMain(*args):
    while gtk.events_pending():
        gtk.main_iteration()

class guiInstall(yum.YumBase):
    def __init__(self, configfn = "/etc/yum.conf"):                                  
        yum.YumBase.__init__(self)
                
        try:
            self.doConfigSetup(fn=configfn,
                               plugin_types=(yum.plugins.TYPE_CORE,))
        except yum.Errors.ConfigError, e:
            raise GuiError, e             
                 
        try:
            self.reset()
        except yum.Errors.RepoError:            
            raise RepoErrors()          

        self.unsignedok = False        
                  
   
    def is_group_installed(self, grpid, mainwin):         
        d = gtk.MessageDialog(mainwin, 
                              gtk.DIALOG_MODAL,
                              gtk.MESSAGE_INFO,
                              message_format = _("Note:"))
        
        d.format_secondary_text(_("Connecting Yum database, please wait for a bit ..."))                        
        d.show()
        
        while (gtk.events_pending ()):
	        gtk.main_iteration ();
        
        groupexists = True    
        if not self.comps.has_group(grpid):
            groupexists = False	

        thisgroup = self.comps.return_group(grpid)
        d.destroy()

        if not thisgroup:
            groupexists = False

        if groupexists == False:
            str = _("No Group named %s exists: Do you still want to install language without proper support?" %grpid)
            gd= gtk.MessageDialog(mainwin, gtk.DIALOG_MODAL,
                                      gtk.MESSAGE_QUESTION,
                                      message_format = str)
            b = gd.add_button(_("No"), gtk.RESPONSE_CANCEL)
            b = gd.add_button(_("Yes"), gtk.RESPONSE_OK)
            d.set_default_response(gtk.RESPONSE_OK)
            rc = gd.run()
            gd.destroy()
            if rc == gtk.RESPONSE_OK:
                lb=language_backend.LanguageBackend()
                ld=lang_dict.languages_Dict
                for (key, val) in ld.iteritems():
                    if ld[key]==grpid:
                        lb.originalFile=None
                        lb.writeI18N(key, "", "latarcyrheb-sun16", "utf8")
                        # send message to login manager to re-read config / pick up lang change
                        if os.access("/var/gdm/.gdmfifo", os.F_OK):
                            try:
                                fd = os.open("/tmp/.gdm_socket", os.O_WRONLY | os.O_APPEND | os.O_NONBLOCK)
                                if fd >= 0:
                                    os.write(fd, "\nUPDATE_CONFIG\n")
                                    os.close(fd)
                            except:
                                pass
                return True
            else:
                       raise yum.Errors.GroupsError, "No Group named %s exists" % grpid

        if thisgroup.installed:
            return True
        else:
	        return False    
	    
    def reset(self):
        self.closeRpmDB()
        self.doTsSetup()
        self.doRpmDBSetup()        
	    
    def checkDeps(self, mainwin):
        class dscb:
            def __init__(self, pbar, ayum):
                self.pbar = pbar
                self.ayum = ayum

                self.incr = 0.0
                
                self.procReq = self.transactionPopulation = self.downloadHeader = self.start = self.unresolved = self.procConflict = _runGtkMain

            def tscheck(self):
                num = len(self.ayum.tsInfo.getMembers())
                self.incr = (1.0 / num) * ((1.0 - self.pbar.get_fraction()) / 2)
                _runGtkMain()                

            def pkgAdded(self, *args):
                self.pbar.set_fraction(self.pbar.get_fraction() + self.incr)
                _runGtkMain()

            def restartLoop(self):
                cur = self.pbar.get_fraction()
                new = ((1.0 - cur) / 2) + cur
                self.pbar.set_fraction(new)
                _runGtkMain()

            def end(self):
                self.pbar.set_fraction(1.0)
                _runGtkMain()

        pbar = GuiProgress(_("Resolving dependencies for updates"), mainwin)
        pbar.show()
        dsCB = dscb(pbar, self)
        self.dsCallback = dsCB
        
        del self.ts
        self.initActionTs() 
        
        try:
            (result, msgs) = self.buildTransaction()
        except yum.Errors.RepoError, errmsg:
            self.dsCallback = None 
            pbar.destroy()
            
            d = GuiDetailsDialog(mainwin, gtk.MESSAGE_ERROR,
                                          [('gtk-ok', gtk.RESPONSE_OK)],
                                          _("Error downloading headers"),
                                          _("Errors were encountered while "
                                            "downloading package headers."))
            d.set_details("%s" %(errmsg,))
            d.run()
            d.destroy()
            raise GuiDownloadError
        
        self.dsCallback = None 
        pbar.destroy()

        if result == 1:
            d = GuiDetailsDialog(mainwin, gtk.MESSAGE_ERROR,
                                 [('gtk-ok', gtk.RESPONSE_OK)],
                                 _("Error resolving dependencies"),
                                 _("Unable to resolve dependencies for some "
                                   "packages selected for installation."))
            d.set_details(string.join(msgs, "\n"))
            d.run()
            d.destroy()
            raise GuiDependencyError

    def depDetails(self, mainwin):
        self.tsInfo.makelists()
        if (len(self.tsInfo.depinstalled) > 0 or 
            len(self.tsInfo.depupdated) > 0 or
            len(self.tsInfo.depremoved) > 0):
            d = GuiDetailsDialog(mainwin, gtk.MESSAGE_INFO,
                                 [('gtk-cancel', gtk.RESPONSE_CANCEL),
                                  (_("Continue"), gtk.RESPONSE_OK, 'gtk-ok')],
                                 _("Dependencies added"),
                                 _("Updating these packages requires "
                                   "additional package changes for proper "
                                   "operation."))

            b = gtk.TextBuffer()
            tag = b.create_tag('bold')
            tag.set_property('weight', pango.WEIGHT_BOLD)
            tag = b.create_tag('indented')
            tag.set_property('left-margin', 10)
            types=[(self.tsInfo.depinstalled,_("Adding for dependencies:\n")),
                   (self.tsInfo.depremoved, _("Removing for dependencies:\n")),
                   (self.tsInfo.depupdated, _("Updating for dependencies:\n"))]
            for (lst, strng) in types:
                if len(lst) > 0:
                    i = b.get_end_iter()
                    b.insert_with_tags_by_name(i, strng, "bold")
                    for txmbr in lst:
                        i = b.get_end_iter()
                        (n,a,e,v,r) = txmbr.pkgtup
                        b.insert_with_tags_by_name(i, "%s-%s-%s\n" % (n,v,r),
                                                   "indented")
            d.set_details(buffer = b)
            timeout = 20
            if len(self.tsInfo.depremoved) > 0:
                d.expand_details()
                timeout = None
            rc = d.run(timeout=timeout)
            d.destroy()
            if rc != gtk.RESPONSE_OK:
                self._undoDepInstalls()

    def downloadPackages(self, mainwin):
        class dlcb(urlgrabber.progress.BaseMeter):
            def __init__(self, pbar, dlpkgs):
                urlgrabber.progress.BaseMeter.__init__(self)
                self.pbar = pbar
                self.total = float(len(dlpkgs))
                self.current = 0
                self.last = 0

            def _do_start(self, now):
                txt = _("Downloading %s") %(urllib2.unquote(self.basename),)
                self.pbar.set_markup("<i>%s</i>" %(txt,))

            def _do_end(self, amount_read, now=None):
                self.current += 1
                self.pbar.set_fraction(self.current / self.total)

            def update(self, amount_read, now=None):
                urlgrabber.progress.BaseMeter.update(self, amount_read, now)
                
            def _do_update(self, amount_read, now=None):
                if self.size is None:
                    return
                pct = float(amount_read) / self.size
                curval = self.pbar.get_fraction()
                newval = (pct * 1/self.total) + (self.current / self.total)
                if newval > curval + 0.001 or time.time() > self.last + 0.5:
                    self.pbar.set_fraction(newval)
                    _runGtkMain()
                    self.last = time.time()

        def downloadErrorDialog(mainwin, secondary, details = None):
            d = GuiDetailsDialog(mainwin, gtk.MESSAGE_ERROR,
                                   [('gtk-ok', gtk.RESPONSE_OK)],
                                   _("Error downloading packages"),
                                   secondary)
            if details:
                d.set_details("%s" %(details,))
            d.run()
            d.destroy()
            raise GuiDownloadError


        dlpkgs = map(lambda x: x.po, filter(lambda txmbr:
                                            txmbr.ts_state in ("i", "u"),
                                            self.tsInfo.getMembers()))       
        
        pbar = GuiProgress(_("Downloading packages"), mainwin)
        dlCb = dlcb(pbar, dlpkgs)
        self.repos.setProgressBar(dlCb)
        pbar.show()       
        
        try:
            probs = self.downloadPkgs(dlpkgs)
        except yum.Errors.RepoError, errmsg:
            downloadErrorDialog(mainwin, secondary = None, details = errmsg)
        except IndexError:
            downloadErrorDialog(mainwin, _("Unable to find a suitable mirror."))
            
        self.repos.setProgressBar(None)
        pbar.destroy()

        if len(probs.keys()) > 0:
            errstr = []
            for key in probs.keys():
                errors = yum.misc.unique(probs[key])
                for error in errors:
                    errstr.append("%s: %s" %(key, error))

            try:
                downloadErrorDialog(mainwin, _("Errors were encountered while "
                                           "downloading packages."),
                                details = string.join(errstr, "\n"))
            except GuiDownloadError:
                pass
        return dlpkgs

    def checkSignatures(self, pkgs, mainwin):
        def keyImportCallback(keydict):
            po = keydict["po"]
            userid = keydict["userid"]
            hexkeyid = keydict["hexkeyid"]
            keyurl = keydict["keyurl"]
            
            d = gtk.MessageDialog(mainwin, gtk.DIALOG_MODAL,
                                  gtk.MESSAGE_QUESTION,
                                  message_format = _("Import key?"))
            sec = _("The package %s is signed with a key "
                  "%s (0x%s) from %s.  Would you like to "
                  "import this key?") %(po, userid, hexkeyid, keyurl)
            d.format_secondary_text(sec)
            b = d.add_button('gtk-cancel', gtk.RESPONSE_CANCEL)
            b = d.add_button(_("_Import key"), gtk.RESPONSE_OK)
            b.set_image(gtk.image_new_from_stock(gtk.STOCK_OK,
                                                 gtk.ICON_SIZE_BUTTON))
            rc = d.run()
            d.destroy()
        
            if rc != gtk.RESPONSE_OK:
                return False
            return True

        
        pbar = GuiProgress(_("Verifying packages"), mainwin)
        num = float(len(pkgs))
        i = 1
        for po in pkgs:
            result, errmsg = self.sigCheckPkg(po)
            pbar.set_fraction(i / num)
            i+=1

            if result == 0:
                continue
            elif result == 1:
                found = True
                try:
                    self.getKeyForPackage(po, fullaskcb = keyImportCallback)
                except yum.Errors.YumBaseError, errmsg:
                    found = False
                if found:
                    continue            

            d = GuiDetailsDialog(mainwin, gtk.MESSAGE_ERROR,
                                   text = _("Unable to verify %s") %(po,))
            d.set_details("%s" %(errmsg,))

            if not self.unsignedok:
                pbar.destroy()
                d.add_button(_("_Close"), gtk.RESPONSE_CLOSE, 'gtk-close')
            else:
                d.format_secondary_markup(_("Malicious software can damage "
                                            "your computer or cause other "
                                            "harm.  Are you sure you wish "
                                            "to install this package?"))
                b = d.add_button(_("_Cancel"), gtk.RESPONSE_CANCEL,
                                 'gtk-cancel')
                b = d.add_button(_("_Install anyway"), gtk.RESPONSE_OK,
                                 'gtk-ok')
                d.set_default_response(gtk.RESPONSE_CANCEL)
            rc = d.run()
            d.destroy()
            if rc != gtk.RESPONSE_OK:
                raise GuiVerifyError
            
        pbar.destroy()
        
    def runTransaction(self, mainwin):
        def transactionErrors(errs):
            d = GuiDetailsDialog(mainwin, gtk.MESSAGE_ERROR,
                                          buttons = [('gtk-ok', 0)],
                                          text = _("Error updating software"))
            d.format_secondary_text(_("There were errors encountered in "
                                      "trying to update the software "
                                      "you selected"))
            d.set_details("%s" %(errs,))
            d.run()
            d.destroy()  
        
        pbar = GuiProgress(_("Updating software"), mainwin)
        tsprog = GuiTransactionProgress(pbar)

        del self.ts
        self.initActionTs() 
        self.populateTs(keepold=0)
        self.ts.check() 
        self.ts.order() 

        tsprog.tsInfo = self.tsInfo

        pbar.show()
        try:
            tserrors = yum.YumBase.runTransaction(self, tsprog)
        except yum.Errors.YumBaseError, err:            
            pbar.destroy()
            transactionErrors(err)
            raise GuiError
        except GuiError, err:
            pbar.destroy()
            transactionErrors(err)
            raise GuiError
                                 
        pbar.destroy()

    def install_language(self, mainWindow, grpid):            

        # download and verify packages
        dlpkgs = self.downloadPackages(mainWindow)
        try:
            self.checkSignatures(dlpkgs, mainWindow)
        except GuiVerifyError:
            str = _(" Error installing Selected Language packages: Do you still want to install language without proper support?")
            d= gtk.MessageDialog(mainWindow, gtk.DIALOG_MODAL,
                                      gtk.MESSAGE_QUESTION,
                                      message_format = str)              
            b = d.add_button(_("No"), gtk.RESPONSE_CANCEL)
            b = d.add_button(_("Yes"), gtk.RESPONSE_OK)    
            d.set_default_response(gtk.RESPONSE_OK)
            rc = d.run()
            d.destroy() 
            if rc != gtk.RESPONSE_OK:
                gtk.main_quit()
            else:
                lb=language_backend.LanguageBackend()
                ld=lang_dict.languages_Dict
                for (key, val) in ld.iteritems():
                    if ld[key]==grpid:
                        lb.originalFile=None
                        lb.writeI18N(key, "", "latarcyrheb-sun16", "utf8")
                        # send message to login manager to re-read config / pick up lang change
                        if os.access("/var/gdm/.gdmfifo", os.F_OK):
                            try:
                                fd = os.open("/tmp/.gdm_socket", os.O_WRONLY | os.O_APPEND | os.O_NONBLOCK)
                                if fd >= 0:
                                    os.write(fd, "\nUPDATE_CONFIG\n")
                                    os.close(fd)
                            except:
                                pass
		gtk.main_quit()

        # run transaction
        self.runTransaction(mainWindow)      
  




	
		
        

	

	
	
	
	
	
	

    
    	
    	
	
	
       


 






