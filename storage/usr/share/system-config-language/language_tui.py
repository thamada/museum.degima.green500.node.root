## language_tui.py: text mode language selection dialog
## Copyright 2002, 2003 Red Hat, Inc.
## Copyright (C) 2002, 2003 Brent Fox <bfox@redhat.com>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


from snack import *
import os
import locale
import language_backend
import lang_dict
import tui_install
from gui_errors import *

locale.setlocale(locale.LC_ALL, "")
import gettext
_ = lambda x: gettext.ldgettext("system-config-language", x)
N_ = lambda x: x
gettext.bind_textdomain_codeset("system-config-language", locale.nl_langinfo(locale.CODESET))

languageBackend = language_backend.LanguageBackend()

class LanguageWindow:
    def __call__(self, screen):

        defaultLang, self.installedLangs = languageBackend.getInstalledLangs()
        self.langDict = {}

        bb = ButtonBar(screen, ["Yes", "No"])
        textBox = TextboxReflowed(40, 
                _("Select the language for the system."))

        list = self.populateListBox(defaultLang)
        g = GridFormHelp(screen, _("Language Selection"), "kbdtype", 1, 4)
        g.add(textBox, 0, 0)
        g.add(list, 0, 1, padding = (0, 1, 0, 1))
        g.add(bb, 0, 3, growx = 1)

        rc = g.runOnce()

        button = bb.buttonPressed(rc)

        if button == "no":
            return -1

        choice = list.current()
        defaultLang, sysfontacm, sysfont = self.langDict[choice]
        
        is_RepoError = False;
        grpid = lang_dict.get_groupID_from_language(defaultLang)
        if not grpid == "none":
            screen.finish() 
            try:    
                install = tui_install.tuiInstall()  
            except RepoErrors:                 
                str = _("The Network or the Repos of Yum has some problems, do you want to continue?\n'Yes' will change the language but not install it.\n'No' will exit without changing the language.")               
                               
                screen = SnackScreen()             
                bb2 = ButtonBar(screen, ["OK", "Cancel"])
                textBox2 = TextboxReflowed(40, str)
                g2 = GridFormHelp(screen, _("Installing Confirm"), "kbdtype", 1, 4)
                g2.add(textBox2, 0, 0)                
                g2.add(bb2, 0, 3, growx = 1)

                rc2 = g2.runOnce()

                button2 = bb2.buttonPressed(rc2)
                                
                if button2 == "ok":     
                    is_RepoError = True 
                else:
                    return -1                       
        
            if not is_RepoError:
                if not install.is_group_installed(grpid):
                    str = _(" language support is not installed, do you want to install it?")
                    str = grpid[:-8] + str   
                    str = str.capitalize()
                    screen = SnackScreen()             
                    bb2 = ButtonBar(screen, ["OK", "Cancel"])
                    textBox2 = TextboxReflowed(40, str)
                    g2 = GridFormHelp(screen, _("Installing Confirm"), "kbdtype", 1, 4)
                    g2.add(textBox2, 0, 0)                
                    g2.add(bb2, 0, 3, growx = 1)

                    rc2 = g2.runOnce()

                    button2 = bb2.buttonPressed(rc2)
                                
                    if button2 == "ok":     
                        screen.finish()                                 
                        install.install_language (grpid)

        if self.installedLangs == None:
            languageBackend.writeI18N(defaultLang, "", sysfont, sysfontacm)
        else:
            modules = self.installedLangs[0]
            for lang in self.installedLangs[1:]:
                modules = modules + ":" + lang

            languageBackend.writeI18N(defaultLang, modules, sysfont, sysfontacm)

    def populateListBox(self, defaultLang):
        list = Listbox(8, scroll = 1, returnExit = 0)

        lines = languageBackend.readTable()

        if defaultLang == None:
            list.append('English (USA)', 'en_US.UTF-8')
            self.installedLangs = ['en_US.UTF-8:en']
            list.setCurrent("en_US.UTF-8")
            return list


        default = ""
        for line in lines:
            tokens = string.split(line)

            if self.installedLangs == None:
                langBase = languageBackend.removeEncoding(tokens[0])                
                name = ""
                for token in tokens[3:]:
                    name = name + " " + token

                    if languageBackend.removeEncoding(defaultLang) == langBase:
                        default = tokens[0]

                list.append(name, tokens[0])
                self.langDict[tokens[0]] = (tokens[0], tokens[1], tokens[2])

            else:
                if '.' in tokens[0]:
                    #Chop encoding off so we can compare to self.installedLangs
                    langBase = languageBackend.removeEncoding(tokens[0])
                    if langBase in self.installedLangs:
                        name = ""
                        for token in tokens[3:]:
                            name = name + " " + token

                        if languageBackend.removeEncoding(defaultLang) == langBase:
                            default = tokens[0]

                        list.append(name, tokens[0])
                        self.langDict[tokens[0]] = (tokens[0], tokens[1], tokens[2])                        
        

        list.setCurrent(default)
        return list

            
class childWindow:
    def __init__(self):
        screen = SnackScreen()
	screen.drawRootText (0, 0, "system-config-language - (C) 2004 Red Hat, Inc.");

        DONE = 0

        while not DONE:

            rc = LanguageWindow()(screen)
            if rc == -1:
                screen.finish()
                DONE = 1
            else:
                screen.finish()
                self.runConfig(rc)
                DONE = 1
                
    def runConfig(self, rc):
        pass
