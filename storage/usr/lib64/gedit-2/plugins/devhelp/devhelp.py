# -*- coding: utf-8 py-indent-offset: 4 -*-
#
#    Gedit devhelp plugin
#    Copyright (C) 2006 Imendio AB
#
#    Author: Richard Hult <richard@imendio.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gedit
import gtk
import os
import gettext

class DevhelpInstance:
    def __init__(self, window):
        self._window = window

    def activate(self):
        manager = self._window.get_ui_manager()
	# Translate actions below, hardcoding domain here to avoid complications now
	_ = lambda s: gettext.dgettext('devhelp', s);

        self._action_group = gtk.ActionGroup("GeditDevhelpPluginActions")
        self._action_group.add_actions([('Devhelp', None,
                                         _('Show API Documentation'),
                                         'F2',
                                         _('Show API Documentation for the word at the cursor'),
                                         self.on_action_devhelp_activate)])
        
        self._merge_id = manager.new_merge_id()
        manager.insert_action_group(self._action_group, -1)		
        manager.add_ui(self._merge_id, '/MenuBar/ToolsMenu/ToolsOps_5',
                       'Devhelp', 'Devhelp', gtk.UI_MANAGER_MENUITEM, False)
        
    def deactivate(self):
        manager = self._window.get_ui_manager()
        manager.remove_ui(self._merge_id)
        manager.remove_action_group(self._action_group)
        self._action_group = None

    def _is_word_separator(self, c):
        return not (c.isalnum() or c == '_')

    def on_action_devhelp_activate(self, *args):
        view = self._window.get_active_view()
        buffer = view.get_buffer()

        # Get the word at the cursor
        insert = buffer.get_iter_at_mark(buffer.get_insert())

        start = insert.copy()
        end = insert.copy()

        # If just after a word, move back into it
        c = start.get_char()
        if self._is_word_separator(c):
            start.backward_char()

        # Go backward
        while True:
            c = start.get_char()
            if not self._is_word_separator(c):
                if not start.backward_char():
                    break
            else:
                start.forward_char()
                break

        # Go forward
        while True:
            c = end.get_char()
            if not self._is_word_separator(c):
                if not end.forward_char():
                    break
            else:
                break

        if end.compare(start) > 0:
            text = buffer.get_text(start,end).strip()
            if text:
                # FIXME: We need a dbus interface for devhelp soon...
                os.spawnlp(os.P_NOWAIT, 'devhelp', 'devhelp', '-s', text)
            

