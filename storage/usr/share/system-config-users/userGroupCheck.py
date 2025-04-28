# -*- coding: utf-8 -*-
#
# userGroupCheck.py - code to make sure that the user/group input is valid
# Copyright © 2001 - 2005, 2007 - 2009 Red Hat, Inc.
# Copyright © 2001 - 2003 Brent Fox <bfox@redhat.com>
# Copyright © 2004 - 2005 Nils Philippsen <nils@redhat.com>
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# Authors:
# Brent Fox
# Nils Philippsen <nils@redhat.com>

import os
import string
import libuser
import messageDialog
import gtk

import gettext
_ = lambda x: gettext.ldgettext ("system-config-users", x)

have_cracklib = False
try:
    import cracklib
    have_cracklib = True
    if "VeryFascistCheck" in dir (cracklib):
        have_cracklib_2_8_13 = True
    else:
        have_cracklib_2_8_13 = False
except ImportError:
    pass

maxusernamelength = libuser.UT_NAMESIZE - 1
maxgroupnamelength = libuser.UT_NAMESIZE - 1
maxfilenamelength = os.pathconf ('/', os.pathconf_names['PC_NAME_MAX'])
maxpathlength = os.pathconf ('/', os.pathconf_names['PC_PATH_MAX'])

user_msgs = {
    "empty": _("Please enter a user name."),
    "too_long": _("The user name must not exceed %d characters."),
    "whitespace": _("The user name '%s' contains whitespace. Please do not include whitespace in the user name."),
    "dollarsign": _("The user name '%s' contains a dollar sign which is not at the end. Please use dollar signs only at the end of user names to indicate Samba machine accounts."),
    "dollarsign_end": _("The user name '%s' contains a trailing dollar sign. This should only be used for Samba machine accounts, using this for a normal user account can cause problems with some software. Is the account in question a Samba machine account?"),
    "illegal_chars": _("The user name '%(name)s' contains an invalid character at position %(position)d."),
    "alldigits": _("Using all numbers as the user name can cause confusion about whether the user name or numerical user id is meant. Do you really want to use a numerical-only user name?")
    }

group_msgs = {
    "empty": _("Please enter a group name."),
    "too_long": _("The group name must not exceed %d characters."),
    "whitespace": _("The group name '%s' contains whitespace. Please do not include whitespace in the group name."),
    "illegal_chars": _("The group name '%(name)s' contains an invalid character at position %(position)d."),
    "alldigits": _("Using all numbers as the group name can cause confusion about whether the group name or numerical group id is meant. Do you really want to use a numerical-only group name?")
    }

def isUserGroupNameOk (type, name, widget):
    if type == 'user':
        msgs = user_msgs
        maxnamelength = maxusernamelength
    if type == 'group':
        msgs = group_msgs
        maxnamelength = maxgroupnamelength

    if len (string.strip (name)) == 0:
        messageDialog.show_message_dialog (msgs["empty"])
        widget.set_text ("")
        widget.grab_focus ()
        return False
        
    if len(name) > maxnamelength:
        messageDialog.show_message_dialog (msgs["too_long"] % (maxusernamelength))
        widget.set_text ("")
        widget.grab_focus ()
        return False

    alldigits = True
    dollarsign_end = False

    for i, j in map (lambda x: (name[x], x), range (len (name))):
        if i == "_" or (i == "-" and j != 0):
            #specifically allow "-" (except at the beginning), "_"
            alldigits = False
            continue

        if (type == "user" and i == "$" and j != 0 and j == len (name) - 1):
            # allow "$" at the end for Samba machine accounts, but get
            # confirmation
            alldigits = False
            dollarsign_end = True
            continue

        if i == "$":
            messageDialog.show_message_dialog (msgs["dollarsign"] % (name))
            widget.set_text ("")
            widget.grab_focus ()
            return False

        if i not in string.ascii_letters and i not in string.digits and i != '.': 
            messageDialog.show_message_dialog (msgs["illegal_chars"] % {'name': name, 'position': j+1})
            widget.set_text ("")
            widget.grab_focus ()
            return False

        if i not in string.digits:
            alldigits = False

    if alldigits:
        yesno = messageDialog.show_confirm_dialog (msgs["alldigits"])
        widget.set_text ("")
        widget.grab_focus ()
        if yesno != gtk.RESPONSE_YES:
            return False

    if dollarsign_end:
        yesno = messageDialog.show_confirm_dialog (msgs["dollarsign_end"] % (name))
        widget.set_text ("")
        widget.grab_focus ()
        if yesno != gtk.RESPONSE_YES:
            return False

    return True

def isUsernameOk (candidate, widget):
    return isUserGroupNameOk ('user', candidate, widget)

def isGroupnameOk(candidate, widget):
    return isUserGroupNameOk ('group', candidate, widget)

def isPasswordOk(candidate, widget):
    for i in candidate:
        if i not in string.ascii_letters and i not in string.digits and i not in string.punctuation and i not in string.whitespace:
            messageDialog.show_message_dialog(_("The password contains invalid characters.  "
                                                "Please use only ASCII characters."))
            widget.set_text("")
            widget.grab_focus()
            return False

    # if cracklib is available, check the password for weaknesses
    if not have_cracklib:
        return True

    clerror = None
    # if cracklib >= 2.8.13 we have VeryFascistCheck() and new semantics
    if have_cracklib_2_8_13:
        try:
            cracklib.VeryFascistCheck (candidate)
        except ValueError, e:
            clerror = str (e)
    else:
        clerror = cracklib.FascistCheck (candidate)

    if clerror:
        # translate error message
        clerror = gettext.ldgettext ("cracklib", clerror)
        rc = messageDialog.show_confirm_dialog (_("The chosen password is too weak: %s. Do you want to use it anyway?") % clerror)
        if rc != gtk.RESPONSE_YES:
            return False

    return True

def isNameOk(candidate, widget):
    try:
        dummy = candidate.decode ('utf-8')
    except UnicodeDecodeError:
        #have to check for whitespace for gecos, since whitespace is ok
        messageDialog.show_message_dialog(_("The name '%s' contains invalid characters.  "
                                            "Please use only UTF-8 characters.") % candidate)
        widget.set_text("")
        widget.grab_focus()
        return False

    if string.find(candidate, ":") >= 0:
            #have to check for colons since /etc/passwd is a colon delimited file
            messageDialog.show_message_dialog(_("The name '%s' contains a colon.  "
                                                "Please do not use colons in the name.") % candidate)
            widget.set_text("")
            widget.grab_focus()
            return False
    return True

def isHomedirOk(candidate, widget, need_homedir = False):
    if need_homedir and len (string.strip(candidate)) == 0:
        messageDialog.show_message_dialog (_("Please enter a home directory."))
        widget.set_text ("")
        widget.grab_focus ()
        return False

    if string.find (candidate, ":") >= 0:
        # have to check for colons since /etc/passwd is a colon delimited file
        messageDialog.show_message_dialog (_("The directory name '%s' contains a colon.  "
                                             "Please do not use colons in the directory name.") % candidate)
        widget.set_text ("")
        widget.grab_focus ()
        return False

    str_split = candidate.split ('/')

    if len (str_split[0]) > 0:
        messageDialog.show_message_dialog (_("The directory name '%s' doesn't begin with a '/'. Please specify an absolute path for the home directory.") % candidate)
        widget.set_text ("")
        widget.grab_focus ()
        return False

    if max (map (lambda x: len (x), str_split)) > maxfilenamelength:
        messageDialog.show_message_dialog (_("The directory name '%s' has path components which are too long. Please use shorter path components for the home directory.") % candidate)
        widget.set_text ("")
        widget.grab_focus ()
        return False

    try:
        if min (map (lambda x: len (x), str_split[1:-1])) == 0:
            messageDialog.show_message_dialog (_("The directory name '%s' contains empty path components. Please specify a home directory name without empty path components.") % candidate)
            widget.set_text ("")
            widget.grab_focus ()
            return False
    except ValueError:
        # too few components
        pass

    if '.' in str_split or '..' in str_split:
        messageDialog.show_message_dialog (_("The directory name '%s' contains illegal path components. Please don't use '.' or '..' as path components for the home directory.") % candidate)
        widget.set_text ("")
        widget.grab_focus ()
        return False

    return True

def userExists (luadmin, user):
    user = luadmin.lookupUserByName (user)
    if user:
        del (user)
        return True
    return False

def groupExists (luadmin, group):
    group = luadmin.lookupGroupByName (group)
    if group:
        del (group)
        return True
    return False
