#!/usr/bin/python

## apache-config - A Python Apache configuration utility for
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


##
## I18N
##
import gettext
PROGNAME='system-config-httpd'
gettext.bindtextdomain(PROGNAME, "/usr/share/locale")
gettext.textdomain(PROGNAME)
try:
    gettext.install(PROGNAME, "/usr/share/locale", 1)
except IOError:
    import __builtin__
    __builtin__.__dict__['_'] = unicode

try:
    import gtk
except:
    import sys
    print (_("system-config-httpd requires a currently running X server."))
    sys.exit(0)

import gtk.gdk
import gtk.glade
import gnome
import gnome.ui
import signal
import re
import os

import ApacheGizmo
from CheckList import CheckList
from ApacheControl import ApacheControl, check_ip, check_port, TestError

gnome.program_init(PROGNAME, "1.4.5")
gtk.glade.bindtextdomain(PROGNAME, "/usr/share/locale")

##
## Global values
##

APACHECONFDIR='/usr/share/system-config-httpd/'
glade_file = "apache-config.glade"

if not os.path.isfile(glade_file):
    glade_file = APACHECONFDIR + glade_file

xml = gtk.glade.XML (glade_file, domain=PROGNAME)
control = ApacheControl (xml)
# lists

vhost_list_data = [ [ _("General Options") ],
                    [ _("Site Configuration") ],
                    [ _("SSL") ],
                    [ _("Logging") ],
                    [ _("Environment Variables") ],
                    [ _("Directories")] ]

default_vhost_list_data = [ [ _("Site Configuration") ],
                            [ _("Logging") ],
                            [ _("Environment Variables") ],
                            [ _("Directories")] ]


# Dir where documentation resided.
doc_dir = '/usr/share/doc/system-config-httpd/html/'


##
# Helper classes
##

class DirOptionsList (CheckList):
    def __init__ (self):
        CheckList.__init__ (self)
        self.column_titles_show ()
        self.set_column_title (1, _("Options"))
        self.column_titles_passive ()
        for i in ApacheGizmo.VirtualHost.DIRECTORY_OPTIONS:
            self.append_row (i, False)
        self.set_selection_mode (gtk.SELECTION_BROWSE)

    def set_to_list (self):
        retval = []
        for i in xrange (len (ApacheGizmo.VirtualHost.DIRECTORY_OPTIONS)):
            if self.row_get_state (i):
                retval.append (ApacheGizmo.VirtualHost.DIRECTORY_OPTIONS[i])
        return retval

    def set_from_list (self, list):
        for i in xrange (self.rows):
            if self.get_text (i, 1) in list:
                self.row_set_state (i, True)
            else:
                self.row_set_state (i, False)

    def set_to_default (self):
        self.set_from_list ([ 'ExecCGI', 'FollowSymLinks', 'Includes', 'IncludesNOEXEC', 'Indexes', 'SymLinksIfOwnerMatch' ])
            
class ErrorDocumentClist (gtk.CList):
    def __init__ (self):
        gtk.CList.__init__ (self, 3, [_("Error Code"), _("Behavior"), _("Location")])
        self.set_column_auto_resize (0, True)
        self.set_column_auto_resize (1, True)
        self.set_column_auto_resize (2, True)
        self.set_selection_mode (gtk.SELECTION_BROWSE)
        self.column_titles_passive ()

        keys = ApacheGizmo.ErrorDocuments.ERROR_CODE_DATA.keys ()
        keys.sort ()
        for i in keys:
            (short, long) = ApacheGizmo.ErrorDocuments.ERROR_CODE_DATA[i]
            text = [  short, _("Default"), "" ]
            row = self.append (text)
            self.set_row_data (row, i)


    def set_to_default (self):
        for i in xrange (self.rows):
            self.set_text (i, 1, _("default"))
            self.set_text (i, 2, "")

## UI Callbacks

def on_generic_clist_select_row (clist, row, column, event, button1, button2):
    button1.set_sensitive (True)
    button2.set_sensitive (True)

def on_generic_clist_unselect_row (clist, row, column, event, button1, button2):
    button1.set_sensitive (False)
    button2.set_sensitive (False)

def on_generic_clist_button_release_event (clist, event, func):
    id = clist.get_data ("signal_id")
    clist.disconnect (id)
    clist.remove_data ("signal_id")
    apply (func)

def on_generic_clist_button_press_event (clist, event, func):
    if event.type == gtk.gdk._2BUTTON_PRESS:
        info = clist.get_selection_info (event.x, event.y)
        if info != None:
            id = clist.connect ("button_release_event", on_generic_clist_button_release_event, func)
            clist.set_data ("signal_id", id)

def on_generic_gtk_widget_hide(button, widget):
    widget.hide();

def on_generic_toggle_set_sensitive(button, widget, reverse=False):
    if not reverse:
        widget.set_sensitive (button.get_active ())
    else:
        widget.set_sensitive (not button.get_active ())

def multiviews_cbutton_toggled(button, clist):
    if button.get_active ():
        clist.set_sensitive (False)
    else:
        clist.set_sensitive (True)

def gui_error_dialog (message, parent_dialog,
                      message_type=gtk.MESSAGE_ERROR,
                      widget=None, page=0, broken_widget=None):
    
    dialog = gtk.MessageDialog(parent_dialog,
                               gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                               message_type, gtk.BUTTONS_OK,
                               message)
    
    if widget != None:
        if isinstance (widget, gtk.CList):
            widget.select_row (page, 0)
        elif isinstance (widget, gtk.Notebook):
            widget.set_current_page (page)
    if broken_widget != None:
        broken_widget.grab_focus ()
        if isinstance (broken_widget, gtk.Entry):
            broken_widget.select_region (0, -1)

    dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
    ret = dialog.run ()
    dialog.destroy()
    return ret

def gui_yesnocancel_dialog (message, parent_dialog,
                            message_type=gtk.MESSAGE_QUESTION,
                            widget=None, page=0, broken_widget=None):
    dialog = gtk.MessageDialog(parent_dialog,
                               gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                               message_type,
                               gtk.BUTTONS_YES_NO,
                               message)
    dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)

    dialog.set_default_response(gtk.RESPONSE_REJECT)

    if widget != None:
        if isinstance (widget, gtk.CList):
            widget.select_row (page, 0)
        elif isinstance (widget, gtk.Notebook):
            widget.set_current_page (page)
    if broken_widget != None:
        broken_widget.grab_focus ()
        if isinstance (broken_widget, gtk.Entry):
            broken_widget.select_region (0, -1)
    dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
    ret = dialog.run ()
    dialog.destroy()
    return ret

def gui_yesno_dialog (message, parent_dialog,
                      message_type=gtk.MESSAGE_QUESTION,
                      widget=None, page=0, broken_widget=None):

    dialog = gtk.MessageDialog(parent_dialog,
                               gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                               message_type,
                               gtk.BUTTONS_YES_NO,
                               message)
    if widget != None:
        if isinstance (widget, gtk.CList):
            widget.select_row (page, 0)
        elif isinstance (widget, gtk.Notebook):
            widget.set_current_page (page)
    if broken_widget != None:
        broken_widget.grab_focus ()
        if isinstance (broken_widget, gtk.Entry):
            broken_widget.select_region (0, -1)
    dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
    ret = dialog.run ()
    dialog.destroy()
    return ret

def generic_error_dialog (message, parent_dialog, message_type=gtk.MESSAGE_WARNING, widget=None, page=0, broken_widget=None):
    gui_error_dialog (message, parent_dialog, message_type, widget, page, broken_widget)


##
## Main Dialog
##

def on_main_ok_button_clicked (button):
    main = xml.get_widget ("main")
    if gui_yesno_dialog(_("Are you sure you want to save and exit?"), main) != gtk.RESPONSE_YES:
        return
    try:
        control.dehydrate_main ()
    except TestError, (message, page, broken_widget):
        generic_error_dialog (message, main, gtk.MESSAGE_WARNING, xml.get_widget ("main_notebook"), page, broken_widget)
        return

    ret = control.write()
    if   ret == -1:
        if gui_yesno_dialog(_("The current configuration file has never been edited with system-config-httpd. Overwrite?"), main) == gtk.RESPONSE_YES:
            control.write(True)
        else:
            return
    elif ret == -2:
        if gui_yesno_dialog(_("The configuration file has been manually modified. Overwrite?"), main) == gtk.RESPONSE_YES:
            control.write(True)
        else:
            return
    gtk.main_quit ()

def on_main_help_button_clicked (button):
    notebook = xml.get_widget ('main_notebook')
    help_pages = [doc_dir+'httpd-basic-settings.html',
                  doc_dir+'httpd-virtualhosts-settings.html',
                  doc_dir+'httpd-server-settings.html',
                  doc_dir+'httpd-tuning-settings.html']
    gnome.url_show("file:"+help_pages [notebook.get_current_page ()])

def on_main_cancel_button_clicked (button):
    if gui_yesno_dialog(_("Are you sure you want to quit?"), xml.get_widget ("main")) == gtk.RESPONSE_YES:
        gtk.main_quit ()
        return False
    return True

def on_main_delete_clicked (window, event):
    return on_main_cancel_button_clicked (None)

def on_address_label_ip_address_toggled (button):
    xml.get_widget ("new_address_ip_entry").set_sensitive (button.get_active ())

def check_new_address_dialog (new_address):
    button = xml.get_widget ("address_label_ip_address")
    clist = xml.get_widget ("address_clist")
    port_text = xml.get_widget ("new_address_port_entry").get_text ()
    address_text = xml.get_widget ("new_address_ip_entry").get_text ()

    if port_text == "":
        generic_error_dialog (_("You must include a port to listen on.  Typically, port 80 is used."), xml.get_widget ("new_address_dialog"), gtk.MESSAGE_INFO)
        return False

    if button.get_active ():
        if address_text == "":
            generic_error_dialog (_("You must include an address to listen on."), xml.get_widget ("new_address_dialog"), gtk.MESSAGE_INFO)
            return False
    else:
        address_text = "0.0.0.0"

    if not check_ip(address_text):
        generic_error_dialog (_("Inserted IP address is not valid."), xml.get_widget ("new_address_dialog"), gtk.MESSAGE_INFO)
        return False

    if not check_port(port_text):
        generic_error_dialog (_("Inserted port is not valid."), xml.get_widget ("new_address_dialog"), gtk.MESSAGE_INFO)
        return False

    for i in xrange (clist.rows):
        if i == new_address:
            continue
        (old_address_text, old_port) = clist.get_row_data (i)
        if old_address_text == address_text and old_port == port_text:
            generic_error_dialog (_("You already have an address with that name."), xml.get_widget ("main"), gtk.MESSAGE_INFO)
            return False

    return True

def on_add_edit_address_button_clicked (button, add):
    clist = xml.get_widget ("address_clist")
    dialog = xml.get_widget ("new_address_dialog")
    port_entry = xml.get_widget ("new_address_port_entry")
    address_entry = xml.get_widget ("new_address_ip_entry")
    obutton = xml.get_widget ("address_label_ip_address")
    xml.get_widget ("new_address_dialog_ok_button").grab_default ()
    obutton.set_active (True)
    if add:
        dialog.set_title (_("Add new address..."))
        port_entry.set_text ("80")
        address_entry.set_text ("")
        row = -1
    else:
        if not clist.selection:
            return
        dialog.set_title (_("Edit an address..."))
        (old_address_text, old_port) = clist.get_row_data (clist.selection[0])
        if old_address_text == "*":
            xml.get_widget ("address_dialog_listen_all").set_active (True); 
            address_entry.set_text ("")
        else:
            obutton.set_active (True)
            address_entry.set_text (old_address_text)
        port_entry.set_text (old_port)
        row = clist.selection [0]
        # OK sensitivity
        ok = xml.get_widget("new_address_dialog_ok_button")
        ok.set_sensitive(False)
        for widget in ["new_address_ip_entry", "new_address_port_entry"]:
            xml.get_widget(widget).connect("changed", lambda *x: ok.set_sensitive(True))
        for widget in ["address_dialog_listen_all", "address_label_ip_address"]:
            xml.get_widget(widget).connect("toggled", lambda *x: ok.set_sensitive(True))


    dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
    dialog.set_transient_for (xml.get_widget("main"))
    while 1:
        button = dialog.run ()
        if button != gtk.RESPONSE_OK:
            dialog.hide ()
            return

        if check_new_address_dialog (row):
            break
    changed ()
    dialog.hide ()
    port_text = port_entry.get_text ()

    if obutton.get_active ():
        ip_text = address_entry.get_text ()
        text = ip_text + ":" + port_text
        if add:
            row = clist.append ( [ text ] )
        else:
            clist.set_text (row, 0, text)
        clist.set_row_data (row, (ip_text, port_text))
    else:
        text = _("All available addresses on port ") + port_text
        if add:
            row = clist.append ( [ text ] )
        else:
            clist.set_text (row, 0, text)
        clist.set_row_data (row, ("*", port_text))
    clist.select_row (row, 0)

def on_edit_address_button_clicked (*args):
    on_add_edit_address_button_clicked (None, False)

def on_delete_address_button_clicked (button):
    clist = xml.get_widget ("address_clist")
    if not clist.selection:
        return
    changed()
    selected = clist.selection [0]
    # FIXME:  Check virtual hosts before deleting addresses
    clist.remove (selected)
    clist.select_row (selected, 0)

def on_host_entry_changed (entry):
    clist = xml.get_widget ("address_clist")
    host_entry = xml.get_widget ("host_entry")
    port_entry = xml.get_widget ("port_entry")
    port_text = port_entry.get_text ()
    if (port_text == ""):
        string = host_entry.get_text ()
    else:
        string = host_entry.get_text () + ":" + port_text
    clist.set_text (clist.selection [0], 0, string)

def on_port_entry_insert_text (entry, text, length, unused):
    sub_string = text[0:length]
    reg = re.compile ("[^0-9]+")
    if reg.match (string):
        entry.emit_stop_by_name ("insert_text")
        return

def run_vhost_dialog (dialog):
    def set_ok_sensitivity():
        ok = xml.get_widget("vhost_ok_button")
        ok.set_sensitive(False)
        for widget in ["vhost_name_entry", "vhost_document_root_entry",
                "vhost_server_admin_entry", "ip_vhost_ip_entry",
                "ip_vhost_host_name_entry", "ssl_certificate_file_entry",
                "ssl_certificate_key_entry", "ssl_certificate_chain_entry",
                "ssl_certificate_authority_entry", "vhost_type_omenu",
                "error_log_level_omenu", "reverse_lookup_omenu",
                "transfer_log_to_file_real_entry", "ServerSignatureOption",
                "transfer_log_to_program_entry", "transfer_use_system_log_entry",
                "custom_log_string_entry", "error_log_to_file_real_entry", 
                "error_log_to_program_entry", "error_use_system_log_entry",
                "name_vhost_ip_entry", "name_vhost_host_name_entry",
                "default_vhost_all_port_entry", "ssl_certificate_file_entry"]:
            xml.get_widget(widget).connect("changed", lambda *x: ok.set_sensitive(True))
        for widget in ["ssl_engine_cbox", "custom_log_cbutton",
               "default_vhost_all_port_rbutton", "default_vhost_all_hosts_rbutton",
               "transfer_log_to_file_rbutton",
               "transfer_log_to_prog_rbutton", "transfer_sys_log_rbutton", 
               "custom_log_cbutton", "error_log_to_file_rbutton", 
               "error_log_to_prog_rbutton", "error_sys_log_rbutton"]:
            xml.get_widget(widget).connect("toggled", lambda *x: ok.set_sensitive(True))
     
    mode = dialog.get_data ("mode")
    row = dialog.get_data ("row")
    clist = xml.get_widget ("vhost_clist")
    vhost_clist = xml.get_widget ("virtual_host_dialog_clist")
    xml.get_widget ("vhost_ok_button").grab_default ()

    vhost_clist.clear ()

    if mode == "default":
        control.hydrate_default_vhost ()
        for i in default_vhost_list_data:
            vhost_clist.append (i)
        xml.get_widget ("vhost_notebook").get_nth_page(0).hide()
        xml.get_widget ("vhost_notebook").get_nth_page(2).hide()
        set_ok_sensitivity()
    else:
        if mode == "edit":
            if not clist.selection:
                return
            control.hydrate_vhost (clist.get_text (clist.selection [0], 0))
            set_ok_sensitivity()
        elif mode == "add":
            control.hydrate_vhost ()
            # Ugly fix for default DirectoryIndex
            tmp_clist = xml.get_widget ("directory_index_clist")
            # Only add default values if they are not there yet.
            if tmp_clist.rows == 0:
                tmp_clist.insert ( 0, [ "index.shtml" ] )
                tmp_clist.insert ( 0, [ "index.htm" ] )
                tmp_clist.insert ( 0, [ "index.html" ] )
                tmp_clist.select_row (0, 0)
        for i in vhost_list_data:
            vhost_clist.append (i)
        xml.get_widget ("vhost_notebook").get_nth_page(0).show()
        xml.get_widget ("vhost_notebook").get_nth_page(2).show()

    vhost_clist.select_row (0, 0)

    dialog.set_transient_for (xml.get_widget("main"))
    while (1):
        button = dialog.run ()
        if button == gtk.RESPONSE_OK:
            try:
                if mode == "edit":
                    new_name, new_address = control.dehydrate_vhost()
                    clist.set_text (clist.selection [0], 0, new_name)
                    clist.set_text (clist.selection [0], 1, new_address)
                elif mode == "add":
                    new_name, new_address = control.dehydrate_vhost()
                    new_row = clist.insert (row, [new_name, new_address])
                    clist.select_row (new_row, 0)
                else:
                    control.dehydrate_default_vhost()
                break
            except TestError, (message, row, broken_widget):
                generic_error_dialog (message.message, dialog, gtk.MESSAGE_ERROR, xml.get_widget ("virtual_host_dialog_clist"), row, broken_widget)
                continue
        elif button == gtk.RESPONSE_HELP:
            continue
        else:
            control.discard_vhost ()
            break
    if button == gtk.RESPONSE_OK:
        changed ()
    dialog.hide ()

def on_add_vhost_button_clicked (button):
    clist = xml.get_widget ("vhost_clist")
    dialog = xml.get_widget ("virtual_host_dialog")
    if clist.selection:
        dialog.set_data ("row", clist.selection [0] + 1)
    else:
        dialog.set_data ("row", 0)
    dialog.set_data ("mode", "add")
    run_vhost_dialog (dialog)

def on_edit_vhost_button_clicked (*args):
    dialog = xml.get_widget ("virtual_host_dialog")
    clist = xml.get_widget ("vhost_clist")
    if not clist.selection:
        return
    dialog.set_data ("row", clist.selection [0] + 1)
    dialog.set_data ("mode", "edit")
    run_vhost_dialog (dialog)

def on_delete_vhost_button_clicked (button):
    clist = xml.get_widget ("vhost_clist")
    if not clist.selection:
        return
    changed()
    selected = clist.selection [0]
    name = clist.get_text (selected, 0)
    clist.remove (selected)
    clist.select_row (selected, 0)
    control.remove_vhost (name)

## Virtual Host Dialog

def on_virtual_host_dialog_clist_select_row (clist, row, column, event):
    dialog = xml.get_widget ("virtual_host_dialog")
    mode = dialog.get_data ("mode")
    notebook = xml.get_widget ("vhost_notebook")
    if mode == "default":
        if row == 0:
            notebook.set_current_page (1)
        else:
            notebook.set_current_page (row + 2)
    else:
        notebook.set_current_page (row)

def on_virtual_host_dialog_ok_button_clicked (button):
    window = xml.get_widget ("quit_dialog")
    window.show_all ()

def on_virtual_host_dialog_cancel_button_clicked (button):
    window = xml.get_widget ("quit_dialog")
    window.show_all ()

def on_vhost_help_button_clicked (button):
    notebook = xml.get_widget ('vhost_notebook')
    help_pages = [doc_dir+'httpd-virtualhosts-settings.html#S3-HTTPD-VIRTUALHOSTS-ADD-GENERAL',
                  doc_dir+'httpd-default-settings.html#HTTPD-SITE-CONFIG',
                  doc_dir+'httpd-virtualhosts-settings.html#S3-HTTPD-VIRTUALHOSTS-ADD-SSL',
                  doc_dir+'httpd-logging.html',
                  doc_dir+'httpd-environment-variables.html',
                  doc_dir+'httpd-directories.html']
    gnome.url_show ("file:"+help_pages [notebook.get_current_page ()])

def on_default_vhost_button_clicked (button):
    dialog = xml.get_widget ("virtual_host_dialog")
    dialog.set_data ("mode", "default")
    run_vhost_dialog (dialog)

def on_unlimited_cnxns_rbutton_toggled (button):
    xml.get_widget ("max_requests_per_child_spin").set_sensitive (not button.get_active ())

def on_keep_alive_cbutton_toggled (button):
    xml.get_widget ("timeout_hbox").set_sensitive (button.get_active ())

def on_vhost_type_omenu_selected (omenu, *args):
    i = omenu.get_children ().index ( omenu.get_active ())
    xml.get_widget ("host_info_notebook").set_current_page (i)
    if i == 1:
        xml.get_widget ("ssl_engine_cbox").set_active (False)

def on_vhost_alias_add_edit_button_clicked (button, add):
    dialog = xml.get_widget ("vhost_alias_dialog")
    label = xml.get_widget ("vhost_alias_dialog_label")
    clist = xml.get_widget ("vhost_alias_clist")
    host_name = xml.get_widget ("name_vhost_host_name_entry").get_text ()
    alias_entry = xml.get_widget ("vhost_alias_entry")

    alias_entry.grab_focus ()
    xml.get_widget ("vhost_alias_dialog_ok_button").grab_default ()
    dialog.set_parent (xml.get_widget ("virtual_host_dialog"))

    if add:
        row = 0
        dialog.set_title (_("Add a new alias..."))
        alias_entry.set_text ("")
        if host_name != "":
            label.set_text (_("Add a new alias for the hostname:\n\"%s\"") % host_name)
        else:
            label.set_text (_("Add a new alias:"))
    else:
        if not clist.selection:
            return
        row = clist.selection [0]
        alias_entry.set_text (clist.get_text (row, 0))

        if host_name != "":
            label.set_text (_("Edit an existing alias for the hostname:\n\"%s\"") % host_name)
            dialog.set_title (_("Edit an alias for %s...") % host_name)
        else:
            label.set_text (_("Edit an existing alias:"))
            dialog.set_title (_("Edit an alias..."))

    while 1:
        button = dialog.run ()
        if button != gtk.RESPONSE_OK:
            dialog.hide ()
            return

        text = alias_entry.get_text ()
        if text == "":
            generic_error_dialog (_("Unable to add an empty alias."), dialog, gtk.MESSAGE_WARNING, broken_widget=alias_entry)
            continue
        duplicate = False
        for i in xrange (clist.rows):
            if not add and i == row:
                continue
            if text == clist.get_text (i, 0):
                generic_error_dialog (_("An alias with the name\n\"%s\"\nalready exists.") % text, dialog, gtk.MESSAGE_WARNING, broken_widget=alias_entry)
                duplicate = True
                break
        if duplicate:
            continue
        break
    xml.get_widget("vhost_ok_button").set_sensitive(True)
    dialog.hide ()

    if add:
        row = clist.append ( [ text ] )
    else:
        clist.set_text (row, 0, text)
    clist.select_row (row, 0)

def on_vhost_alias_edit_button_clicked (*args):
    on_vhost_alias_add_edit_button_clicked (None, False)

def on_vhost_alias_delete_button_clicked (button):
    clist = xml.get_widget ("vhost_alias_clist")
    if not clist.selection:
        return
    xml.get_widget("vhost_ok_button").set_sensitive(True)
    selected = clist.selection [0]
    clist.remove (selected)
    clist.select_row (selected, 0)

def on_default_vhost_all_port_rbutton_toggled (check):
    xml.get_widget ('default_vhost_all_port_entry').set_sensitive (check.get_active ())

def on_custom_logging_toggled (check):
    label = xml.get_widget ("custom_log_string_label")
    entry = xml.get_widget ("custom_log_string_entry")
    label.set_sensitive (check.get_active ())
    entry.set_sensitive (check.get_active ())

def on_transfer_log_to_file_toggled (radio):
    entry = xml.get_widget ("transfer_log_to_file_real_entry")
    entry.set_sensitive (radio.get_active ())
    entry.grab_focus ()

def on_transfer_log_to_program_toggled (radio):
    entry = xml.get_widget ("transfer_log_to_program_entry")
    entry.set_sensitive (radio.get_active ())
    entry.grab_focus ()

def on_transfer_use_system_log_toggled (radio):
    entry = xml.get_widget ("transfer_use_system_log_entry")
    entry.set_sensitive (radio.get_active ())
    entry.grab_focus ()

def on_error_log_to_file_toggled (radio):
    entry = xml.get_widget ("error_log_to_file_real_entry")
    entry.set_sensitive (radio.get_active ())
    entry.grab_focus ()

def on_error_log_to_program_toggled (radio):
    entry = xml.get_widget ("error_log_to_program_entry")
    entry.set_sensitive (radio.get_active ())
    entry.grab_focus ()

def on_error_use_system_log_toggled (radio):
    entry = xml.get_widget ("error_use_system_log_entry")
    entry.set_sensitive (radio.get_active ())
    entry.grab_focus ()

def on_edit_error_documents_clicked (*args):
    sw = xml.get_widget ("error_doc_list_swindow")
    clist = sw.get_data ("clist")
    if not clist.selection:
        return
    data = clist.get_row_data (clist.selection [0])
    if data == None:
        return

    #set up the dialog
    label = xml.get_widget ("error_document_dialog_error_code_label")
    label.set_text (_("%d - %s") % (data, ApacheGizmo.ErrorDocuments.ERROR_CODE_DATA[data][0]))

    label = xml.get_widget ("error_document_dialog_description_label")
    label.set_text (ApacheGizmo.ErrorDocuments.ERROR_CODE_DATA[data][1])

    behavior = clist.get_text (clist.selection [0], 1)
    index = 0
    if behavior == _("File"):
        index = 1
    elif behavior == "URL":
        index = 2
    omenu = xml.get_widget ("error_document_dialog_behavior_omenu")
    omenu.set_history (index)
    on_error_document_dialog_omenu_activate (None, index)

    location = clist.get_text (clist.selection [0], 2)
    entry = xml.get_widget ("error_document_dialog_location_entry")
    entry.set_text (location)

    dialog = xml.get_widget ("error_document_dialog")
    # OK sensitivity
    ok = xml.get_widget("error_document_dialog_ok_button")
    ok.set_sensitive(False)
    for widget in ["error_document_dialog_behavior_omenu", "error_document_dialog_location_entry"]:
        xml.get_widget(widget).connect("changed", lambda *x: ok.set_sensitive(True))
    button = dialog.run ()
    on_error_document_dialog_clicked_event(dialog, button)

def on_error_document_dialog_clicked_event (dialog, button):
    if button == gtk.RESPONSE_OK:
        clist = xml.get_widget ("error_doc_list_swindow").get_data ("clist")
        omenu = xml.get_widget ("error_document_dialog_behavior_omenu")
        entry = xml.get_widget ("error_document_dialog_location_entry")
        behavior = omenu.get_menu ().get_active ()
        index = 0
        for menu_item in omenu.get_menu ().get_children ():
            if menu_item == behavior:
                break
            index = index + 1

        if index == 0:
            clist.set_text (clist.selection [0], 1, _("default"))
            clist.set_text (clist.selection [0], 2, "")
        elif index == 1:
            clist.set_text (clist.selection [0], 1, _("File"))
            clist.set_text (clist.selection [0], 2, entry.get_text ())
        elif index == 2:
            clist.set_text (clist.selection [0], 1, "URL")
            clist.set_text (clist.selection [0], 2, entry.get_text ())
        xml.get_widget("vhost_ok_button").set_sensitive(True)
    dialog.hide()

def on_error_document_dialog_omenu_activate (menu_item, offset):
    entry = xml.get_widget ("error_document_dialog_location_entry")
    if offset == 0:
        entry.set_sensitive (False)
    else:
        entry.set_sensitive (True)

def on_error_document_clist_select_row (clist, row, column, event):
    data = clist.get_row_data (row)
    if data == None:
        return
    label = xml.get_widget ("error_document_label")
    label.set_text (_("Error Code %d - %s") % (data, ApacheGizmo.ErrorDocuments.ERROR_CODE_DATA[data][0]))

def on_directory_index_add_clicked (button):
    clist = xml.get_widget ("directory_index_clist")
    dialog = xml.get_widget ("directory_index_dialog")
    entry = xml.get_widget ("directory_index_dialog_entry")
    entry.set_text ("")
    if clist.selection:
        dialog.set_data ("row", clist.selection [0] + 1)
    else:
        dialog.set_data ("row", 0)
    dialog.set_data ("mode", "add")
    button = dialog.run ()
    on_directory_index_dialog_clicked(dialog, button)

def on_directory_index_edit_clicked (*args):
    clist = xml.get_widget ("directory_index_clist")
    if not clist.selection:
        return
    dialog = xml.get_widget ("directory_index_dialog")
    entry = xml.get_widget ("directory_index_dialog_entry")

    text = clist.get_text (clist.selection [0], 0)
    dialog.set_data ("row", clist.selection [0])
    dialog.set_data ("mode", "edit")
    entry.set_text (text)
    # OK sensitivity
    ok = xml.get_widget("directory_index_dialog_ok_button")
    ok.set_sensitive(False)
    xml.get_widget("directory_index_dialog_entry").connect("changed", lambda *x: ok.set_sensitive(True))

    button = dialog.run ()
    on_directory_index_dialog_clicked(dialog, button)

def on_directory_index_delete_clicked (button):
    clist = xml.get_widget ("directory_index_clist")
    if not clist.selection:
        return
    xml.get_widget("vhost_ok_button").set_sensitive(True)
    selected = clist.selection [0]
    clist.remove (selected)
    clist.select_row (selected, 0)

def on_directory_index_dialog_clicked (dialog, button):
    if button == gtk.RESPONSE_OK:
        clist = xml.get_widget ("directory_index_clist")
        entry = xml.get_widget ("directory_index_dialog_entry")
        mode = dialog.get_data ("mode")
        row = dialog.get_data ("row")
        if mode == "add":
            new_row = clist.insert ( row, [ entry.get_text ()] )
            clist.select_row (new_row, 0)
        else:
            clist.set_text (row, 0, entry.get_text ())
        xml.get_widget("vhost_ok_button").set_sensitive(True)
    dialog.hide ()

def on_ssl_engine_cbox_toggled (toggle):
    omenu = xml.get_widget('vhost_type_omenu').get_menu ()
    if toggle.get_active () and omenu.get_children ().index (omenu.get_active ()) == 1:
        generic_error_dialog (_("SSL cannot be used with name based virtual hosts.\nPlease change to an IP based virtual host."),
                              xml.get_widget ("virtual_host_dialog"),
                              gtk.MESSAGE_WARNING,
                              xml.get_widget ("virtual_host_dialog_clist"), 0,
                              xml.get_widget ("vhost_type_omenu"))
        toggle.set_active (False)
    else:
        xml.get_widget ("ssl_frame").set_sensitive (toggle.get_active ())

def on_pass_env_add_button_clicked (button):
    clist = xml.get_widget ("pass_env_clist")
    entry = xml.get_widget ("env_dialog_variable_entry")
    entry.set_text ("")
    entry = xml.get_widget ("env_dialog_value_entry")
    entry.hide ()
    label = xml.get_widget ("env_dialog_label")
    label.hide ()
    dialog = xml.get_widget ("env_dialog")
    dialog.set_data ("mode", "add")
    dialog.set_data ("clist", "pass_env_clist")
    if clist.selection:
        dialog.set_data ("row", clist.selection [0] + 1)
    else:
        dialog.set_data ("row", 0)
    button = dialog.run ()
    on_env_dialog_clicked(dialog, button)
    dialog.hide ()

def on_pass_env_edit_button_clicked (*args):
    clist = xml.get_widget ("pass_env_clist")
    if not clist.selection:
        return
    entry = xml.get_widget ("env_dialog_variable_entry")
    entry.set_text (clist.get_text (clist.selection [0], 0))
    entry = xml.get_widget ("env_dialog_value_entry")
    entry.hide ()
    label = xml.get_widget ("env_dialog_label")
    label.hide ()
    dialog = xml.get_widget ("env_dialog")
    dialog.set_data ("mode", "edit")
    dialog.set_data ("clist", "pass_env_clist")
    dialog.set_data ("row", clist.selection [0])
    # OK sensitivity
    ok = xml.get_widget("env_dialog_ok_button")
    ok.set_sensitive(False)
    xml.get_widget("env_dialog_variable_entry").connect("changed", lambda *x: ok.set_sensitive(True))
    button = dialog.run ()
    on_env_dialog_clicked(dialog, button)
    dialog.hide ()

def on_pass_env_delete_button_clicked (button):
    clist = xml.get_widget ("pass_env_clist")
    if not clist.selection:
        return
    xml.get_widget("vhost_ok_button").set_sensitive(True)
    selected = clist.selection [0]
    clist.remove (selected)
    clist.select_row (selected, 0)

def on_set_env_add_button_clicked (button):
    clist = xml.get_widget ("set_env_clist")
    entry = xml.get_widget ("env_dialog_variable_entry")
    entry.set_text ("")
    entry = xml.get_widget ("env_dialog_value_entry")
    entry.set_text ("")
    entry.show ()
    label = xml.get_widget ("env_dialog_label")
    label.show ()
    dialog = xml.get_widget ("env_dialog")
    dialog.set_data ("mode", "add")
    dialog.set_data ("clist", "set_env_clist")
    if clist.selection:
        dialog.set_data ("row", clist.selection [0] + 1)
    else:
        dialog.set_data ("row", 0)
    while 1:
        button = dialog.run ()
        if on_env_dialog_clicked(dialog, button):
            break
    dialog.hide ()

def on_set_env_edit_button_clicked (*args):
    clist = xml.get_widget ("set_env_clist")
    if not clist.selection:
        return
    entry = xml.get_widget ("env_dialog_variable_entry")
    entry.set_text (clist.get_text (clist.selection [0], 0))
    entry = xml.get_widget ("env_dialog_value_entry")
    entry.set_text (clist.get_text (clist.selection [0], 1))
    entry.show ()
    label = xml.get_widget ("env_dialog_label")
    label.show ()
    dialog = xml.get_widget ("env_dialog")
    dialog.set_data ("mode", "edit")
    dialog.set_data ("clist", "set_env_clist")
    dialog.set_data ("row", clist.selection [0])
    # OK sensitivity
    ok = xml.get_widget("env_dialog_ok_button")
    ok.set_sensitive(False)
    for widget in ["env_dialog_variable_entry", "env_dialog_value_entry"]:
        xml.get_widget(widget).connect("changed", lambda *x: ok.set_sensitive(True))
    while 1:
        button = dialog.run ()
        if on_env_dialog_clicked(dialog, button):
            break
    dialog.hide ()

def on_set_env_delete_button_clicked (button):
    clist = xml.get_widget ("set_env_clist")
    if not clist.selection:
        return
    xml.get_widget("vhost_ok_button").set_sensitive(True)
    selected = clist.selection [0]
    clist.remove (selected)
    clist.select_row (selected, 0)

def on_unset_env_add_button_clicked (button):
    clist = xml.get_widget ("unset_env_clist")
    entry = xml.get_widget ("env_dialog_variable_entry")
    entry.set_text ("")
    entry = xml.get_widget ("env_dialog_value_entry")
    entry.hide ()
    label = xml.get_widget ("env_dialog_label")
    label.hide ()
    dialog = xml.get_widget ("env_dialog")
    dialog.set_data ("mode", "add")
    dialog.set_data ("clist", "unset_env_clist")
    if clist.selection:
        dialog.set_data ("row", clist.selection [0] + 1)
    else:
        dialog.set_data ("row", 0)
    button = dialog.run ()
    on_env_dialog_clicked(dialog, button)

def on_unset_env_edit_button_clicked (*args):
    clist = xml.get_widget ("unset_env_clist")
    if not clist.selection:
        return
    entry = xml.get_widget ("env_dialog_variable_entry")
    entry.set_text (clist.get_text (clist.selection [0], 0))
    entry = xml.get_widget ("env_dialog_value_entry")
    entry.hide ()
    label = xml.get_widget ("env_dialog_label")
    label.hide ()
    dialog = xml.get_widget ("env_dialog")
    dialog.set_data ("mode", "edit")
    dialog.set_data ("clist", "unset_env_clist")
    dialog.set_data ("row", clist.selection [0])
    # OK sensitivity
    ok = xml.get_widget("env_dialog_ok_button")
    ok.set_sensitive(False)
    xml.get_widget("env_dialog_variable_entry").connect("changed", lambda *x: ok.set_sensitive(True))
    button = dialog.run ()
    on_env_dialog_clicked(dialog, button)

def on_unset_env_delete_button_clicked (button):
    clist = xml.get_widget ("unset_env_clist")
    if not clist.selection:
        return
    xml.get_widget("vhost_ok_button").set_sensitive(True)
    selected = clist.selection [0]
    clist.remove (selected)
    clist.select_row (selected, 0)

def on_env_dialog_clicked (dialog, button):
    if button == gtk.RESPONSE_OK:
        clist_text = dialog.get_data ("clist")
        mode = dialog.get_data ("mode")
        row = dialog.get_data ("row")

        clist = xml.get_widget (clist_text)
        entry = xml.get_widget ("env_dialog_variable_entry")
        entry2 = xml.get_widget ("env_dialog_value_entry")
        xml.get_widget("vhost_ok_button").set_sensitive(True)
	if entry2.get_property("visible") and entry2.get_text () == "":
                generic_error_dialog ("Environment variable value may not be empty", dialog, gtk.MESSAGE_ERROR, broken_widget=dialog)
                return False

        if mode == "add":
            if clist_text == "set_env_clist":
                new_row = clist.insert ( row, [ entry.get_text (), entry2.get_text ()] )
            else:
                new_row = clist.insert ( row, [ entry.get_text ()] )
            clist.select_row (new_row, 0)
        else:
            clist.set_text (row, 0, entry.get_text ())
            if clist_text == "set_env_clist":
                clist.set_text (row, 1, entry2.get_text ())

    dialog.hide ()
    return True

def on_default_dir_options_edit_button_clicked (button):
    dialog = xml.get_widget ("default_directory_options_dialog")
    control.hydrate_default_dir_options (dialog)
    # OK sensitivity
    ok = xml.get_widget("default_directory_options_dialog_ok_button")
    ok.set_sensitive(False)
    dialog.get_data ("clist").set_toggled_func(lambda *x: ok.set_sensitive(True))

    button = dialog.run ()
    dialog.hide ()
    if button != gtk.RESPONSE_OK:
        return
    xml.get_widget("vhost_ok_button").set_sensitive(True)
    control.dehydrate_default_dir_options (dialog)

def run_dir_options_dialog (dialog):
    mode = dialog.get_data ("mode")
    row = dialog.get_data ("row")
    clist = xml.get_widget ("dir_options_clist")

    xml.get_widget ("dir_options_dialog_ok_button").grab_default ()
    dir_name = None
    if mode == "edit":
        dir_name = clist.get_text (clist.selection[0], 0)

    control.hydrate_dir_options (dir_name)

    if mode == "edit":
        # OK sensitivity
        ok = xml.get_widget("dir_options_dialog_ok_button")
        ok.set_sensitive(False)
        for widget in ["dir_opt_dialog_let_all_rbutton", "dir_opt_dialog_deny_first_rbutton",
                       "dir_opt_dialog_allow_first_rbutton", "dir_opt_dialog_deny_all_rbutton",
                       "dir_opt_dialog_deny_from_rbutton", "dir_opt_dialog_allow_all_rbutton",
                       "dir_opt_dialog_allow_from_rbutton", "allow_override_cbox"]:
            xml.get_widget(widget).connect("toggled", lambda *x: ok.set_sensitive(True))
        for widget in ["deny_list_entry", "allow_list_entry", "directory_options_dialog_dir_entry"]:
            xml.get_widget(widget).connect("changed", lambda *x: ok.set_sensitive(True))
        xml.get_widget ("directory_options_dialog").get_data ("clist").set_toggled_func(lambda *x: ok.set_sensitive(True))

    while True:
        button = dialog.run ()
        if button == gtk.RESPONSE_HELP:
            continue
        if button == gtk.RESPONSE_OK:
            try:
                dir_name = control.dehydrate_dir_options (dir_name)
            except TestError, (message, row, broken_widget):
                generic_error_dialog (message, dialog, gtk.MESSAGE_ERROR, broken_widget=broken_widget)
                continue
            xml.get_widget("vhost_ok_button").set_sensitive(True)
            break
        else:
            control.discard_dir_options ()
            dialog.hide ()
            return
    dialog.hide ()
    if mode == "add":
        row = clist.insert (row, [ dir_name ])
    else:
        clist.set_text (row, 0, dir_name)

def on_dir_options_add_button_clicked (button):
    dialog = xml.get_widget ("directory_options_dialog")
    clist = xml.get_widget ("dir_options_clist")

    dialog.set_data ("mode", "add")
    if clist.selection:
        dialog.set_data ("row", clist.selection [0] + 1)
    else:
        dialog.set_data ("row", 0)
    run_dir_options_dialog (dialog)

def on_dir_options_edit_button_clicked (*args):
    dialog = xml.get_widget ("directory_options_dialog")
    clist = xml.get_widget ("dir_options_clist")
    if not clist.selection:
        return
    dialog.set_data ("mode", "edit")
    dialog.set_data ("row", clist.selection [0])
    run_dir_options_dialog (dialog)

def on_dir_options_delete_button_clicked (button):
    clist = xml.get_widget ("dir_options_clist")
    if not clist.selection:
        return
    xml.get_widget("vhost_ok_button").set_sensitive(True)
    selected = clist.selection [0]
    name = clist.get_text (selected, 0)
    clist.remove (selected)
    clist.select_row (selected, 0)
    control.remove_dir_option (name)

def on_dir_options_help_button_clicked (button):
    gnome.url_show ("file:"+doc_dir+'httpd-directories.html#HTTPD-DIRECTORIES-ADD')

def on_order_deny_group_toggled (button):
    if button.get_active ():
        xml.get_widget ("deny_list_frame").set_sensitive (False)
        xml.get_widget ("allow_list_frame").set_sensitive (False)
    else:
        xml.get_widget ("deny_list_frame").set_sensitive (True)
        xml.get_widget ("allow_list_frame").set_sensitive (True)


# SETUP CODE
def setup_main ():
    xml.get_widget ("edit_address_button").set_sensitive (False)
    xml.get_widget ("delete_address_button").set_sensitive (False)
    xml.get_widget ("edit_vhost_button").set_sensitive (False)
    xml.get_widget ("delete_vhost_button").set_sensitive (False)

#    xml.get_widget ("new_address_dialog").close_hides (True)
#    xml.get_widget ("virtual_host_dialog").close_hides (True)
#    xml.get_widget ("default_directory_options_dialog").close_hides (True)
#    xml.get_widget ("vhost_alias_dialog").close_hides (True)
#    xml.get_widget ("directory_options_dialog").close_hides (True)
#    xml.get_widget ("env_dialog").close_hides (True)
#    xml.get_widget ("directory_index_dialog").close_hides (True)
#    xml.get_widget ("error_document_dialog").close_hides (True)

    xml.get_widget ("question-pixmap1").set_from_file ("/usr/share/pixmaps/gnome-question.png")
    xml.get_widget ("question-pixmap2").set_from_file ("/usr/share/pixmaps/gnome-question.png")
    xml.get_widget ("question-pixmap3").set_from_file ("/usr/share/pixmaps/gnome-question.png")
    clist = xml.get_widget ("vhost_clist")
    clist.set_reorderable (True)
    clist.column_titles_passive ()
    clist.set_column_auto_resize (0, True)
    clist.set_column_auto_resize (1, True)

def setup_basic_vhost ():
    dialog = xml.get_widget ("virtual_host_dialog")
    xml.get_widget('vhost_type_omenu').get_menu ().connect('selection-done', on_vhost_type_omenu_selected)

def setup_default_directory_options_dialog ():
    dialog = xml.get_widget ("default_directory_options_dialog")
    vbox = xml.get_widget ("default_directory_options_dialog_vbox")
    clist = DirOptionsList ()
    clist.set_column_auto_resize (0, True)
    clist.set_column_auto_resize (1, True)
    vbox.pack_start (clist, True, True, 0)
    hbox = gtk.HBox (False, 4)
    vbox.pack_start (hbox, False, False, 0)
    vbox.show_all ()
    dialog.set_data ("clist", clist)


def setup_directory_options_dialog ():
    dialog = xml.get_widget ("directory_options_dialog")
    vbox = xml.get_widget ("directory_options_options_vbox")
    clist = DirOptionsList ()
    clist.set_column_auto_resize (0, True)
    clist.set_column_auto_resize (1, True)
    vbox.pack_start (clist, True, True, 0)
    vbox.show_all ()
    dialog.set_data ("clist", clist)
    on_generic_clist_unselect_row (clist, 0, 0, 0, xml.get_widget ("dir_options_edit_button"), xml.get_widget ("dir_options_delete_button"))
    xml.get_widget ("deny_list_frame").set_sensitive (False)
    xml.get_widget ("allow_list_frame").set_sensitive (False)

def setup_default_directory ():
    clist = xml.get_widget ("directory_index_clist")
    clist.set_reorderable (True)
    clist.column_titles_passive ()
    on_generic_clist_unselect_row (clist, 0, 0, 0, xml.get_widget ("directory_index_edit"), xml.get_widget ("directory_index_delete"))

def setup_error_document ():
    sw = xml.get_widget ("error_doc_list_swindow")
    clist = ErrorDocumentClist ()
    clist.column_titles_passive ()
    clist.show ()
    clist.connect ('select_row', on_error_document_clist_select_row)
    clist.connect ('button_press_event', on_generic_clist_button_press_event, on_edit_error_documents_clicked)
    on_error_document_clist_select_row (clist, 0, 0, None)
    sw.add (clist)
    sw.set_data ("clist", clist)

    omenu = xml.get_widget ("error_document_dialog_behavior_omenu")
    menu = omenu.get_menu ()
    i = 0
    for menu_item in menu.get_children():
        menu_item.connect ("activate", on_error_document_dialog_omenu_activate, i)
        i = i + 1

def setup_ssl_options ():
    vbox = xml.get_widget ("ssl_vbox")
    clist = CheckList ()
    clist.column_titles_show ()
    clist.set_column_title (1, _("SSL Options"))
    clist.column_titles_passive ()
    clist.show_all ()
    clist.set_toggled_func(lambda x, y: xml.get_widget("vhost_ok_button").set_sensitive(True))
    for i in ApacheGizmo.VirtualHost.SSL_OPTIONS:
        clist.append_row (i, False)
    vbox.pack_start (clist, True, True, 0)
    vbox.set_data ("ssl_clist", clist)

def setup_env ():
    clist = xml.get_widget ("pass_env_clist")
    on_generic_clist_unselect_row (clist, 0, 0, 0, xml.get_widget ("pass_env_edit_button"), xml.get_widget ("pass_env_delete_button"))
    clist = xml.get_widget ("set_env_clist")
    clist.set_column_auto_resize (0, True)
    clist.set_column_auto_resize (1, True)
    clist.column_titles_passive ()
    on_generic_clist_unselect_row (clist, 0, 0, 0, xml.get_widget ("set_env_edit_button"), xml.get_widget ("set_env_delete_button"))
    clist = xml.get_widget ("unset_env_clist")
    on_generic_clist_unselect_row (clist, 0, 0, 0, xml.get_widget ("unset_env_edit_button"), xml.get_widget ("unset_env_delete_button"))

def setup_directory_options ():
    clist = xml.get_widget ("dir_options_clist")
    clist.set_reorderable (True)
    clist.column_titles_passive ()

def changed (*args):
    ok = xml.get_widget ("main_ok_button")
    ok.set_sensitive(True)

def setup ():
    setup_main ()
    setup_basic_vhost ()
    setup_default_directory_options_dialog ()
    setup_directory_options_dialog ()
    setup_default_directory ()
    setup_error_document ()
    setup_ssl_options ()
    setup_env ()
    setup_directory_options ()
    control.hydrate_main ()
    ok = xml.get_widget ("main_ok_button")
    ok.set_sensitive(False)
    xml.get_widget("server_name_entry").connect("changed", changed)
    xml.get_widget("server_admin_entry").connect("changed", changed)
    xml.get_widget("max_clients_spin").connect("changed", changed)
    xml.get_widget("time_out_spin").connect("changed", changed)
    xml.get_widget("max_requests_per_child_spin").connect("changed", changed)
    xml.get_widget("keep_alive_spin").connect("changed", changed)
    xml.get_widget("unlimited_cnxns_rbutton").connect("toggled", changed)
    xml.get_widget("limited_cnxns_rbutton").connect("toggled", changed)
    xml.get_widget("keep_alive_cbutton").connect("toggled", changed)

def main ():
    xml.signal_autoconnect (
        { "on_address_clist_select_row" : (on_generic_clist_select_row, xml.get_widget ("delete_address_button"), xml.get_widget ("edit_address_button")),
          "on_address_clist_unselect_row" : (on_generic_clist_unselect_row, xml.get_widget ("delete_address_button"), xml.get_widget ("edit_address_button")),
          "on_address_clist_button_press_event" : (on_generic_clist_button_press_event, on_edit_address_button_clicked),
          "on_main_ok_button_clicked" : on_main_ok_button_clicked,
          "on_main_cancel_button_clicked" : on_main_cancel_button_clicked,
          "on_main_help_button_clicked" : on_main_help_button_clicked,
          "on_main_delete_event" : on_main_delete_clicked,
          "on_address_label_ip_address_toggled" : on_address_label_ip_address_toggled,
          "on_add_address_button_clicked" : (on_add_edit_address_button_clicked, True),
          "on_edit_address_button_clicked" : (on_add_edit_address_button_clicked, False),
          "on_host_entry_changed" : on_host_entry_changed,
          "on_port_entry_changed" : on_host_entry_changed,
          "on_port_entry_insert_text" : on_port_entry_insert_text,
          "on_delete_address_button_clicked" : on_delete_address_button_clicked,
          "on_add_vhost_button_clicked" : on_add_vhost_button_clicked,
          "on_edit_vhost_button_clicked" : on_edit_vhost_button_clicked,
          "on_delete_vhost_button_clicked" : on_delete_vhost_button_clicked,
          "on_virtual_host_dialog_clist_select_row" : on_virtual_host_dialog_clist_select_row,
          "on_default_vhost_button_clicked" : on_default_vhost_button_clicked,
          "on_unlimited_cnxns_rbutton_toggled" : on_unlimited_cnxns_rbutton_toggled,
          "on_keep_alive_cbutton_toggled" : on_keep_alive_cbutton_toggled,
          "on_vhost_clist_select_row" : (on_generic_clist_select_row, xml.get_widget ("edit_vhost_button"), xml.get_widget ("delete_vhost_button")),
          "on_vhost_clist_unselect_row" : (on_generic_clist_unselect_row, xml.get_widget ("edit_vhost_button"), xml.get_widget ("delete_vhost_button")),
          "on_vhost_clist_button_press_event" : (on_generic_clist_button_press_event, on_edit_vhost_button_clicked),
          "on_vhost_alias_add_button_clicked" : (on_vhost_alias_add_edit_button_clicked, True),
          "on_vhost_alias_edit_button_clicked" : (on_vhost_alias_add_edit_button_clicked, False),
          "on_vhost_alias_delete_button_clicked" : on_vhost_alias_delete_button_clicked,
          "on_vhost_alias_clist_select_row" : (on_generic_clist_select_row, xml.get_widget ("vhost_alias_edit_button"), xml.get_widget ("vhost_alias_delete_button")),
          "on_vhost_alias_clist_unselect_row" : (on_generic_clist_unselect_row, xml.get_widget ("vhost_alias_edit_button"), xml.get_widget ("vhost_alias_delete_button")),
          "on_vhost_alias_clist_button_press_event": (on_generic_clist_button_press_event, on_vhost_alias_edit_button_clicked),
          "on_default_vhost_all_port_rbutton_toggled" : on_default_vhost_all_port_rbutton_toggled,
          "on_custom_logging_toggled" : on_custom_logging_toggled,
          "on_transfer_log_to_file_toggled" : on_transfer_log_to_file_toggled,
          "on_transfer_log_to_program_toggled" : on_transfer_log_to_program_toggled,
          "on_transfer_use_system_log_toggled" : on_transfer_use_system_log_toggled,
          "on_error_log_to_file_toggled" : on_error_log_to_file_toggled,
          "on_error_log_to_program_toggled" : on_error_log_to_program_toggled,
          "on_error_use_system_log_toggled" : on_error_use_system_log_toggled,
          "on_virtual_host_dialog_ok_button_clicked" : on_virtual_host_dialog_ok_button_clicked,
          "on_virtual_host_dialog_cancel_button_clicked" : on_virtual_host_dialog_cancel_button_clicked,
          "on_vhost_help_button_clicked" : on_vhost_help_button_clicked,
          "on_edit_error_documents_clicked" : on_edit_error_documents_clicked,
          "on_error_document_dialog_clicked_event" : on_error_document_dialog_clicked_event,
          "on_directory_index_clist_select_row" : (on_generic_clist_select_row, xml.get_widget ("directory_index_edit"), xml.get_widget ("directory_index_delete")),
          "on_directory_index_clist_unselect_row" : (on_generic_clist_unselect_row, xml.get_widget ("directory_index_edit"), xml.get_widget ("directory_index_delete")),
          "on_directory_index_add_clicked" : on_directory_index_add_clicked,
          "on_directory_index_edit_clicked" : on_directory_index_edit_clicked,
          "on_directory_index_delete_clicked" : on_directory_index_delete_clicked,
          "on_directory_index_dialog_clicked" : on_directory_index_dialog_clicked,
          "on_directory_index_clist_button_press_event" : (on_generic_clist_button_press_event, on_directory_index_edit_clicked),
          "on_ssl_engine_cbox_toggled" : on_ssl_engine_cbox_toggled,
          "on_pass_env_add_button_clicked" : on_pass_env_add_button_clicked,
          "on_pass_env_edit_button_clicked" : on_pass_env_edit_button_clicked,
          "on_pass_env_delete_button_clicked" : on_pass_env_delete_button_clicked,
          "on_pass_env_clist_select_row" : (on_generic_clist_select_row, xml.get_widget ("pass_env_edit_button"), xml.get_widget ("pass_env_delete_button")),
          "on_pass_env_clist_unselect_row" : (on_generic_clist_unselect_row, xml.get_widget ("pass_env_edit_button"), xml.get_widget ("pass_env_delete_button")),
          "on_pass_env_clist_button_press_event" : (on_generic_clist_button_press_event, on_pass_env_edit_button_clicked),
          "on_set_env_add_button_clicked" : on_set_env_add_button_clicked,
          "on_set_env_edit_button_clicked" : on_set_env_edit_button_clicked,
          "on_set_env_delete_button_clicked" : on_set_env_delete_button_clicked,
          "on_set_env_clist_select_row" : (on_generic_clist_select_row, xml.get_widget ("set_env_edit_button"), xml.get_widget ("set_env_delete_button")),
          "on_set_env_clist_unselect_row" : (on_generic_clist_unselect_row, xml.get_widget ("set_env_edit_button"), xml.get_widget ("set_env_delete_button")),
          "on_set_env_clist_button_press_event" : (on_generic_clist_button_press_event, on_set_env_edit_button_clicked),
          "on_unset_env_add_button_clicked" : on_unset_env_add_button_clicked,
          "on_unset_env_edit_button_clicked" : on_unset_env_edit_button_clicked,
          "on_unset_env_delete_button_clicked" : on_unset_env_delete_button_clicked,
          "on_unset_env_clist_select_row" : (on_generic_clist_select_row, xml.get_widget ("unset_env_edit_button"), xml.get_widget ("unset_env_delete_button")),
          "on_unset_env_clist_unselect_row" : (on_generic_clist_unselect_row, xml.get_widget ("unset_env_edit_button"), xml.get_widget ("unset_env_delete_button")),
          "on_unset_env_clist_button_press_event" : (on_generic_clist_button_press_event, on_unset_env_edit_button_clicked),
          "on_env_dialog_clicked" : on_env_dialog_clicked,
          "on_dir_options_clist_select_row" : (on_generic_clist_select_row, xml.get_widget ("dir_options_edit_button"), xml.get_widget ("dir_options_delete_button")),
          "on_dir_options_clist_unselect_row" : (on_generic_clist_unselect_row, xml.get_widget ("dir_options_edit_button"), xml.get_widget ("dir_options_delete_button")),
          "on_dir_options_clist_button_press_event" : (on_generic_clist_button_press_event, on_dir_options_edit_button_clicked ),
          "on_dir_options_add_button_clicked" : on_dir_options_add_button_clicked,
          "on_dir_options_edit_button_clicked" : on_dir_options_edit_button_clicked,
          "on_dir_options_delete_button_clicked" : on_dir_options_delete_button_clicked,
          "on_dir_options_help_button_clicked" : on_dir_options_help_button_clicked,
          "on_default_dir_options_edit_button_clicked" : on_default_dir_options_edit_button_clicked,
          "on_order_deny_group_toggled" : on_order_deny_group_toggled,
          "on_dir_opt_dialog_deny_all_rbutton_toggled" : (on_generic_toggle_set_sensitive, xml.get_widget ("deny_list_entry"), True),
          "on_dir_opt_dialog_allow_all_rbutton_toggled" : (on_generic_toggle_set_sensitive, xml.get_widget ("allow_list_entry"), True),
          })

    setup ()
    # quick hack to show

    gtk.main ()



# Have we been called? Then just kick in and run our main function
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    main ()
