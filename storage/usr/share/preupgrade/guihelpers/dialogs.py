#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# Authors:
#    Tim Lauridsen <timlau@fedoraproject.org>

import gtk
import gobject

def questionDialog(parent, msg):
    ''' A question dialog with yes/no buttons'''
    dlg = gtk.MessageDialog(parent=parent,
                            type=gtk.MESSAGE_QUESTION,
                            buttons=gtk.BUTTONS_YES_NO)
    dlg.set_markup(cleanMarkupString(msg))
    rc = dlg.run()
    dlg.destroy()
    if rc == gtk.RESPONSE_YES:
        return True
    else:
        return False

def okDialog(parent, msg):
    ''' An info dialog with an ok button'''
    dlg = gtk.MessageDialog(parent=parent,
                            type=gtk.MESSAGE_INFO,
                            buttons=gtk.BUTTONS_OK)
    dlg.set_markup(cleanMarkupString(msg))
    rc = dlg.run()
    dlg.destroy()
    return rc

def errorDialog(parent, msg):
    ''' An error dialog with an ok button'''
    dlg = gtk.MessageDialog(parent=parent,
                            type=gtk.MESSAGE_ERROR,
                            buttons=gtk.BUTTONS_OK)
    dlg.set_markup(cleanMarkupString(msg))
    rc = dlg.run()
    dlg.destroy()
    return rc

def continueQuitDialog(parent, msg, button="Continue"):
    '''An error dialog with "Continue" and "Quit" buttons.
    Returns gtk.RESPONSE_YES if the user wishes to retry and
    gtk.RESPONSE_NO otherwise.'''
    dlg = gtk.MessageDialog(parent=parent,
                            type=gtk.MESSAGE_ERROR,
                            buttons=gtk.BUTTONS_NONE)
    dlg.add_buttons(button, gtk.RESPONSE_YES,
                    gtk.STOCK_QUIT, gtk.RESPONSE_NO)
    dlg.set_markup(cleanMarkupString(msg))
    rc = dlg.run()
    dlg.destroy()
    return rc

def retryDialog(parent, msg):
    '''An error dialog with "Retry" and "Quit" buttons.
    Returns gtk.RESPONSE_YES if the user wishes to continue and
    gtk.RESPONSE_NO otherwise.'''
    return continueQuitDialog(parent, msg, "Retry")


def cleanMarkupString(msg):
    msg = str(msg) # make sure it is a string
    msg = gobject.markup_escape_text(msg)
    return msg

if __name__ == '__main__':
    win = gtk.Window()
    win.set_title("Dialog Test")
    win.show()
    r = questionDialog(win,"This is a questionDialog")
    print "questionDialog returned %s" % r
    r = okDialog(win,"This is a okDialog")
    print "okDialog returned %s" % r
    r = errorDialog(win,"This is an errorDialog")
    print "errorDialog returned %s" % r
    r = retryDialog(win,"This is a retryDialog")
    print "retryDialog returned %s" % r
    win.hide()

