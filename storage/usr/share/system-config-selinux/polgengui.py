#!/usr/bin/python -E
#
# polgengui.py - GUI for SELinux Config tool in system-config-selinux
#
# Dan Walsh <dwalsh@redhat.com>
#
# Copyright 2007, 2008, 2009 Red Hat, Inc.
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
import signal
import string
import gtk
import gtk.glade
import os
import gobject
import gnome
import sys
import polgen
import re
import commands


##
## I18N
## 
PROGNAME="policycoreutils"

import gettext
gettext.bindtextdomain(PROGNAME, "/usr/share/locale")
gettext.textdomain(PROGNAME)
try:
    gettext.install(PROGNAME,
                    localedir="/usr/share/locale",
                    unicode=False,
                    codeset = 'utf-8')
except IOError:
    import __builtin__
    __builtin__.__dict__['_'] = unicode

gnome.program_init("SELinux Policy Generation Tool", "5")

version = "1.0"

sys.path.append('/usr/share/system-config-selinux')
sys.path.append('.')

# From John Hunter http://www.daa.com.au/pipermail/pygtk/2003-February/004454.html
def foreach(model, path, iter, selected):
    selected.append(model.get_value(iter, 0))

##
## Pull in the Glade file
##
if os.access("polgen.glade", os.F_OK):
    xml = gtk.glade.XML ("polgen.glade", domain=PROGNAME)
else:
    xml = gtk.glade.XML ("/usr/share/system-config-selinux/polgen.glade", domain=PROGNAME)

FILE = 1
DIR = 2

class childWindow:
    START_PAGE = 0
    SELECT_TYPE_PAGE = 1
    APP_PAGE = 2
    EXISTING_USER_PAGE = 3
    TRANSITION_PAGE = 4
    USER_TRANSITION_PAGE = 5
    ADMIN_PAGE = 6
    ROLE_PAGE = 7
    IN_NET_PAGE = 8
    OUT_NET_PAGE = 9
    COMMON_APPS_PAGE = 10
    FILES_PAGE = 11
    BOOLEAN_PAGE = 12
    SELECT_DIR_PAGE = 13
    GEN_POLICY_PAGE = 14
    GEN_USER_POLICY_PAGE = 15
    
    def __init__(self):
        self.xml = xml
        self.all_types=polgen.get_all_types()
        self.all_modules=polgen.get_all_modules()
        self.name=""
        xml.signal_connect("on_delete_clicked", self.delete)
        xml.signal_connect("on_delete_boolean_clicked", self.delete_boolean)
        xml.signal_connect("on_exec_select_clicked", self.exec_select)
        xml.signal_connect("on_init_script_select_clicked", self.init_script_select)
        xml.signal_connect("on_add_clicked", self.add)
        xml.signal_connect("on_add_boolean_clicked", self.add_boolean)
        xml.signal_connect("on_add_dir_clicked", self.add_dir)
        xml.signal_connect("on_about_clicked", self.on_about_clicked)
        xml.get_widget ("cancel_button").connect("clicked",self.quit)
        self.forward_button = xml.get_widget ("forward_button")
        self.forward_button.connect("clicked",self.forward)
        self.back_button = xml.get_widget ("back_button")
        self.back_button.connect("clicked",self.back)

        self.boolean_dialog = xml.get_widget ("boolean_dialog")
        self.boolean_name_entry = xml.get_widget ("boolean_name_entry")
        self.boolean_description_entry = xml.get_widget ("boolean_description_entry")

        self.notebook = xml.get_widget ("notebook1")
        self.pages={}
        self.finish_page = [ self.GEN_POLICY_PAGE, self.GEN_USER_POLICY_PAGE ]
        for i in polgen.USERS:
            self.pages[i] = [ self.START_PAGE, self.SELECT_TYPE_PAGE, self.APP_PAGE, self.TRANSITION_PAGE, self.ROLE_PAGE, self.IN_NET_PAGE, self.OUT_NET_PAGE, self.BOOLEAN_PAGE, self.SELECT_DIR_PAGE, self.GEN_USER_POLICY_PAGE] 
        self.pages[polgen.RUSER] = [ self.START_PAGE, self.SELECT_TYPE_PAGE, self.APP_PAGE,  self.ADMIN_PAGE, self.USER_TRANSITION_PAGE, self.IN_NET_PAGE, self.OUT_NET_PAGE, self.BOOLEAN_PAGE, self.SELECT_DIR_PAGE, self.GEN_USER_POLICY_PAGE]
        self.pages[polgen.LUSER] = [ self.START_PAGE, self.SELECT_TYPE_PAGE, self.APP_PAGE, self.TRANSITION_PAGE, self.IN_NET_PAGE, self.OUT_NET_PAGE, self.BOOLEAN_PAGE, self.SELECT_DIR_PAGE, self.GEN_USER_POLICY_PAGE] 

        self.pages[polgen.EUSER] = [ self.START_PAGE, self.SELECT_TYPE_PAGE, self.EXISTING_USER_PAGE, self.TRANSITION_PAGE, self.ROLE_PAGE, self.IN_NET_PAGE, self.OUT_NET_PAGE, self.BOOLEAN_PAGE, self.SELECT_DIR_PAGE, self.GEN_USER_POLICY_PAGE] 

        for i in polgen.APPLICATIONS:
            self.pages[i] = [ self.START_PAGE, self.SELECT_TYPE_PAGE, self.APP_PAGE, self.IN_NET_PAGE, self.OUT_NET_PAGE, self.COMMON_APPS_PAGE, self.FILES_PAGE, self.BOOLEAN_PAGE, self.SELECT_DIR_PAGE, self.GEN_POLICY_PAGE]
        self.pages[polgen.USER] = [ self.START_PAGE, self.SELECT_TYPE_PAGE, self.APP_PAGE, self.USER_TRANSITION_PAGE, self.IN_NET_PAGE, self.OUT_NET_PAGE, self.COMMON_APPS_PAGE, self.FILES_PAGE, self.BOOLEAN_PAGE, self.SELECT_DIR_PAGE, self.GEN_POLICY_PAGE]
        
        self.current_page = 0
        self.back_button.set_sensitive(0)

        self.network_buttons = {}

        self.in_tcp_all_checkbutton = xml.get_widget ("in_tcp_all_checkbutton")
        self.in_tcp_reserved_checkbutton = xml.get_widget ("in_tcp_reserved_checkbutton")
        self.in_tcp_unreserved_checkbutton = xml.get_widget ("in_tcp_unreserved_checkbutton")
        self.in_tcp_entry = self.xml.get_widget("in_tcp_entry")
        self.network_buttons[self.in_tcp_all_checkbutton] = [ self.in_tcp_reserved_checkbutton, self.in_tcp_unreserved_checkbutton, self.in_tcp_entry ]


        self.out_tcp_all_checkbutton = xml.get_widget ("out_tcp_all_checkbutton")
        self.out_tcp_reserved_checkbutton = xml.get_widget ("out_tcp_reserved_checkbutton")
        self.out_tcp_unreserved_checkbutton = xml.get_widget ("out_tcp_unreserved_checkbutton")
        self.out_tcp_entry = self.xml.get_widget("out_tcp_entry")

        self.network_buttons[self.out_tcp_all_checkbutton] = [ self.out_tcp_entry ]

        self.in_udp_all_checkbutton = xml.get_widget ("in_udp_all_checkbutton")
        self.in_udp_reserved_checkbutton = xml.get_widget ("in_udp_reserved_checkbutton")
        self.in_udp_unreserved_checkbutton = xml.get_widget ("in_udp_unreserved_checkbutton")
        self.in_udp_entry = self.xml.get_widget("in_udp_entry")

        self.network_buttons[self.in_udp_all_checkbutton] = [ self.in_udp_reserved_checkbutton, self.in_udp_unreserved_checkbutton, self.in_udp_entry ]

        self.out_udp_all_checkbutton = xml.get_widget ("out_udp_all_checkbutton")
        self.out_udp_entry = self.xml.get_widget("out_udp_entry")
        self.network_buttons[self.out_udp_all_checkbutton] = [ self.out_udp_entry ]

        for b in self.network_buttons.keys():
            b.connect("clicked",self.network_all_clicked)

        self.boolean_treeview = self.xml.get_widget("boolean_treeview")
        self.boolean_store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING)
        self.boolean_treeview.set_model(self.boolean_store)
        self.boolean_store.set_sort_column_id(0, gtk.SORT_ASCENDING)        
        col = gtk.TreeViewColumn(_("Name"), gtk.CellRendererText(), text = 0)
        self.boolean_treeview.append_column(col)
        col = gtk.TreeViewColumn(_("Description"), gtk.CellRendererText(), text = 1)
        self.boolean_treeview.append_column(col)

        self.role_treeview = self.xml.get_widget("role_treeview")
        self.role_store = gtk.ListStore(gobject.TYPE_STRING)
        self.role_treeview.set_model(self.role_store)
        self.role_treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.role_store.set_sort_column_id(0, gtk.SORT_ASCENDING)        
        col = gtk.TreeViewColumn(_("Role"), gtk.CellRendererText(), text = 0)
        self.role_treeview.append_column(col)

        self.existing_user_treeview = self.xml.get_widget("existing_user_treeview")
        self.existing_user_store = gtk.ListStore(gobject.TYPE_STRING)
        self.existing_user_treeview.set_model(self.existing_user_store)
        self.existing_user_store.set_sort_column_id(0, gtk.SORT_ASCENDING)        
        col = gtk.TreeViewColumn(_("Existing_User"), gtk.CellRendererText(), text = 0)
        self.existing_user_treeview.append_column(col)

        roles = polgen.get_all_roles()
        for i in roles:
            iter = self.role_store.append()
            self.role_store.set_value(iter, 0, i[:-2])

        self.types = polgen.get_all_types()

        self.transition_treeview = self.xml.get_widget("transition_treeview")
        self.transition_store = gtk.ListStore(gobject.TYPE_STRING)
        self.transition_treeview.set_model(self.transition_store)
        self.transition_treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.transition_store.set_sort_column_id(0, gtk.SORT_ASCENDING)        
        col = gtk.TreeViewColumn(_("Application"), gtk.CellRendererText(), text = 0)
        self.transition_treeview.append_column(col)

        self.user_transition_treeview = self.xml.get_widget("user_transition_treeview")
        self.user_transition_store = gtk.ListStore(gobject.TYPE_STRING)
        self.user_transition_treeview.set_model(self.user_transition_store)
        self.user_transition_treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.user_transition_store.set_sort_column_id(0, gtk.SORT_ASCENDING)        
        col = gtk.TreeViewColumn(_("Application"), gtk.CellRendererText(), text = 0)
        self.user_transition_treeview.append_column(col)

        for i in polgen.get_all_users():
            iter = self.user_transition_store.append()
            self.user_transition_store.set_value(iter, 0, i)
            iter = self.existing_user_store.append()
            self.existing_user_store.set_value(iter, 0, i)

        self.admin_treeview = self.xml.get_widget("admin_treeview")
        self.admin_store = gtk.ListStore(gobject.TYPE_STRING)
        self.admin_treeview.set_model(self.admin_store)
        self.admin_treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.admin_store.set_sort_column_id(0, gtk.SORT_ASCENDING)        
        col = gtk.TreeViewColumn(_("Application"), gtk.CellRendererText(), text = 0)
        self.admin_treeview.append_column(col)

        for i in polgen.methods:
            m = re.findall("(.*)%s" % polgen.USER_TRANSITION_INTERFACE, i) 
            if len(m) > 0:
                if "%s_exec" % m[0] in self.types:
                    iter = self.transition_store.append()
                    self.transition_store.set_value(iter, 0, m[0])
                continue

            m = re.findall("(.*)%s" % polgen.ADMIN_TRANSITION_INTERFACE, i) 
            if len(m) > 0:
                iter = self.admin_store.append()
                self.admin_store.set_value(iter, 0, m[0])
                continue
        
    def confine_application(self):
        return self.get_type() in polgen.APPLICATIONS

    def forward(self, arg):
        type = self.get_type()
        if self.current_page == self.START_PAGE:
            self.back_button.set_sensitive(1)

        if self.pages[type][self.current_page] == self.SELECT_TYPE_PAGE:
            if self.on_select_type_page_next():
                return

        if self.pages[type][self.current_page] == self.IN_NET_PAGE:
            if self.on_in_net_page_next():
                return

        if self.pages[type][self.current_page] == self.OUT_NET_PAGE:
            if self.on_out_net_page_next():
                return

        if self.pages[type][self.current_page] == self.APP_PAGE:
            if self.on_name_page_next():
                return

        if self.pages[type][self.current_page] == self.EXISTING_USER_PAGE:
            if self.on_existing_user_page_next():
                return

        if self.pages[type][self.current_page] == self.SELECT_DIR_PAGE:
            outputdir = self.output_entry.get_text()
            if not os.path.isdir(outputdir):
                self.error(_("%s must be a directory") % outputdir )
                return False
            
        if self.pages[type][self.current_page] in self.finish_page:
            self.generate_policy()
            self.xml.get_widget ("cancel_button").set_label(gtk.STOCK_CLOSE)
        else:
            self.current_page = self.current_page + 1
            self.notebook.set_current_page(self.pages[type][self.current_page])
            if self.pages[type][self.current_page] in self.finish_page:
                self.forward_button.set_label(gtk.STOCK_APPLY)
        
    def back(self,arg):
        type = self.get_type()
        if self.pages[type][self.current_page] in self.finish_page:
            self.forward_button.set_label(gtk.STOCK_GO_FORWARD)

        self.current_page = self.current_page - 1 
        self.notebook.set_current_page(self.pages[type][self.current_page])
        if self.current_page == 0:
            self.back_button.set_sensitive(0)
        
    def network_all_clicked(self, button):
        active = button.get_active()
        for b in self.network_buttons[button]:
            b.set_sensitive(not active)
        
    def verify(self, message, title="" ):
        dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO,
                                gtk.BUTTONS_YES_NO,
                                message)
        dlg.set_title(title)
        dlg.set_position(gtk.WIN_POS_MOUSE)
        dlg.show_all()
        rc = dlg.run()
        dlg.destroy()
        return rc

    def info(self, message):
        dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO,
                                gtk.BUTTONS_OK,
                                message)
        dlg.set_position(gtk.WIN_POS_MOUSE)
        dlg.show_all()
        dlg.run()
        dlg.destroy()

    def error(self, message):
        dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR,
                                gtk.BUTTONS_CLOSE,
                                message)
        dlg.set_position(gtk.WIN_POS_MOUSE)
        dlg.show_all()
        dlg.run()
        dlg.destroy()

    def get_name(self):
        if self.existing_user_radiobutton.get_active():
            store, iter = self.existing_user_treeview.get_selection().get_selected()
            if iter == None:
                raise(_("You must select a user"))
            return store.get_value(iter, 0)
        else:
            return self.name_entry.get_text()

    def get_type(self):
        if self.cgi_radiobutton.get_active():
            return polgen.CGI
        if self.user_radiobutton.get_active():
            return polgen.USER
        if self.init_radiobutton.get_active():
            return polgen.DAEMON
        if self.dbus_radiobutton.get_active():
            return polgen.DBUS
        if self.inetd_radiobutton.get_active():
            return polgen.INETD
        if self.login_user_radiobutton.get_active():
            return polgen.LUSER
        if self.admin_user_radiobutton.get_active():
            return polgen.AUSER
        if self.xwindows_user_radiobutton.get_active():
            return polgen.XUSER
        if self.terminal_user_radiobutton.get_active():
            return polgen.TUSER
        if self.root_user_radiobutton.get_active():
            return polgen.RUSER
        if self.existing_user_radiobutton.get_active():
            return polgen.EUSER

    def generate_policy(self, *args):
        outputdir = self.output_entry.get_text()
        try:
            my_policy=polgen.policy(self.get_name(), self.get_type())
            my_policy.set_in_tcp(self.in_tcp_all_checkbutton.get_active(), self.in_tcp_reserved_checkbutton.get_active(), self.in_tcp_unreserved_checkbutton.get_active(), self.in_tcp_entry.get_text())
            my_policy.set_in_udp(self.in_udp_all_checkbutton.get_active(), self.in_udp_reserved_checkbutton.get_active(), self.in_udp_unreserved_checkbutton.get_active(), self.in_udp_entry.get_text())
            my_policy.set_out_tcp(self.out_tcp_all_checkbutton.get_active(), self.out_tcp_entry.get_text())
            my_policy.set_out_udp(self.out_udp_all_checkbutton.get_active(), self.out_udp_entry.get_text())

            iter= self.boolean_store.get_iter_first()
            while(iter):
                my_policy.add_boolean(self.boolean_store.get_value(iter, 0), self.boolean_store.get_value(iter, 1))
                iter= self.boolean_store.iter_next(iter)

            if self.get_type() in polgen.APPLICATIONS:
                my_policy.set_program(self.exec_entry.get_text())
                my_policy.set_use_syslog(self.syslog_checkbutton.get_active() == 1)
                my_policy.set_use_tmp(self.tmp_checkbutton.get_active() == 1)
                my_policy.set_use_uid(self.uid_checkbutton.get_active() == 1)
                my_policy.set_use_pam(self.pam_checkbutton.get_active() == 1)

                my_policy.set_use_dbus(self.dbus_checkbutton.get_active() == 1)
                my_policy.set_use_audit(self.audit_checkbutton.get_active() == 1)
                my_policy.set_use_terminal(self.terminal_checkbutton.get_active() == 1)
                my_policy.set_use_mail(self.mail_checkbutton.get_active() == 1)
                if self.get_type() is polgen.DAEMON:
                    my_policy.set_init_script(self.init_script_entry.get_text())
                if self.get_type() == polgen.USER:
                    selected = []
                    self.user_transition_treeview.get_selection().selected_foreach(foreach, selected)
                    my_policy.set_transition_users(selected)
            else:
                if self.get_type() == polgen.RUSER:
                    selected = []
                    self.admin_treeview.get_selection().selected_foreach(foreach, selected)
                    my_policy.set_admin_domains(selected)
                    selected = []
                    self.user_transition_treeview.get_selection().selected_foreach(foreach, selected)
                    my_policy.set_transition_users(selected)
                else:
                    selected = []
                    self.transition_treeview.get_selection().selected_foreach(foreach, selected)
                    my_policy.set_transition_domains(selected)
                
                    selected = []
                    self.role_treeview.get_selection().selected_foreach(foreach, selected)
                    my_policy.set_admin_roles(selected)
                
            iter= self.store.get_iter_first()
            while(iter):
                if self.store.get_value(iter, 1) == FILE:
                    my_policy.add_file(self.store.get_value(iter, 0))
                else:
                    my_policy.add_dir(self.store.get_value(iter, 0))
                iter= self.store.iter_next(iter)
                
            self.info(my_policy.generate(outputdir))
            return False
        except ValueError, e:
            self.error(e.message)
        
    def delete(self, args):
        store, iter = self.view.get_selection().get_selected()
        if iter != None:
            store.remove(iter)
            self.view.get_selection().select_path ((0,))

    def delete_boolean(self, args):
        store, iter = self.boolean_treeview.get_selection().get_selected()
        if iter != None:
            store.remove(iter)
            self.boolean_treeview.get_selection().select_path ((0,))

    def add_boolean(self,type):
        self.boolean_name_entry.set_text("")
        self.boolean_description_entry.set_text("")
        rc = self.boolean_dialog.run()
        self.boolean_dialog.hide()
        if rc == gtk.RESPONSE_CANCEL:
            return
        iter = self.boolean_store.append()
        self.boolean_store.set_value(iter, 0, self.boolean_name_entry.get_text())
        self.boolean_store.set_value(iter, 1, self.boolean_description_entry.get_text())
        
    def __add(self,type):
        rc = self.file_dialog.run()
        self.file_dialog.hide()
        if rc == gtk.RESPONSE_CANCEL:
            return
        for i in self.file_dialog.get_filenames():
            iter = self.store.append()
            self.store.set_value(iter, 0, i)
            self.store.set_value(iter, 1, type)
        
    def exec_select(self, args):
        self.file_dialog.set_select_multiple(0)
        self.file_dialog.set_title(_("Select executable file to be confined."))
        self.file_dialog.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
        self.file_dialog.set_current_folder("/usr/sbin")
        rc = self.file_dialog.run()
        self.file_dialog.hide()
        if rc == gtk.RESPONSE_CANCEL:
            return
        self.exec_entry.set_text(self.file_dialog.get_filename())

    def init_script_select(self, args):
        self.file_dialog.set_select_multiple(0)
        self.file_dialog.set_title(_("Select init script file to be confined."))
        self.file_dialog.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
        self.file_dialog.set_current_folder("/etc/rc.d/init.d")
        rc = self.file_dialog.run()
        self.file_dialog.hide()
        if rc == gtk.RESPONSE_CANCEL:
            return
        self.init_script_entry.set_text(self.file_dialog.get_filename())

    def add(self, args):
        self.file_dialog.set_title(_("Select file(s) that confined application creates or writes"))
        self.file_dialog.set_current_folder("/")
        self.file_dialog.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
        self.file_dialog.set_select_multiple(1)
        self.__add(FILE)

    def add_dir(self, args):
        self.file_dialog.set_title(_("Select directory(s) that the confined application owns and writes into"))
        self.file_dialog.set_current_folder("/")
        self.file_dialog.set_select_multiple(1)
        self.file_dialog.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        self.__add(DIR)
        
    def on_about_clicked(self, args):
        dlg = xml.get_widget ("about_dialog")
        dlg.run ()
        dlg.hide ()

    def quit(self, args):
        gtk.main_quit()

    def setupScreen(self):
        # Bring in widgets from glade file.
        self.mainWindow = self.xml.get_widget("main_window")
        self.druid = self.xml.get_widget("druid")
        self.type = 0
        self.name_entry = self.xml.get_widget("name_entry")
        self.name_entry.connect("focus_out_event",self.on_name_entry_changed)
        self.exec_entry = self.xml.get_widget("exec_entry")
        self.exec_button = self.xml.get_widget("exec_button")
        self.init_script_entry = self.xml.get_widget("init_script_entry")
        self.init_script_button = self.xml.get_widget("init_script_button")
        self.output_entry = self.xml.get_widget("output_entry")
        self.output_entry.set_text(os.getcwd())
        self.xml.get_widget("output_button").connect("clicked",self.output_button_clicked)
        
        self.xwindows_user_radiobutton = self.xml.get_widget("xwindows_user_radiobutton")
        self.terminal_user_radiobutton = self.xml.get_widget("terminal_user_radiobutton")
        self.root_user_radiobutton = self.xml.get_widget("root_user_radiobutton")
        self.login_user_radiobutton = self.xml.get_widget("login_user_radiobutton")
        self.admin_user_radiobutton = self.xml.get_widget("admin_user_radiobutton")
        self.existing_user_radiobutton = self.xml.get_widget("existing_user_radiobutton")

        self.user_radiobutton = self.xml.get_widget("user_radiobutton")
        self.init_radiobutton = self.xml.get_widget("init_radiobutton")
        self.inetd_radiobutton = self.xml.get_widget("inetd_radiobutton")
        self.dbus_radiobutton = self.xml.get_widget("dbus_radiobutton")
        self.cgi_radiobutton = self.xml.get_widget("cgi_radiobutton")
        self.tmp_checkbutton = self.xml.get_widget("tmp_checkbutton")
        self.uid_checkbutton = self.xml.get_widget("uid_checkbutton")
        self.pam_checkbutton = self.xml.get_widget("pam_checkbutton")
        self.dbus_checkbutton = self.xml.get_widget("dbus_checkbutton")
        self.audit_checkbutton = self.xml.get_widget("audit_checkbutton")
        self.terminal_checkbutton = self.xml.get_widget("terminal_checkbutton")
        self.mail_checkbutton = self.xml.get_widget("mail_checkbutton")
        self.syslog_checkbutton = self.xml.get_widget("syslog_checkbutton")
        self.view = self.xml.get_widget("write_treeview")
        self.file_dialog = self.xml.get_widget("filechooserdialog")

        self.store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT)
        self.view.set_model(self.store)
        col = gtk.TreeViewColumn("",  gtk.CellRendererText(), text = 0)
        col.set_resizable(True)
        self.view.append_column(col)
        self.view.get_selection().select_path ((0,))

    def output_button_clicked(self, *args):
        self.file_dialog.set_title(_("Select directory to generate policy files in"))
        self.file_dialog.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        self.file_dialog.set_select_multiple(0)
        rc = self.file_dialog.run()
        self.file_dialog.hide()
        if rc == gtk.RESPONSE_CANCEL:
            return
        self.output_entry.set_text(self.file_dialog.get_filename())
        
    def on_name_entry_changed(self, entry, third):
        name = entry.get_text()
        if self.name != name:
            if name in self.all_types:
                if self.verify(_("Type %s_t already defined in current policy.\nDo you want to continue?") % name, _("Verify Name")) == gtk.RESPONSE_NO:
                    entry.set_text("")
                    return False
            if name in self.all_modules:
                if self.verify(_("Module %s.pp already loaded in current policy.\nDo you want to continue?") % name, _("Verify Name")) == gtk.RESPONSE_NO:
                    entry.set_text("")
                    return False

            file = "/etc/rc.d/init.d/" + name
            if os.path.isfile(file) and self.init_script_entry.get_text() == "":
                self.init_script_entry.set_text(file)
                
            file = "/usr/sbin/" + name
            if os.path.isfile(file) and self.exec_entry.get_text() == "":
                self.exec_entry.set_text(file)

        self.name = name
        return False

    def on_in_net_page_next(self, *args):
        try:
            polgen.verify_ports(self.in_tcp_entry.get_text())
            polgen.verify_ports(self.in_udp_entry.get_text())
        except ValueError, e:
            self.error(e.message)
            return True
        
    def on_out_net_page_next(self, *args):
        try:
            polgen.verify_ports(self.out_tcp_entry.get_text())
            polgen.verify_ports(self.out_udp_entry.get_text())
        except ValueError, e:
            self.error(e.message)
            return True
        
    def on_select_type_page_next(self, *args):
        self.exec_entry.set_sensitive(self.confine_application())
        self.exec_button.set_sensitive(self.confine_application())
        self.init_script_entry.set_sensitive(self.init_radiobutton.get_active())
        self.init_script_button.set_sensitive(self.init_radiobutton.get_active())

    def on_existing_user_page_next(self, *args):
        store, iter = self.view.get_selection().get_selected()
        if iter != None:
            self.error(_("You must select a user"))
            return True
        
    def on_name_page_next(self, *args):
        name=self.name_entry.get_text()
        if name == "":
            self.error(_("You must enter a name"))
            return True
        
        if self.confine_application():
            exe = self.exec_entry.get_text()
            if exe == "":
                self.error(_("You must enter a executable"))
                return True

    def stand_alone(self):
        desktopName = _("Configue SELinux")

        self.setupScreen()
        self.mainWindow.connect("destroy", self.quit)

        self.mainWindow.show_all()
        gtk.main()

if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)

    app = childWindow()
    app.stand_alone()
