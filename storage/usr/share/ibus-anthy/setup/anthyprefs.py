# -*- coding: utf-8 -*-
# vim:set noet ts=4:
#
# ibus-anthy - The Anthy engine for IBus
#
# Copyright (c) 2007-2008 Peng Huang <shawn.p.huang@gmail.com>
# Copyright (c) 2009 Hideaki ABE <abe.sendai@gmail.com>
# Copyright (c) 2007-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import gtk
import sys

from prefs import Prefs

N_ = lambda a : a

__all__ = ['AnthyPrefs']


class AnthyPrefs(Prefs):
    _prefix = 'engine/anthy'

    def __init__(self, bus=None, config=None):
        super(AnthyPrefs, self).__init__(bus, config)
        self.default = _config

        # The keys will be EOSL in the near future.
        self.__update_key ("common",
                           "behivior_on_focus_out",
                           "behavior_on_focus_out")
        self.__update_key ("common",
                           "behivior_on_period",
                           "behavior_on_period")
        self.fetch_all()

    def __update_key (self, section, old_key, new_key):
        file = __file__
        if __file__.find('/') >= 0:
            file = __file__[__file__.rindex('/') + 1:]
        warning_message = \
            "(" + file + ") ibus-anthy-WARNING **: "                        \
            "The key (" + old_key + ") will be removed in the future. "     \
            "Currently the key (" + new_key + ") is used instead. "         \
            "The ibus keys are defined in " +                               \
            "/".join(["/desktop/ibus", self._prefix, section]) + " ."

        if not self.fetch_item(section, old_key, True):
            return
        print >> sys.stderr, warning_message
        if self.fetch_item(section, new_key, True):
            return

        self.fetch_item(section, old_key)
        value = self.get_value(section, old_key)
        self.set_value(section, new_key, value)
        self.commit_item(section, new_key)
        self.undo_item(section, new_key)

    def keys(self, section):
        if section.startswith('shortcut/'):
            return _cmd_keys
        return self.default[section].keys()


_cmd_keys = [
    "on_off",
    "circle_input_mode",
    "circle_kana_mode",
    "latin_mode",
    "wide_latin_mode",
    "hiragana_mode",
    "katakana_mode",
    "half_katakana_mode",
#    "cancel_pseudo_ascii_mode_key",
    "circle_typing_method",
    "circle_dict_method",

    "insert_space",
    "insert_alternate_space",
    "insert_half_space",
    "insert_wide_space",
    "backspace",
    "delete",
    "commit",
    "convert",
    "predict",
    "cancel",
    "cancel_all",
    "reconvert",
#    "do_nothing",

    "select_first_candidate",
    "select_last_candidate",
    "select_next_candidate",
    "select_prev_candidate",
    "candidates_page_up",
    "candidates_page_down",

    "move_caret_first",
    "move_caret_last",
    "move_caret_forward",
    "move_caret_backward",

    "select_first_segment",
    "select_last_segment",
    "select_next_segment",
    "select_prev_segment",
    "shrink_segment",
    "expand_segment",
    "commit_first_segment",
    "commit_selected_segment",

    "select_candidates_1",
    "select_candidates_2",
    "select_candidates_3",
    "select_candidates_4",
    "select_candidates_5",
    "select_candidates_6",
    "select_candidates_7",
    "select_candidates_8",
    "select_candidates_9",
    "select_candidates_0",

    "convert_to_char_type_forward",
    "convert_to_char_type_backward",
    "convert_to_hiragana",
    "convert_to_katakana",
    "convert_to_half",
    "convert_to_half_katakana",
    "convert_to_wide_latin",
    "convert_to_latin",

    "dict_admin",
    "add_word",

    "start_setup",
]

_config = {
    'common': {
        'input_mode': 0,
        'typing_method': 0,
        'conversion_segment_mode': 0,

        'period_style': 0,
        'symbol_style': 1,
        'ten_key_mode': 1,
        'behavior_on_focus_out': 0,
        'behavior_on_period': 0,

        'page_size': 10,
        'half_width_symbol': False,
        'half_width_number': False,
        'half_width_space': False,

        'shortcut_type': 'default',

        'dict_admin_command': ['/usr/bin/kasumi', 'kasumi'],
        'add_word_command': ['/usr/bin/kasumi', 'kasumi', '-a'],
        'dict_config_icon': '/usr/share/pixmaps/kasumi.png',
    },

    'thumb': {
        'keyboard_layout_mode': True,
        'keyboard_layout': 0,
        'fmv_extension': 2,
        'handakuten': False,
        'rs': 'Henkan',
        'ls': 'Muhenkan',
        't1': 100,
        't2': 75,
    },

    'dict': {
        'anthy_zipcode': ['/usr/share/anthy/zipcode.t'],
        'ibus_symbol': ['/usr/share/ibus-anthy/dicts/symbol.t'],
        'files': [
            '/usr/share/anthy/zipcode.t',
            '/usr/share/ibus-anthy/dicts/symbol.t',
        ],
    },

    'dict/file/default': {
        'embed': False,
        'single': True,
        'icon': None,
        'short_label': None,
        'long_label': None,
        'preview_lines': 30,
        'reverse': False,
        'is_system': False,
        'encoding': 'utf-8',
    },

    'dict/file/embedded': {
        'embed': True,
        'single': True,
        'icon': None,
        'short_label': '般',
        'long_label': N_("General"),
        'preview_lines': 0,
        'reverse': False,
        'is_system': True,
    },

    'dict/file/anthy_zipcode': {
        'embed': False,
        'single': True,
        'icon': None,
        'short_label': '〒',
        'long_label': N_("Zip Code Conversion"),
        'preview_lines': 30,
        'reverse': True,
        'is_system': True,
        'encoding': 'euc_jp',
    },

    'dict/file/ibus_symbol': {
        'embed': True,
        'single': False,
        'icon': None,
        'short_label': '記',
        'long_label': N_("Symbol"),
        'preview_lines': -1,
        'reverse': False,
        'is_system': True,
    },
}

_shortcut_default = {
    'on_off': ['Ctrl+J'],
    'circle_input_mode': ['Ctrl+comma', 'Ctrl+less'],
    'circle_kana_mode': ['Ctrl+period', 'Ctrl+greater', 'Hiragana_Katakana'],
#    'cancel_pseudo_ascii_mode_key': ['Escape'],
    'circle_typing_method': ['Alt+Romaji', 'Ctrl+slash'],
    'circle_dict_method': ['Alt+Henkan'],

    'insert_space': ['space'],
    'insert_alternate_space': ['Shift+space'],
    'backspace': ['BackSpace', 'Ctrl+H'],
    'delete': ['Delete', 'Ctrl+D'],
    'commit': ['Return', 'KP_Enter', 'Ctrl+J', 'Ctrl+M'],
    'convert': ['space', 'KP_Space', 'Henkan'],
    'predict': ['Tab', 'ISO_Left_Tab'],
    'cancel': ['Escape', 'Ctrl+G'],
    'reconvert': ['Shift+Henkan'],

    'move_caret_first': ['Ctrl+A', 'Home'],
    'move_caret_last': ['Ctrl+E', 'End'],
    'move_caret_forward': ['Right', 'Ctrl+F'],
    'move_caret_backward': ['Left', 'Ctrl+B'],

    'select_first_segment': ['Ctrl+A', 'Home'],
    'select_last_segment': ['Ctrl+E', 'End'],
    'select_next_segment': ['Right', 'Ctrl+F'],
    'select_prev_segment': ['Left', 'Ctrl+B'],
    'shrink_segment': ['Shift+Left', 'Ctrl+I'],
    'expand_segment': ['Shift+Right', 'Ctrl+O'],
    'commit_first_segment': ['Shift+Down'],
    'commit_selected_segment': ['Ctrl+Down'],

    'select_first_candidate': ['Home'],
    'select_last_candidate': ['End'],
    'select_next_candidate': ['space', 'KP_Space', 'Tab', 'ISO_Left_Tab', 'Henkan', 'Down', 'KP_Add', 'Ctrl+N'],
    'select_prev_candidate': ['Shift+Tab', 'Shift+ISO_Left_Tab', 'Up', 'KP_Subtract', 'Ctrl+P'],
    'candidates_page_up': ['Page_Up'],
    'candidates_page_down': ['Page_Down', 'KP_Tab'],

    'select_candidates_1': ['1'],
    'select_candidates_2': ['2'],
    'select_candidates_3': ['3'],
    'select_candidates_4': ['4'],
    'select_candidates_5': ['5'],
    'select_candidates_6': ['6'],
    'select_candidates_7': ['7'],
    'select_candidates_8': ['8'],
    'select_candidates_9': ['9'],
    'select_candidates_0': ['0'],

    'convert_to_char_type_forward': ['Muhenkan'],
    'convert_to_hiragana': ['F6'],
    'convert_to_katakana': ['F7'],
    'convert_to_half': ['F8'],
    'convert_to_half_katakana': ['Shift+F8'],
    'convert_to_wide_latin': ['F9'],
    'convert_to_latin': ['F10'],

    'dict_admin': ['F11'],
    'add_word': ['F12'],
}

_config['shortcut/default'] = dict.fromkeys(_cmd_keys, [])
_config['shortcut/default'].update(_shortcut_default)

_shortcut_atok = {
    'on_off': ['Henkan', 'Eisu_toggle', 'Zenkaku_Hankaku'],
    'circle_input_mode': ['F10'],
    'hiragana_mode': ['Hiragana_Katakana'],
    'katakana_mode': ['Shift+Hiragana_Katakana'],
    'circle_typing_method': ['Romaji', 'Alt+Romaji'],
    'circle_dict_method': ['Alt+Henkan'],
    'convert': ['space', 'Henkan', 'Shift+space', 'Shift+Henkan'],
    'predict': ['Tab'],
    'cancel': ['Escape', 'BackSpace', 'Ctrl+H', 'Ctrl+bracketleft'],
    'commit': ['Return', 'Ctrl+M'],
    'reconvert': ['Shift+Henkan'],

    'insert_space': ['space'],
    'insert_alternate_space': ['Shift+space'],
    'backspace': ['BackSpace', 'Ctrl+H'],
    'delete': ['Delete', 'Ctrl+G'],

    'move_caret_backward': ['Left', 'Ctrl+K'],
    'move_caret_forward': ['Right', 'Ctrl+L'],
    'move_caret_first': ['Ctrl+Left'],
    'move_caret_last': ['Ctrl+Right'],

    'select_prev_segment': ['Shift+Left'],
    'select_next_segment': ['Shift+Right'],
    'select_first_segment': ['Ctrl+Left'],
    'select_last_segment': ['Ctrl+Right'],
    'expand_segment': ['Right', 'Ctrl+L'],
    'shrink_segment': ['Left', 'Ctrl+K'],
    'commit_selected_segment': ['Down'],

    'candidates_page_up': ['Shift+Henkan', 'Page_Up'],
    'candidates_page_down': ['Henkan', 'Page_Down'],
    'select_next_candidate': ['space', 'Tab', 'Henkan', 'Shift+space', 'Shift+Henkan'],
    'select_prev_candidate': ['Up'],

    'select_candidates_1': ['1'],
    'select_candidates_2': ['2'],
    'select_candidates_3': ['3'],
    'select_candidates_4': ['4'],
    'select_candidates_5': ['5'],
    'select_candidates_6': ['6'],
    'select_candidates_7': ['7'],
    'select_candidates_8': ['8'],
    'select_candidates_9': ['9'],
    'select_candidates_0': ['0'],

    'convert_to_hiragana': ['F6', 'Ctrl+U'],
    'convert_to_katakana': ['F7', 'Ctrl+I'],
    'convert_to_half': ['F8', 'Ctrl+O'],
    'convert_to_half_katakana': ['Shift+F8'],
    'convert_to_wide_latin': ['F9', 'Ctrl+P'],
    'convert_to_latin': ['F10', 'Ctrl+at'],

    'add_word': ['Ctrl+F7'],
}

_config['shortcut/atok'] = dict.fromkeys(_cmd_keys, [])
_config['shortcut/atok'].update(_shortcut_atok)

_shortcut_wnn = {
    'on_off': ['Shift+space'],
    'convert': ['space'],
    'predict': ['Ctrl+Q'],
    'cancel': ['Escape', 'Ctrl+G', 'Alt+Down', 'Muhenkan'],
    'commit': ['Ctrl+L', 'Ctrl+M', 'Ctrl+J', 'Return'],
    'insert_space': ['space'],
    'backspace': ['Ctrl+H', 'BackSpace'],
    'delete': ['Ctrl+D', 'Delete'],
    'circle_dict_method': ['Alt+Henkan'],

    'move_caret_backward': ['Ctrl+B', 'Left'],
    'move_caret_forward': ['Ctrl+F', 'Right'],
    'move_caret_first': ['Ctrl+A', 'Alt+Left'],
    'move_caret_last': ['Ctrl+E', 'Alt+Right'],

    'select_prev_segment': ['Ctrl+B', 'Left'],
    'select_next_segment': ['Ctrl+F', 'Right'],
    'select_first_segment': ['Ctrl+A', 'Alt+Left'],
    'select_last_segment': ['Ctrl+E', 'Alt+Right'],
    'expand_segment': ['Ctrl+O', 'F14'],
    'shrink_segment': ['Ctrl+I', 'F13'],

    'candidates_page_up': ['Tab'],
    'candidates_page_down': ['Shift+Tab'],
    'select_next_candidate': ['space', 'Ctrl+Q', 'Ctrl+P', 'Down'],
    'select_prev_candidate': ['Ctrl+N', 'Up'],

    'select_candidates_1': ['1'],
    'select_candidates_2': ['2'],
    'select_candidates_3': ['3'],
    'select_candidates_4': ['4'],
    'select_candidates_5': ['5'],
    'select_candidates_6': ['6'],
    'select_candidates_7': ['7'],
    'select_candidates_8': ['8'],
    'select_candidates_9': ['9'],
    'select_candidates_0': ['0'],

    'convert_to_hiragana': ['F6'],
    'convert_to_katakana': ['F7'],
    'convert_to_half': ['F8'],
    'convert_to_wide_latin': ['F9'],
    'convert_to_latin': ['F10'],
}

_config['shortcut/wnn'] = dict.fromkeys(_cmd_keys, [])
_config['shortcut/wnn'].update(_shortcut_wnn)

