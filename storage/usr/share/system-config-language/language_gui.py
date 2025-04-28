#!/usr/bin/python

## language_gui.py - Contains the UI code needed for system-config-language
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 Red Hat, Inc.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 Brent Fox <bfox@redhat.com>

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

import string
import gtk
import gtk.gdk
import gobject
import sys, os
sys.path.append('/usr/share/system-config-language/')
import language_backend
import lang_dict  
import gui_install

from gui_errors import * 

##
## I18N
## 
import gettext
_ = lambda x: gettext.ldgettext("system-config-language", x)
N_ = lambda x: x

##
## Icon for windows
##

iconPixbuf = None      
try:
    iconPixbuf = gtk.gdk.pixbuf_new_from_file("/usr/share/icons/gnome/32x32/apps/preferences-desktop-locale.png")
except:
    pass

class childWindow:
    #You must specify a runPriority for the order in which you wish your module to run
    runPriority = 0
    moduleName = _("Language")
    moduleClass = "reconfig"
    nameTag = _("Language Selection")
    commentTag = _("Change the default system language")

    def destroy(self, args):
        gtk.main_quit()
    
    def __init__(self):
        self.doDebug = None
        self.firstboot = None
        self.languageBackend = language_backend.LanguageBackend()
        self.toplevel = gtk.VBox()
        self.iconBox = gtk.HBox()
        self.langStore = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING,
                                       gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.title = gtk.Label(_("Language Selection"))
        self.title.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse ("white"))

        self.msgLabel = gtk.Label(_("Please select the default language for the system."))
        self.msgLabel.set_line_wrap(True)
        self.msgLabel.set_alignment(0.0, 0.5)
        self.msgLabel.set_padding(7,0)

        defaultLang, self.installedLangs = self.languageBackend.getInstalledLangs()        
        self.originalLang = defaultLang
        self.fillStore()

        self.langView = gtk.TreeView(self.langStore)
        self.langViewSW = gtk.ScrolledWindow()
        self.langViewSW.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.langViewSW.set_shadow_type(gtk.SHADOW_IN)
        self.langViewSW.add(self.langView)
        self.col = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=3)        
        self.langView.append_column(self.col)
        self.langView.set_property("headers-visible", False)

        self.langChangedFlag = 0
        self.setDefault(defaultLang)

        self.langView.get_selection().connect("changed", self.langChanged)

        #Add icon to the top frame
        p = None
        try:
            p = gtk.gdk.pixbuf_new_from_file("/usr/share/icons/gnome/32x32/apps/preferences-desktop-locale.png")
        except:
            try:
                p = gtk.gdk.pixbuf_new_from_file("/usr/share/icons/gnome/32x32/apps/preferences-desktop-locale.png")
            except:
                pass

        if p:
            self.icon = gtk.Image()
            self.icon.set_from_pixbuf(p)

    def listScroll(self, widget, *args):
        # recenter the list
        rc = self.langView.get_selection().get_selected()
        if rc is None:
            return
        model, iter = rc
        
        path = self.langStore.get_path(iter)
        col = self.langView.get_column(0)
        self.langView.scroll_to_cell(path, col, True, 0.5, 0.5)

    def setDefault(self, defaultLang):
        iter = self.langStore.get_iter_first()
        while iter:
            langBase = self.languageBackend.removeEncoding(self.langStore.get_value(iter, 0))
            if langBase == defaultLang:
                path = self.langStore.get_path(iter)
                self.langView.set_cursor(path, self.col, False)
                self.langView.scroll_to_cell(path, self.col, True, 0.5, 0.5)
                break
            iter = self.langStore.iter_next(iter)

    def fillStore(self):
        lines = self.languageBackend.readTable()

        #If /etc/sysconfig/i18n file is empty for some reason, assume English is the only lang
        if self.originalLang == None:
            iter = self.langStore.append()
            self.langStore.set_value(iter, 0, 'en_US.UTF-8')
            self.langStore.set_value(iter, 1, 'iso01')
            self.langStore.set_value(iter, 2, 'lat0-sun16')
            self.langStore.set_value(iter, 3, 'English (USA)')
            self.installedLangs = ['en_US.UTF-8:en']
            return

        for line in lines:
            tokens = string.split(line)
            if self.installedLangs == None:
                iter = self.langStore.append()
                self.langStore.set_value(iter, 0, tokens[0])
                self.langStore.set_value(iter, 1, tokens[1])
                self.langStore.set_value(iter, 2, tokens[2])
                name = ""
                for token in tokens[3:]:
                    name = name + " " + token
                self.langStore.set_value(iter, 3, name)            

            else:
                if '.' in tokens[0]:
                    #Chop encoding off so we can compare to self.installedLangs
                    langBase = self.languageBackend.removeEncoding(tokens[0])

                    if langBase in self.installedLangs:
                        iter = self.langStore.append()
                        self.langStore.set_value(iter, 0, tokens[0])
                        self.langStore.set_value(iter, 1, tokens[1])
                        self.langStore.set_value(iter, 2, tokens[2])
                        name = ""
                        for token in tokens[3:]:
                            name = name + " " + token
                        self.langStore.set_value(iter, 3, name)
   
    def langChanged(self, *args):
        self.langChangedFlag = 1
	self.okButton.set_sensitive(True)

    def okClicked(self, *args):
        self.apply()
        gtk.main_quit()

    def restoreClicked(self, *args):
        #Get the lang from the list of languages
        rc = self.langView.get_selection().get_selected()
        if rc:
            model, iter = rc
            defaultLang =  self.langStore.get_value(iter, 0)
            sysfontacm = self.langStore.get_value(iter, 1)
            sysfont = self.langStore.get_value(iter, 2)
            fullName = self.langStore.get_value(iter, 3)

	if defaultLang=="en_US.UTF-8":
        	dlg = gtk.MessageDialog(self.mainWindow, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
        	(_("Already system in default language,\nNothing to do.")))
		dlg.run()
        	dlg.destroy()
        	return 1


        str = _("Do you really want to change system language to default [en_US]?")                
        d = gtk.MessageDialog(self.mainWindow, gtk.DIALOG_MODAL,
        		gtk.MESSAGE_QUESTION,
        		message_format = str)
                                  
        b = d.add_button(_("No"), gtk.RESPONSE_CANCEL)
        b = d.add_button(_("Yes"), gtk.RESPONSE_OK)    
        d.set_default_response(gtk.RESPONSE_OK)
        rc = d.run()
        d.destroy() 
            
        if rc == gtk.RESPONSE_OK:                               
        	is_RepoError = True 
        	defaultLang= "en_US"
		self.setDefault(defaultLang)
        else:
        	return -1


    def helpClicked(self, args):
            dlg = gtk.MessageDialog(self.mainWindow, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                    (_("system-config-language is a graphical user interface that allows the user to change the default language of the system.")))
            dlg.run()
            dlg.destroy()
            return 1

    def apply(self, *args):
        if self.doDebug:
            return 0

        if not self.langChangedFlag:
            #If the user didn't actually change the lang when in the app, then just return 1
            return 0

        #Get the lang from the list of languages
        rc = self.langView.get_selection().get_selected()
        if rc:
            model, iter = rc
            defaultLang =  self.langStore.get_value(iter, 0)
            sysfontacm = self.langStore.get_value(iter, 1)
            sysfont = self.langStore.get_value(iter, 2)
            fullName = self.langStore.get_value(iter, 3)

        is_RepoError = False;          
        
        grpid = lang_dict.get_groupID_from_language(defaultLang)       
         
        if not grpid == "none": 
            try:       
                install = gui_install.guiInstall()
            except RepoErrors:
                    str = _("The Network or the Repos of Yum has some problems, do you want to continue?\n'Yes' will change the language but not install it.\n'No' will exit without changing the language.")                
                               
                    d = gtk.MessageDialog(self.mainWindow, gtk.DIALOG_MODAL,
                                      gtk.MESSAGE_QUESTION,
                                      message_format = str)
                                  
                    b = d.add_button(_("No"), gtk.RESPONSE_CANCEL)
                    b = d.add_button(_("Yes"), gtk.RESPONSE_OK)    
                    d.set_default_response(gtk.RESPONSE_OK)
                    rc = d.run()
                    d.destroy() 
            
                    if rc == gtk.RESPONSE_OK:                               
                        is_RepoError = True 
                    else:
                        return -1               
                                       
            if not is_RepoError:   
                if not install.is_group_installed(grpid, self.mainWindow):
                    install.selectGroup(grpid)
                
                    # do depsolve.  determine if we've added anything or not.
                    install.checkDeps(self.mainWindow)
                    install.depDetails(self.mainWindow)
                    
                    
                    dlpkgs = map(lambda x: x.po, filter(lambda txmbr:txmbr.ts_state in ("i", "u"),install.tsInfo.getMembers()))
		    
		    if len(dlpkgs)!=0:
                    	str = _(" language support is not installed, do you want to install it?")                
                    	str = grpid[:-8] + str
                    	str = str.capitalize()
            
                    	d = gtk.MessageDialog(self.mainWindow, gtk.DIALOG_MODAL,
                                      gtk.MESSAGE_QUESTION,
                                      message_format = str)
                                  
                    	b = d.add_button(_("No"), gtk.RESPONSE_CANCEL)
                    	b = d.add_button(_("Yes"), gtk.RESPONSE_OK)    
                    	d.set_default_response(gtk.RESPONSE_OK)
                    	rc = d.run()
                    	d.destroy() 
            
                    	if rc == gtk.RESPONSE_OK:                               
                        	install.install_language (self.mainWindow, grpid)                           
		    else:
			pass	

        if self.installedLangs == None:
            self.languageBackend.writeI18N(defaultLang, "", sysfont, sysfontacm)

        else:
            modules = self.installedLangs[0]
            for lang in self.installedLangs[1:]:
                modules = modules + ":" + lang

            self.languageBackend.writeI18N(defaultLang, modules, sysfont, sysfontacm)

        #If the language selection has changed, then apply the changes
        if self.firstboot:
            #If running in firstboot mode, allow firstboot to change the current locale
            self.firstboot.changeLocale(defaultLang, fullName)
        else:
            #Else, we're not in firstboot mode, so show the dialog
            dlg = gtk.MessageDialog(self.mainWindow, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                    _("The changes will take effect the next time you log in."))
            dlg.set_border_width(6)
            dlg.set_modal(True)
            rc = dlg.run()
            dlg.destroy()
            
        # send message to login manager to re-read config / pick up lang change
        if os.access("/var/gdm/.gdmfifo", os.F_OK):
            try:
                fd = os.open("/tmp/.gdm_socket",
                             os.O_WRONLY | os.O_APPEND | os.O_NONBLOCK)
                if fd >= 0:
                    os.write(fd, "\nUPDATE_CONFIG\n")
                    os.close(fd)
            except:
                pass

        return 0

    def setKickstartData(self, kickstartData):
        #Get the lang from the list of languages
        rc = self.langView.get_selection().get_selected()
        if rc:
            model, iter = rc
            defaultLang =  self.langStore.get_value(iter, 0)

        try:
            prefix, suffix = string.split(defaultLang, ".")
            defaultLang = prefix
        except:
            pass

        kickstartData.setDefaultLang(defaultLang)
        return 0

    def setKickstartDefaults(self, kickstartData):
        pass

    def passInParent(self, parent):
        self.firstboot = parent

    def launch(self, doDebug = None):
        self.doDebug = doDebug

        self.mainVBox = gtk.VBox()
        self.internalVBox = gtk.VBox(False, 10)
        self.internalVBox.set_border_width(10)

        self.msgLabel.set_size_request(500, -1)
        self.internalVBox.pack_start(self.msgLabel, False)
        self.internalVBox.pack_start(self.langViewSW)
        self.mainVBox.pack_start(self.internalVBox, True)
        return self.mainVBox, self.icon, self.moduleName

    def stand_alone(self):
        self.mainWindow = gtk.Window()
        self.mainWindow.connect("destroy", self.destroy)
        self.mainWindow.set_title(_("Language Selection"))
        self.mainWindow.set_icon(iconPixbuf)        
        self.screen=self.mainWindow.get_screen()
        self.screenwidth= self.screen.get_width()
        self.screenheight= self.screen.get_height()
        if self.screenheight <= 600:
            self.mainWindow.set_size_request(-1, int(self.screenheight*0.9))
        else:
            self.mainWindow.set_size_request(-1, 600)
        self.mainWindow.set_border_width(12)        

        self.bb = gtk.HButtonBox()
        self.bb.set_layout(gtk.BUTTONBOX_END)
        self.bb.set_spacing(12)

        self.sdButton = gtk.Button(_("System _Defaults"), None, True)
        self.sdButton.connect("clicked", self.restoreClicked)
        self.bb.pack_start(self.sdButton)

        self.cancelButton = gtk.Button(stock='gtk-cancel')
        self.cancelButton.connect("clicked", self.destroy)
        self.bb.pack_start(self.cancelButton)

        self.okButton = gtk.Button(stock='gtk-ok')
	self.okButton.set_sensitive(False)
        self.okButton.connect("clicked", self.okClicked)
        self.bb.pack_start(self.okButton)


        self.helpButton = gtk.Button(stock='gtk-help')
        self.helpButton.connect("clicked", self.helpClicked)
        self.bb.pack_start(self.helpButton)
	self.bb.set_child_secondary(self.helpButton, True)

        self.toplevel.set_spacing(12)

        self.iconBox.pack_start(self.icon, False)
        self.iconBox.pack_start(self.msgLabel)
        self.toplevel.pack_start(self.iconBox, False)
        self.toplevel.pack_start(self.langViewSW)
        self.toplevel.pack_start(gtk.HSeparator(), False)
        self.toplevel.pack_start(self.bb, False)
        self.mainWindow.add(self.toplevel)
        self.mainWindow.show_all()
        gtk.main()
