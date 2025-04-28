#!/usr/bin/python

## ApacheControl - A Python Apache configuration utility for:
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

import string
import re

from ApacheGizmo import *

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

## helper function
def get_history (omenu):
    menu = omenu.get_menu ().get_active ()
    index = 0
    for menu_item in omenu.get_menu ().get_children ():
        if menu_item == menu:
            break
        index = index + 1
    return index

def check_ip(ip):
    splitted = ip.split(".")
    if len(splitted) != 4:
        return False
    try:
        numbers = [True for x in splitted if int(x) in range(0, 256)]
    except:
        return False
    return len(numbers) == 4

def check_port(port):
    try:
        iport = int(port)
    except:
        return False
    return iport >= 0 and iport <= 65535

class TestError(Exception):
    pass

##
## ApacheControl
##
class ApacheControl:

    def __init__ (self, xml):
        self.xml = xml
        self.curr_vh = None

    def write(self, force=False):
        return stack.apache.write(force)

###
### MAIN PAGE
###

    def hydrate_main (self):
        ## Main
        self.xml.get_widget ('server_name_entry').set_text (stack.apache.ServerName)
        self.xml.get_widget ('server_admin_entry').set_text (stack.apache.ServerAdmin)

        # Do Listen list.
        clist = self.xml.get_widget ("address_clist")
        for i in xrange (len (stack.apache.listener)):
            item = stack.apache.listener[i]
            if string.find(item, ':') >= 0:
                line = string.split (item, ':')
            else:
                line = ['*', item]

            if line[0] == "*":
                clist.append ([ _("All available addresses on port ") + line[1] ])
            else:
                clist.append ([ line[0] + line[1] ])

            clist.set_row_data (i, line)


        ## Virtual Hosts
        clist = self.xml.get_widget ('vhost_clist')
        for key in stack.apache.vhosts.keys ():
            vhost = stack.apache.vhosts[key]
            clist.append ([vhost.VHName, vhost.get_readable_address () ])

        ## Performance Tuning
        self.xml.get_widget ("max_clients_spin").set_value (stack.apache.MaxClients)
        self.xml.get_widget ('time_out_spin').set_value (stack.apache.TimeOut)
        self.xml.get_widget ('keep_alive_cbutton').set_active (stack.apache.KeepAlive == Apache.TRUE or stack.apache.KeepAlive == Apache.ON)

        if stack.apache.MaxRequestsPerChild == 0:
            self.xml.get_widget ('unlimited_cnxns_rbutton').set_active (True)
        else:
            self.xml.get_widget ('limited_cnxns_rbutton').set_active (True)
            self.xml.get_widget ('max_requests_per_child_spin').set_value (stack.apache.MaxRequestsPerChild)
        self.xml.get_widget ("keep_alive_spin").set_value (stack.apache.KeepAliveTimeout)


    def dehydrate_main (self):
        stack.push_state ()
        try:
            offset = 0
            widget = self.xml.get_widget ('server_name_entry')
            stack.apache.ServerName = widget.get_text ()
            widget = self.xml.get_widget ('server_admin_entry')
            stack.apache.ServerAdmin = widget.get_text ()
            widget = self.xml.get_widget ("address_clist")
            stack.apache.listener.clear()
            if widget.rows > 0:
                for i in xrange (widget.rows):
                    (address_text, port) = widget.get_row_data (i)
                    stack.apache.listener.add (address_text + ":" + port)

            offset = 1
            name_based_vh = []
            if stack.apache.vhosts != None:
                for i in stack.apache.vhosts.keys ():
                    vhost = stack.apache.vhosts[i]
                    if vhost.NameBased == VirtualHost.HOST_TYPE_NAME and not vhost.Address in name_based_vh:
                        name_based_vh.append (vhost.Address)
                stack.apache.NameVirtualHosts = name_based_vh
            else:
                stack.apache.NameVirtualHosts = None

            clist = self.xml.get_widget ('vhost_clist')
            for i in xrange (clist.rows - 1):
                vhname = clist.get_text (i, 0)
                stack.apache.vhosts.move (vhname, i)

            offset = 3
            widget = self.xml.get_widget ("max_clients_spin")
            stack.apache.MaxClients = int (widget.get_text ())
            widget = self.xml.get_widget ('time_out_spin')
            stack.apache.TimeOut = int (widget.get_text ())
            widget = None
            if self.xml.get_widget ('keep_alive_cbutton').get_active():
                stack.apache.KeepAlive = Apache.ON
            else:
                stack.apache.KeepAlive = Apache.OFF

            if self.xml.get_widget ('unlimited_cnxns_rbutton').get_active ():
                stack.apache.MaxRequestsPerChild = 0
            else:
                widget = self.xml.get_widget ('max_requests_per_child_spin')
                stack.apache.MaxRequestsPerChild = int (widget.get_text ())
            widget = self.xml.get_widget ("keep_alive_spin")
            stack.apache.KeepAliveTimeout = int (widget.get_text ())
        except TestError, message:
            stack.pop_restore ()
            raise TestError, (message, offset, widget)
        except '*', message:
            stack.pop_restore ()
            raise TestError, ("Generic Error: " + message, None, None)
        stack.pop ()

###
### VIRTUAL HOSTS
###

    def hydrate_vhost (self, name=None):
        stack.push_state ()

        if name == None:
            vhost = stack.apache.vhosts.add ()
        else:
            vhost = stack.apache.vhosts[name]

        self.curr_vh = vhost.VHName

        self._hydrate_vhost_page_1 (vhost)
        self._hydrate_vhost_page_2 (vhost)
        self._hydrate_vhost_page_3 (vhost)
        self._hydrate_vhost_page_4 (vhost)
        self._hydrate_vhost_page_5 (vhost)
        self._hydrate_vhost_page_6 (vhost)

    def hydrate_default_vhost (self):
        stack.push_state ()
        vhost = stack.apache.default_vhost

        self._hydrate_vhost_page_2 (vhost)
        self._hydrate_vhost_page_4 (vhost)
        self._hydrate_vhost_page_5 (vhost)
        self._hydrate_vhost_page_6 (vhost)

    def dehydrate_vhost (self):
        vhost = stack.apache.vhosts[self.curr_vh]

        self._dehydrate_vhost_page_1 (vhost)
        self._dehydrate_vhost_page_2 (vhost)
        self._dehydrate_vhost_page_3 (vhost)
        self._dehydrate_vhost_page_4 (vhost)
        self._dehydrate_vhost_page_5 (vhost)
        self._dehydrate_vhost_page_6 (vhost)

        stack.pop ()
        return (vhost.VHName, vhost.get_readable_address ())

    def dehydrate_default_vhost (self):
        vhost = stack.apache.default_vhost

        self._dehydrate_vhost_page_2 (vhost)
        self._dehydrate_vhost_page_4 (vhost)
        self._dehydrate_vhost_page_5 (vhost)
        self._dehydrate_vhost_page_6 (vhost)
        self.curr_vh = None
        stack.pop ()

    def discard_vhost (self):
        self.curr_vh = None
        stack.pop_restore ()

    def remove_vhost (self, name):
        del stack.apache.vhosts[name]

    def _hydrate_vhost_page_1 (self, vhost):
        self.xml.get_widget ('vhost_name_entry').set_text (vhost.VHName)
        self.xml.get_widget ('vhost_document_root_entry').set_text (vhost.DocumentRoot)
        self.xml.get_widget ('vhost_server_admin_entry').set_text (vhost.ServerAdmin)

        if vhost.NameBased == VirtualHost.HOST_TYPE_DEFAULT:
            self.xml.get_widget ('vhost_type_omenu').set_history (2)
            self.xml.get_widget ('host_info_notebook').set_current_page (2)
            self.xml.get_widget ('name_vhost_ip_entry').set_text ("")
            self.xml.get_widget ('ip_vhost_ip_entry').set_text ("")
            self.xml.get_widget ('name_vhost_host_name_entry').set_text ("")
            self.xml.get_widget ('ip_vhost_host_name_entry').set_text ("")
            self.xml.get_widget ('vhost_alias_clist').clear ()
            server = vhost.ServerName
            if server == VirtualHost.DEFAULT:
                self.xml.get_widget ('default_vhost_all_hosts_rbutton').set_active (True)
                self.xml.get_widget ('default_vhost_all_port_entry').set_text ("")
            else:
                match = re.match (r'_default_:([0-9]+)', server)
                try:
                    port = match.groups()[0]
                except:
                    port = ""
                self.xml.get_widget ('default_vhost_all_port_rbutton').set_active (True)
                self.xml.get_widget ('default_vhost_all_port_entry').set_text (port)
        else:
            self.xml.get_widget ('name_vhost_ip_entry').set_text (vhost.Address)
            self.xml.get_widget ('ip_vhost_ip_entry').set_text (vhost.Address)
            self.xml.get_widget ('name_vhost_host_name_entry').set_text (vhost.ServerName)
            self.xml.get_widget ('ip_vhost_host_name_entry').set_text (vhost.ServerName)
            aliases = vhost.Aliases
            clist = self.xml.get_widget ('vhost_alias_clist')
            clist.clear()
            for alias in aliases:
                clist.append ( [ alias ] )

            if vhost.NameBased == VirtualHost.HOST_TYPE_IP:
                self.xml.get_widget ('vhost_type_omenu').set_history (0)
                self.xml.get_widget ('host_info_notebook').set_current_page (0)
            elif vhost.NameBased == VirtualHost.HOST_TYPE_NAME:
                self.xml.get_widget ('vhost_type_omenu').set_history (1)
                self.xml.get_widget ('host_info_notebook').set_current_page (1)



    def _dehydrate_vhost_page_1 (self, vhost):
        try:
            widget = self.xml.get_widget ('vhost_name_entry')
            vhost.VHName = widget.get_text ()
            widget = self.xml.get_widget ('vhost_document_root_entry')
            vhost.DocumentRoot = widget.get_text ()
            widget = self.xml.get_widget ('vhost_server_admin_entry')
            vhost.ServerAdmin = widget.get_text ()

            widget = self.xml.get_widget('vhost_type_omenu').get_menu ()
            behaviour = widget.get_active ()
            index = 0
            for menu_item in widget.get_children ():
                if menu_item == behaviour:
                    break
                index = index + 1

            if index == 0:
                vhost.NameBased = VirtualHost.HOST_TYPE_IP
                widget = self.xml.get_widget ('ip_vhost_ip_entry')
                vhost.Address = widget.get_text ()
                widget = self.xml.get_widget ('ip_vhost_host_name_entry')
                vhost.ServerName = widget.get_text ()
            elif index == 1:
                vhost.NameBased = VirtualHost.HOST_TYPE_NAME
                widget = self.xml.get_widget ('name_vhost_ip_entry')
                address = widget.get_text ()
                if address != "" and not check_ip (address):
                    raise TestError, _("Inserted IP address is not valid.")
                vhost.Address = widget.get_text ()
                widget = self.xml.get_widget ('name_vhost_host_name_entry')
                vhost.ServerName = widget.get_text ()
            else:
                vhost.NameBased = VirtualHost.HOST_TYPE_DEFAULT
                widget = None
                if self.xml.get_widget ('default_vhost_all_port_rbutton').get_active ():
                    widget = self.xml.get_widget ('default_vhost_all_port_entry')
                    port = widget.get_text ()
                    vhost.ServerName = VirtualHost.DEFAULT + ':' + port
                    vhost.Address = "*:" + port
                else:
                    vhost.ServerName = VirtualHost.DEFAULT
                    vhost.Address = "*"


            widget = self.xml.get_widget ('vhost_alias_clist')
            aliases = []
            for i in xrange (widget.rows):
                aliases.append (widget.get_text (i, 0))
            vhost.Aliases = aliases
        except TestError, message:
            raise TestError, (message, 0, widget)

    def _hydrate_vhost_page_2 (self, vhost):
        ## Directory Index
        clist = self.xml.get_widget ('directory_index_clist')
        clist.clear ()

        if vhost.DirectoryIndex != None:
            for i in string.split (vhost.DirectoryIndex):
                clist.append ( [ i ] )
            clist.select_row (0, 0)

        ## Error documents
        clist = self.xml.get_widget ('error_doc_list_swindow').get_data ('clist')
        clist.set_to_default ()
        keys = vhost.ErrorDocuments.keys ()
        for i in xrange (clist.rows):
            key = clist.get_row_data (i)
            if key in keys:
                value = vhost.ErrorDocuments[key]
                if value[0:5] == 'file:':
                    clist.set_text (i, 1, _("File"))
                    clist.set_text (i, 2, value[5:])
                else:
                    clist.set_text (i, 1, 'URL')
                    clist.set_text (i, 2, value[:])

        ## Error page footer (ServerSignature option)
        if vhost.ServerSignature == VirtualHost.SERVER_SIGNATURE_OFF:
            self.xml.get_widget ('ServerSignatureOption').set_history (0)
        elif vhost.ServerSignature == VirtualHost.SERVER_SIGNATURE_ON:
            self.xml.get_widget ('ServerSignatureOption').set_history (1)
        else:
            self.xml.get_widget ('ServerSignatureOption').set_history (2)

    def _dehydrate_vhost_page_2 (self, vhost):
        try:
            widget = self.xml.get_widget ('directory_index_clist')
            if widget.rows > 0:
                dir_index = widget.get_text (0, 0)
                for i in xrange (1, widget.rows):
                    dir_index = dir_index + " " + widget.get_text (i, 0)
                vhost.DirectoryIndex = dir_index

            ## Error documents
            clist = self.xml.get_widget ('error_doc_list_swindow').get_data ('clist')
            widget = clist
            for i in xrange (clist.rows):
                type = clist.get_text (i, 1)
                if type == _("default"):
                    try:
                        del vhost.ErrorDocuments[clist.get_row_data (i)]
                    except:
                        pass
                    continue
                elif type == 'URL':
                    value = clist.get_text (i, 2)
                else:
                    value = 'file:' + clist.get_text (i, 2)

                vhost.ErrorDocuments[clist.get_row_data (i)] = value

            widget = self.xml.get_widget('ServerSignatureOption').get_menu ()
            behaviour = widget.get_active ()
            index = 0
            for menu_item in widget.get_children ():
                if menu_item == behaviour:
                    break
                index = index + 1

            if index == 0:
                vhost.ServerSignature = VirtualHost.SERVER_SIGNATURE_OFF
            elif index == 1:
                vhost.ServerSignature = VirtualHost.SERVER_SIGNATURE_ON
            else:
                vhost.ServerSignature = VirtualHost.SERVER_SIGNATURE_EMAIL

        except TestError, message:
            raise TestError, (message, 0, widget)

    def _hydrate_vhost_page_3 (self, vhost):
        if vhost.SSLEngine:
            self.xml.get_widget ('ssl_engine_cbox').set_active (vhost.SSLEngine == Apache.ON)
        if vhost.SSLCertificateFile:
            self.xml.get_widget ('ssl_certificate_file_entry').set_text (vhost.SSLCertificateFile)
        if vhost.SSLCertificateKeyFile:
            self.xml.get_widget ('ssl_certificate_key_entry').set_text (vhost.SSLCertificateKeyFile)
        if vhost.SSLCertificateChainFile:
            self.xml.get_widget ('ssl_certificate_chain_entry').set_text (vhost.SSLCertificateChainFile)
        if vhost.SSLCACertificateFile:
            self.xml.get_widget ('ssl_certificate_authority_entry').set_text (vhost.SSLCACertificateFile)

        clist = self.xml.get_widget ("ssl_vbox").get_data ("ssl_clist")
        clist.initialize_from_list (string.split (vhost.SSLOptions))

    def _dehydrate_vhost_page_3 (self, vhost):
        try:
            widget = self.xml.get_widget ('ssl_engine_cbox')
            if widget.get_active ():
                vhost.SSLEngine = Apache.ON
            else:
                vhost.SSLEngine = Apache.OFF

            text = self.xml.get_widget ('ssl_certificate_file_entry').get_text ()
            if text != "":
                vhost.SSLCertificateFile = text
            else:
                vhost.SSLCertificateFile = None

            text = self.xml.get_widget ('ssl_certificate_key_entry').get_text ()
            if text != "":
                vhost.SSLCertificateKeyFile = text
            else:
                vhost.SSLCertificateKeyFile = None

            text = self.xml.get_widget ('ssl_certificate_chain_entry').get_text ()
            if text != "":
                vhost.SSLCertificateChainFile = text
            else:
                vhost.SSLCertificateChainFile = None

            text = self.xml.get_widget ('ssl_certificate_authority_entry').get_text ()
            if text != "":
                vhost.SSLCACertificateFile = text
            else:
                vhost.SSLCACertificateFile = None

            widget = self.xml.get_widget ("ssl_vbox").get_data ("ssl_clist")
            list = widget.dump_to_list ()
            options = ""
            first = True
            for i in list:
                if first:
                    options = options + i
                    first = False
                else:
                    options = options + " " + i
            vhost.SSLOptions = options
        except TestError, message:
            raise TestError, (message, 3, widget)

    def _hydrate_vhost_page_4 (self, vhost):
        # Transfer log
        self.xml.get_widget ('transfer_log_to_program_entry').set_text ("")
        self.xml.get_widget ('transfer_use_system_log_entry').set_text ("")
        self.xml.get_widget ('transfer_log_to_file_real_entry').set_text ("")

        if len (vhost.TransferLog) > 0:
            if vhost.TransferLog [0] == '|':
                self.xml.get_widget ('transfer_log_to_prog_rbutton').set_active (True)
                self.xml.get_widget ('transfer_log_to_program_entry').set_text (vhost.TransferLog[1:])
            elif vhost.TransferLog[0:7] == 'syslog:':
                self.xml.get_widget ('transfer_sys_log_rbutton').set_active(True)
                self.xml.get_widget ('transfer_use_system_log_entry').set_text (vhost.TransferLog[7:])
            else:
                self.xml.get_widget ('transfer_log_to_file_rbutton').set_active(True)
                self.xml.get_widget ('transfer_log_to_file_real_entry').set_text (vhost.TransferLog)

	if vhost.LogFormat:
        	self.xml.get_widget ('custom_log_cbutton').set_active (len (vhost.LogFormat) > 0)
        	self.xml.get_widget ('custom_log_string_entry').set_text (vhost.LogFormat)
	else:
        	self.xml.get_widget ('custom_log_cbutton').set_active (0)

        # Error log
        self.xml.get_widget ('error_log_to_program_entry').set_text ("")
        self.xml.get_widget ('error_use_system_log_entry').set_text ("")
        self.xml.get_widget ('error_log_to_file_real_entry').set_text ("")
        if len (vhost.ErrorLog) > 0:
            if   vhost.ErrorLog[0] == '|':
                self.xml.get_widget ('error_log_to_prog_rbutton').set_active (True)
                self.xml.get_widget ('error_log_to_program_entry').set_text (vhost.ErrorLog[1:])
            elif vhost.ErrorLog[0:7] == 'syslog:':
                self.xml.get_widget ('error_sys_log_rbutton').set_active(True)
                self.xml.get_widget ('error_use_system_log_entry').set_text (vhost.ErrorLog[7:])
            else:
                self.xml.get_widget ('error_log_to_file_rbutton').set_active(True)
                self.xml.get_widget ('error_log_to_file_real_entry').set_text (vhost.ErrorLog)

        for i in xrange (len (VirtualHost.LOG_LEVELS)):
            if VirtualHost.LOG_LEVELS[i] == vhost.LogLevel:
                break
        self.xml.get_widget ('error_log_level_omenu').set_history(i)

        if   vhost.HostNameLookups == VirtualHost.SERVER_HOST_NAME_LOOKUP_OFF:
            self.xml.get_widget ('reverse_lookup_omenu').set_history(0)
        elif vhost.HostNameLookups == VirtualHost.SERVER_HOST_NAME_LOOKUP_ON:
            self.xml.get_widget ('reverse_lookup_omenu').set_history(1)
        else:
            self.xml.get_widget ('reverse_lookup_omenu').set_history(2)

    def _dehydrate_vhost_page_4 (self, vhost):
        try:
            # Transfer log
            if self.xml.get_widget ('transfer_log_to_prog_rbutton').get_active ():
                widget = self.xml.get_widget ('transfer_log_to_program_entry')
                vhost.TransferLog = '|' + widget.get_text ()
            elif self.xml.get_widget ('transfer_sys_log_rbutton').get_active ():
                widget = self.xml.get_widget ('transfer_use_system_log_entry')
                vhost.TransferLog = 'syslog:' + widget.get_text ()
            else:
                widget = self.xml.get_widget ('transfer_log_to_file_real_entry')
                vhost.TransferLog = widget.get_text ()

            if self.xml.get_widget ('custom_log_cbutton').get_active ():
                widget = self.xml.get_widget ('custom_log_string_entry')
                vhost.LogFormat = widget.get_text ()
            else:
                vhost.LogFormat = None

            # Error log
            if self.xml.get_widget ('error_log_to_prog_rbutton').get_active ():
                widget = self.xml.get_widget ('error_log_to_program_entry')
                vhost.ErrorLog = '|' + widget.get_text ()
            elif self.xml.get_widget ('error_sys_log_rbutton').get_active ():
                widget = self.xml.get_widget ('error_use_system_log_entry')
                vhost.ErrorLog = 'syslog:' + widget.get_text ()
            else:
                widget = self.xml.get_widget ('error_log_to_file_real_entry')
                vhost.ErrorLog = widget.get_text ()

            widget = self.xml.get_widget ('error_log_level_omenu')
            i = get_history (widget)
            vhost.LogLevel = VirtualHost.LOG_LEVELS[i]

            widget = self.xml.get_widget ('reverse_lookup_omenu')
            i = get_history (widget)
            if i == 0:
                vhost.HostNameLookups = VirtualHost.SERVER_HOST_NAME_LOOKUP_OFF
            elif i == 1:
                vhost.HostNameLookups = VirtualHost.SERVER_HOST_NAME_LOOKUP_ON
            else:
                vhost.HostNameLookups = VirtualHost.SERVER_HOST_NAME_LOOKUP_DOUBLE

        except TestError, message:
            raise TestError, (message, 4, widget)


    def _hydrate_vhost_page_5 (self, vhost):
        sclist = self.xml.get_widget ("set_env_clist")
        sclist.clear ()
        for var in vhost.SetEnv.keys ():
            sclist.append ( (var, vhost.SetEnv[var]) )

        pclist = self.xml.get_widget ("pass_env_clist")
        pclist.clear ()
        for var in vhost.PassEnv:
            pclist.append ( [var] )

        uclist = self.xml.get_widget ("unset_env_clist")
        uclist.clear ()
        for var in vhost.UnsetEnv:
            uclist.append ( [var] )

    def _dehydrate_vhost_page_5 (self, vhost):
        clist = self.xml.get_widget ("set_env_clist")
        env = {}
        for i in xrange (clist.rows):
            env[clist.get_text (i, 0)] = clist.get_text (i, 1)
        vhost.SetEnv = env

        clist = self.xml.get_widget ("pass_env_clist")
        env = []
        for i in xrange (clist.rows):
            env.append (clist.get_text (i, 0))
        vhost.PassEnv = env

        clist = self.xml.get_widget ("unset_env_clist")
        env = []
        for i in xrange (clist.rows):
            env.append (clist.get_text (i, 0))
        vhost.UnsetEnv = env

    def _hydrate_vhost_page_6 (self, vhost):
        clist = self.xml.get_widget ("dir_options_clist")
        clist.clear ()
        if vhost.directories.keys ():
            for dirname in vhost.directories.keys ():
                row = clist.append ( [dirname] )
            clist.select_row (0, 0)

        options_list = vhost.Options

        options = _("[ No Options ]")
        count = 0
        for i in options_list:
            if count == 0:
                options = i
            elif count == 4:
                options = options + "\n" + i
            else:
                options = options + ", " + i
            count = count + 1

        self.xml.get_widget ("default_dir_options_label").set_text (options)

    def _dehydrate_vhost_page_6 (self, vhost):
        # nothing here needs dehydrating -- the Options and the dirs have already taken
        # care of themselves.
        pass

###
### Directory stuff
###

    def hydrate_default_dir_options (self, dialog):
        if self.curr_vh:
            vhost = stack.apache.vhosts[self.curr_vh]
        else:
            vhost = stack.apache.default_vhost

        dialog.get_data ("clist").set_from_list (vhost.Options)

    def dehydrate_default_dir_options (self, dialog):
        if self.curr_vh:
            vhost = stack.apache.vhosts[self.curr_vh]
        else:
            vhost = stack.apache.default_vhost
        clist = dialog.get_data ("clist")

        options_list = clist.set_to_list ()
        vhost.Options = options_list

        options = _("[ No Options ]")
        count = 0
        for i in options_list:
            if count == 0:
                options = i
            elif count == 4:
                options = options + "\n" + i
            else:
                options = options + ", " + i
            count = count + 1
        self.xml.get_widget ("default_dir_options_label").set_text (options)


    def hydrate_dir_options (self, dir_name = None):
        stack.push_state ()
        if self.curr_vh:
            vhost = stack.apache.vhosts[self.curr_vh]
        else:
            vhost = stack.apache.default_vhost

        dir_entry = self.xml.get_widget ("directory_options_dialog_dir_entry")
        clist = self.xml.get_widget ("directory_options_dialog").get_data ("clist")

        if dir_name == None:
            self.xml.get_widget ("allow_override_cbox").set_active (False)
            self.xml.get_widget ("dir_opt_dialog_let_all_rbutton").set_active (True)
            self.xml.get_widget ("dir_opt_dialog_deny_all_rbutton").set_active (True)
            self.xml.get_widget ("deny_list_entry").set_text ("")
            self.xml.get_widget ("dir_opt_dialog_allow_all_rbutton").set_active (True)
            self.xml.get_widget ("allow_list_entry").set_text ("")
            clist.set_to_default ()

            dir_default = self.xml.get_widget ("vhost_document_root_entry").get_text ()
            if len (dir_default) > 1 and dir_default[-1] != '/':
                dir_default = dir_default + "/"
            dir_entry.set_text (dir_default)
            dir_entry.grab_focus ()
            dir_entry.set_position (-1)
        else:
            dir = vhost.directories[dir_name]
            dir_entry.set_text (dir.Dir)
            self.xml.get_widget ("allow_override_cbox").set_active (dir.AllowOverride == Apache.ALL)
            clist.set_from_list (dir.Options)
            if dir.Mode == Directory.ALL_HOSTS:
                self.xml.get_widget ("dir_opt_dialog_let_all_rbutton").set_active (True)
                self.xml.get_widget ("dir_opt_dialog_deny_all_rbutton").set_active (True)
                self.xml.get_widget ("dir_opt_dialog_allow_all_rbutton").set_active (True)
                self.xml.get_widget ("deny_list_entry").set_text ("")
                self.xml.get_widget ("allow_list_entry").set_text ("")
            else:
                if dir.Mode == Directory.ALLOW_FIRST:
                    self.xml.get_widget ("dir_opt_dialog_allow_first_rbutton").set_active (True)
                else:
                    self.xml.get_widget ("dir_opt_dialog_deny_first_rbutton").set_active (True)

                if dir.Deny == Directory.FROM_ALL or dir.Deny == "from all":
                    dir.Deny = Directory.FROM_ALL
                    self.xml.get_widget ("dir_opt_dialog_deny_all_rbutton").set_active (True)
                    self.xml.get_widget ("deny_list_entry").set_text ("")
                else:
                    self.xml.get_widget ("dir_opt_dialog_deny_from_rbutton").set_active (True)
                    self.xml.get_widget ("deny_list_entry").set_text (dir.Deny)

                if dir.Allow == Directory.FROM_ALL or dir.Allow == "from all":
                    dir.Allow = Directory.FROM_ALL
                    self.xml.get_widget ("dir_opt_dialog_allow_all_rbutton").set_active (True)
                    self.xml.get_widget ("allow_list_entry").set_text ("")
                else:
                    self.xml.get_widget ("dir_opt_dialog_allow_from_rbutton").set_active (True)
                    self.xml.get_widget ("allow_list_entry").set_text (dir.Allow)
        dir_entry.grab_focus ()

    def dehydrate_dir_options (self, old_name=None):
        widget = None

        try:
            if self.curr_vh:
                vhost = stack.apache.vhosts[self.curr_vh]
            else:
                vhost = stack.apache.default_vhost

            widget = self.xml.get_widget ("directory_options_dialog_dir_entry")
            new_name = widget.get_text ()
            if old_name:
                dir = vhost.directories[old_name]
                dir.Dir = new_name
            else:
                try:
                    dir = vhost.directories.add (new_name)
                except KeyError:
                    raise TestError, (_("A directory named %s already exists.") % new_name)

            if self.xml.get_widget ("dir_opt_dialog_let_all_rbutton").get_active ():
                dir.Mode = Directory.ALL_HOSTS
            else:
                if self.xml.get_widget ("dir_opt_dialog_deny_first_rbutton").get_active ():
                    dir.Mode = Directory.DENY_FIRST
                else:
                    dir.Mode = Directory.ALLOW_FIRST
                if self.xml.get_widget ("dir_opt_dialog_deny_all_rbutton").get_active ():
                    dir.Deny = Directory.FROM_ALL
                else:
                    widget = self.xml.get_widget ("deny_list_entry")
                    dir.Deny = widget.get_text ()
                if self.xml.get_widget ("dir_opt_dialog_allow_all_rbutton").get_active ():
                    dir.Allow = Directory.FROM_ALL
                else:
                    widget = self.xml.get_widget ("allow_list_entry")
                    dir.Allow = widget.get_text ()

            clist = self.xml.get_widget ("directory_options_dialog").get_data ("clist")
            dir.Options = clist.set_to_list ()

            if self.xml.get_widget ("allow_override_cbox").get_active ():
                dir.AllowOverride = Apache.ALL
            else:
                dir.AllowOverride = Apache.NONE
            stack.pop ()
            return new_name
        except TestError, message:
            raise TestError, (message, 0, widget)

    def discard_dir_options (self):
        stack.pop_restore ()

    def remove_dir_option (self, name):
        if self.curr_vh:
            vhost = stack.apache.vhosts[self.curr_vh]
        else:
            vhost = stack.apache.default_vhost
        del vhost.directories[name]
