#!/usr/bin/python

from gtk import *
import signal

class CheckList (CList):
    """A class (derived from CList) that provides a list of
    checkbox / text string pairs"""
    CHECK_SIZE = 13

    def __init__ (self):
        CList.__init__ (self, 2)
        
        self.set_column_auto_resize (0, 1)    
        self.set_column_auto_resize (1, 1)
        self.column_titles_passive ()
            
        self.connect ("realize", self._realize_cb)
        self.connect ("button_press_event", self._button_press_cb)
        self.connect ("key_press_event", self._key_press_cb)
        self.connect ("state_changed", self._state_changed_cb)

        self.off_pixmap = None
        self.on_pixmap = None
        self.off_insensitive_pixmap = None
        self.on_insensitive_pixmap = None

        self.toggled_func = None

        self.n_rows = 0

    def append_row (self, text, init_value, row_data=None):
        """Add a row to the list.
        text: text to display in the row
        init_value: initial state of the indicator
        row_data: data to pass to the toggled_func callback"""
        
        row = self.append (["", text])
        self.set_row_data (row, (not not init_value, row_data))
        self.n_rows = self.n_rows + 1

        self._update_row (row)

        return row

    def clear (self):
        "Remove all rows"
        CList.clear(self)
        self.n_rows = 0

    def set_toggled_func (self, func):
        """Set a function to be called when the value of a row is toggled.
        The  function will be called with two arguments, the new state
        of the indicator (boolean) and the row_data for the row."""
        self.toggled_func = func

    def row_set_state (self, row, state):
        state = not not state
        (val, row_data) = self.get_row_data(row)
        if val == state:
            return
        self.set_row_data(row, (state, row_data))
        
        self._update_row (row)
        
        if self.toggled_func != None:
            self.toggled_func(state, row_data)

    def row_get_state (self, row):
        (val, row_data) = self.get_row_data(row)
        return val

    def initialize_from_list (self, list):
        count = 0
        for i in xrange (self.rows):
            if count < len (list) and self.get_text (i, 1) == list[count]:
                self.row_set_state (i, True)
                count = count + 1
            else:
                self.row_set_state (i, False)

    def dump_to_list (self):
        retval = []
        for i in xrange (self.rows):
            if self.row_get_state (i):
                retval.append (self.get_text (i, 1))
        return retval

    def _update_row (self, row):
        if not (self.flags() & REALIZED):
            return
        (val, row_data) = self.get_row_data(row)

        if (self.flags() & SENSITIVE) and (self.flags() & PARENT_SENSITIVE):
            if val:
                self.set_pixmap(row,0,self.on_pixmap,self.mask)
            else:
                self.set_pixmap(row,0,self.off_pixmap,self.mask)
        else:
            if val:
                self.set_pixmap(row,0,self.on_insensitive_pixmap,self.mask)
            else:
                self.set_pixmap(row,0,self.off_insensitive_pixmap,self.mask)

    def _color_pixmaps(self):
        style = self.get_style()
        base_gc = self.on_pixmap.new_gc(foreground = style.base[STATE_NORMAL])
        text_gc = self.on_pixmap.new_gc(foreground = style.text[STATE_NORMAL])
        
        self.mask = create_pixmap(None,CheckList.CHECK_SIZE,CheckList.CHECK_SIZE,1)
        # HACK - we really want to just use a color with a pixel value of 1
        mask_gc = self.mask.new_gc (foreground = self.get_style().white)
        self.mask.draw_rectangle(mask_gc,1,0,0,CheckList.CHECK_SIZE,CheckList.CHECK_SIZE)

        self.on_pixmap.draw_rectangle(base_gc,1,0,0,CheckList.CHECK_SIZE,CheckList.CHECK_SIZE)
        self.on_pixmap.draw_rectangle(text_gc,0,0,0,CheckList.CHECK_SIZE-1,CheckList.CHECK_SIZE-1)
        self.on_pixmap.draw_line(text_gc,2, CheckList.CHECK_SIZE/2,CheckList.CHECK_SIZE/3,CheckList.CHECK_SIZE-5)
        self.on_pixmap.draw_line(text_gc,2, CheckList.CHECK_SIZE/2+1,CheckList.CHECK_SIZE/3,CheckList.CHECK_SIZE-4)
        self.on_pixmap.draw_line(text_gc,CheckList.CHECK_SIZE/3, CheckList.CHECK_SIZE-5, CheckList.CHECK_SIZE-3, 3)
        self.on_pixmap.draw_line(text_gc,CheckList.CHECK_SIZE/3, CheckList.CHECK_SIZE-4, CheckList.CHECK_SIZE-3, 2)
        
        self.off_pixmap.draw_rectangle(base_gc,1,0,0,CheckList.CHECK_SIZE,CheckList.CHECK_SIZE)
        self.off_pixmap.draw_rectangle(text_gc,0,0,0,CheckList.CHECK_SIZE-1,CheckList.CHECK_SIZE-1)

        text_gc = self.on_pixmap.new_gc(foreground = style.text[STATE_INSENSITIVE])

        self.on_insensitive_pixmap.draw_rectangle(base_gc,1,0,0,CheckList.CHECK_SIZE,CheckList.CHECK_SIZE)
        self.on_insensitive_pixmap.draw_rectangle(text_gc,0,0,0,CheckList.CHECK_SIZE-1,CheckList.CHECK_SIZE-1)
        self.on_insensitive_pixmap.draw_line(text_gc,2, CheckList.CHECK_SIZE/2,CheckList.CHECK_SIZE/3,CheckList.CHECK_SIZE-5)
        self.on_insensitive_pixmap.draw_line(text_gc,2, CheckList.CHECK_SIZE/2+1,CheckList.CHECK_SIZE/3,CheckList.CHECK_SIZE-4)
        self.on_insensitive_pixmap.draw_line(text_gc,CheckList.CHECK_SIZE/3, CheckList.CHECK_SIZE-5, CheckList.CHECK_SIZE-3, 3)
        self.on_insensitive_pixmap.draw_line(text_gc,CheckList.CHECK_SIZE/3, CheckList.CHECK_SIZE-4, CheckList.CHECK_SIZE-3, 2)
        
        self.off_insensitive_pixmap.draw_rectangle(base_gc,1,0,0,CheckList.CHECK_SIZE,CheckList.CHECK_SIZE)
        self.off_insensitive_pixmap.draw_rectangle(text_gc,0,0,0,CheckList.CHECK_SIZE-1,CheckList.CHECK_SIZE-1)

    def _realize_cb (self, clist):
        if self.get_parent_window() == None:
            return

        self.on_pixmap = create_pixmap(self.get_parent_window(), CheckList.CHECK_SIZE,CheckList.CHECK_SIZE)
        self.off_pixmap = create_pixmap(self.get_parent_window(), CheckList.CHECK_SIZE,CheckList.CHECK_SIZE)
        self.on_insensitive_pixmap = create_pixmap(self.get_parent_window(), CheckList.CHECK_SIZE,CheckList.CHECK_SIZE)
        self.off_insensitive_pixmap = create_pixmap(self.get_parent_window(), CheckList.CHECK_SIZE,CheckList.CHECK_SIZE)

        # We can't connect this callback before because of a bug in PyGtk where it doesn't
        # like style_set to be called with a NULL old_style
        self.connect ("style_set", lambda self, old_style: self._color_pixmaps)
        self._color_pixmaps()

        for i in range (self.n_rows):
            self._update_row (i)

    def _state_changed_cb (self, clist, old_state):
        self._realize_cb(self)
        if not (self.flags() & REALIZED):
            return

        for i in range (self.n_rows):
            self._update_row (i)

    def _toggle_row (self, row):
        self._realize_cb(self)
        (val, row_data) = self.get_row_data(row)
        val = not val
        self.set_row_data(row, (val, row_data))
        
        self._update_row (row)
        
        if self.toggled_func != None:
            self.toggled_func(val, row_data)

    def _key_press_cb (self, clist, event):
        self._realize_cb(self)
        if event.keyval == ord(" ") and self.focus_row != -1:
            self._toggle_row (self.focus_row)
            self.emit_stop_by_name ("key_press_event")
            return 1

        return 0
            
    def _button_press_cb (self, clist, event):
        self._realize_cb(self)
        info  = self.get_selection_info (event.x, event.y)
        if info != None:
            self._toggle_row (info[0])
            self.emit_stop_by_name ("button_press_event")
            return 1

        return 0

        
        

# test program

def cbox_callback (cbox, clist):
    clist.set_sensitive (cbox.get_active ())

if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = Window ()
    vbox = VBox (False, 8)
    cbox = CheckButton ("Set sensitive")
    sample_data = [ "foo", "bar", "baz", "bop" ]
    clist = CheckList ()
    cbox.connect ("toggled", cbox_callback, clist)
    cbox.set_active (True)
    init_val = True
    for i in sample_data:
        clist.append_row (i, init_val)
        init_val = not init_val
    vbox.pack_start (clist)
    vbox.pack_start (cbox, False, False, 0)
    window.add (vbox)
    window.show_all ()

    mainloop ()
