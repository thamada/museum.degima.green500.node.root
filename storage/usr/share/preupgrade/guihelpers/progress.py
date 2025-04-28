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

# (C) 2007 Tim Lauridsen <timlau@fedoraproject.org>

import gtk
import gtk.glade
import gobject
import sys

class ProgressStepsBase:
    '''
    Base class for implementing a checklist progress
    It contains a number of steps with the following info for each step.
        * Step Completion state (True / False)
        * Step Description Text
        * Step Subfraction of the whole process (0.0 -> 1.0)
        * Step Complete Fraction of the step (0.0 -> 1.0)

    Adding steps:

       obj.add_step(description, subfraction)

    Bumping to the next step:

       obj.bump()

    Setting step progress fraction & details text:

       obj.progress(fraction, details text)

    Reset.
        obj.clear()

    The class has to be parent to a child class there implement the following methods

    def _populate_view(self, data):
    Update the checklist view visuals

    def _update_progressbar(self, frac, details):
    Update the total process progressbar.

    '''
    def __init__(self):
        self._steps = {}                # Step Data
        self._num_steps = 0             # Number of steps
        self._cur_step = 1              # Current step
        self._start_progress = 0.0      # Start Total Progress for current step
        self._next_progress = 0.0       # Start Total Progress for next step
        self._cur_progress = 0.0        # Current Total Progress Fraction
        self._complete = False          # All Steps Completed
        self._last_frac = 0.0           # Last Fraction value for current step

    def add_step(self, text, frac):
        '''
        Add a new step
        @param text: Step Description
        @param frac: The steps part of the total fraction for the whole process
        '''
        self._num_steps += 1
        self._steps[self._num_steps] = (False, text, frac, 0)
        self._refresh_view()
        if self._num_steps == 1:
            self._next_progress = frac


    def get_step(self, no):
        '''
        Get step
        @param no: Step number to get
        @return: (state, text, total fraction, current sub fraction)
        '''
        return self._steps[no]

    def get_current(self):
        '''
        Get current step
        @return: (state, text, total fraction, current sub fraction)
        '''

        return self.get_step(self._cur_step)

    def _update_current_progress(self, frac):
        '''
        Update subfraction for current step
        @param frac: subfraction for current step
        '''

        state, text, totalfrac, progress = self.get_current()
        self._update_step(self._cur_step, state, frac)
        self._cur_progress = self._start_progress + (totalfrac*frac)

    def _update_step(self, no, state, frac):
        '''
        Update state & subfraction for a selected step
        @param no: Step to work on
        @param state: Step completion state (True / False)
        @param frac: subfraction for current step
        '''
        s, text, tf, p = self._steps[no]
        self._steps[no] = (state, text, tf, frac)

    def reset_step(self, no):
        '''
        reset state & subfraction for a step
        @param no: Step to work on
        '''
        state, text, pct, progress = self._steps[no]
        self._steps[no] = (False, text, pct, 0)

    def reset_all_steps(self):
        '''
        reset state & subfraction for all steps
        '''
        for key in self._steps.keys():
            self.reset_step(key)

    def clear(self):
        '''
        clear all var initial conditions
        '''
        self._steps = {}
        self._num_steps = 0
        self._cur_step = 1
        self._start_progress = 0.0
        self._next_progress = 0.0
        self._cur_progress = 0.0
        self._complete = False
        self._last_frac = 0.0

    def _complete_step(self):
        '''
        Complete the current step (state = True, subfraction = 1.0 )
        '''
        self._update_step(self._cur_step, True, 1.0)
        if self._cur_step < self._num_steps:
            self._cur_step += 1
        else:
            self._complete = True
            self._update_progressbar(1.0, "Finish")
        self._refresh_view()

    def _refresh_view(self):
        '''
        Get data from steps and populate checklist view
        '''
        keys = self._steps.keys()
        keys.sort()
        data = []
        for key in keys:
            state, text, totalfrac, progress = self.get_step(key)
            if key == self._cur_step:
                data.append([state, text, True])
            else:
                data.append([state, text, False])

        self._populate_view(data)

    def bump(self):
        '''
        Complete the current step & and start on the next one
        '''
        self._complete_step()
        if not self._complete:
            state, text, frac, progress = self.get_current()
            self._start_progress = self._next_progress
            self._next_progress = self._start_progress + frac
            self._cur_progress = self._start_progress
            self._last_frac = 0.0
            self._update_progressbar(self._cur_progress, "")

    def progress(self, frac, details=""):
        '''
        Set the progress for current step
        @param frac: Progress fraction for current step (0.0 -> 1.0)
        @param details: Details Text (optional)
        '''
        if frac >= 0.0 and frac <= 1.0: # Just to be safe
            if frac >= self._last_frac + 0.005:
                self._update_current_progress(frac)
                self._update_progressbar(self._cur_progress, details)
                self._last_frac = frac

##################### Virtual Methods ##########################

    def _populate_view(self, data):
        '''
        Populate the checklist view
        Implement in a child class
        @param data: a list containing [state, text, active entry] elements.
        '''
        pass

    def _update_progressbar(self, frac, details):
        '''
        Update the progressbar and write details
        Implement in a child class
        @param frac: Progress fraction (0.0 -> 1.0)
        @param details: Details text
        '''
        pass

    def set_details(self, details):
        '''
        Set the details
        @param details: The details string
        '''
        pass

class ProgressStepsView(ProgressStepsBase):
    '''
    Implemtent the visuals for checklist progress dialog
    need the following gtk widgets
        gtk.TreeView     : to show the tasks and if they are completted.
        gtk.ProgressBar  : To show the total progress
        gtk.Label        : To show task details
    '''
    def __init__(self, treeview, pbar, details):
        '''
        @param treeview: gtk TreeView widget
        @param pbar: gtk ProgressBar widget
        @param details: gtk Label to write Task details
        '''
        ProgressStepsBase.__init__(self)
        self._view = treeview
        self._progressbar = pbar
        self._details = details
        self._model = self._setup_view()

    def _setup_view(self):
        '''
        Setup the TextView
        '''
        model = gtk.ListStore(gobject.TYPE_BOOLEAN,
                              gobject.TYPE_STRING )
        self._view.set_model(model)
        # Setup Step completted
        cell1 = gtk.CellRendererToggle()    # Selection
        column1 = gtk.TreeViewColumn("", cell1)
        column1.add_attribute(cell1, "active", 0)
        column1.set_sort_column_id(-1)
        self._view.append_column(column1)

        # Setup Step text colum
        self._create_text_column("", 1)
        self._view.set_reorderable(False)
        return model

    def _create_text_column( self, hdr, colno):
        '''
        Create a TextView Text Column
        @param hdr: Column Header Text
        @param colno: ListStore Column no. contain the data
        '''
        cell = gtk.CellRendererText()    # Size Column
        column = gtk.TreeViewColumn( hdr, cell, markup=colno )
        column.set_resizable( False )
        self._view.append_column( column )

    def _populate_view( self, data ):
        '''
        Populate the checklist view
        @param data: a list containing [state, text, active entry] elements.
        '''
        self._model.clear()
        for state, text, active in data:
            if active:
                self._model.append([state, "<b>%s</b>" % text])
            else:
                self._model.append([state, "%s" % text])


    def _update_progressbar(self, frac, details):
        '''
        Update the progressbar and write details
        @param frac: Progress fraction (0.0 -> 1.0)
        @param details: Details text
        '''
        self._progressbar.set_fraction(frac)
        pct = int(frac * 100)
        self._progressbar.set_text("%i %%" % pct)
        self._details.set_text(details)

    def pulse_progressbar(self):
        self._progressbar.pulse()

    def set_details(self, details):
        '''
        Set the details
        @param details: The details string
        '''
        self._details.set_text(details)


WIDGETS = {
'box'           : 'DPMain',
'eta'           : 'DP_fileETA',
'fileNo'        : 'DP_fileNo',
'fileName'      : 'DP_fileName',
'fileProgress'  : 'DP_progressSub',
'totalProgress' : 'DP_progressTotal',
'dnlImage'      : 'DP_dnlImage',
'iconBox'       : 'DP_iconBox',
'dnlButtons'    : 'DP_dnlButtons',
'stopButton'    : 'DP_stopDownload'
}

class DownloadProgress:

    def __init__(self, ui, widgets=WIDGETS, stop=True):
        self.ui = ui
        self.box            = self.ui.progressBox
        self.eta            = getattr(self.ui, widgets['eta'])
        self.fileNo         = getattr(self.ui, widgets['fileNo'])
        self.fileName       = getattr(self.ui, widgets['fileName'])
        self.fileProgress   = getattr(self.ui, widgets['fileProgress'])
        self.totalProgress  = getattr(self.ui, widgets['totalProgress'])
        self.dnlImage       = getattr(self.ui, widgets['dnlImage'])
        self.iconBox        = getattr(self.ui, widgets['iconBox'])
        self.dnlButtons     = getattr(self.ui, widgets['dnlButtons'])
        self.stopButton     = getattr(self.ui, widgets['stopButton'])
        if stop:
            self.stopButton.show()
            self.stopButton.connect('clicked', self.stop_pressed)
        else:
            self.stopButton.hide()

    def show(self):
        self.box.show()

    def hide(self):
        self.box.hide()

    def set_fileno(self, now, total):
        txt = "(%s/%s)" % (now, total)
        self.fileNo.set_text(txt)

    def show_fileno(self, show=True):
        if show:
            self.fileNo.show()
        else:
            self.fileNo.hide()

    def set_eta(self, eta):
        self.eta.set_text(eta)

    def show_eta(self, show=True):
        if show:
            self.eta.show()
        else:
            self.eta.hide()

    def set_filename(self, fn):
        self.fileName.set_text(fn)

    def set_file_progress(self, frac):
        self.fileProgress.set_fraction(frac)

    def pulse_file_progress(self):
        self.fileProgress.pulse()

    def set_total_progress(self, frac):
        self.totalProgress.set_fraction(frac)


    def stop_pressed(self, widget):
        pass

    def set_filename_only(self, state):
        if state:
            self.eta.hide()
            self.fileNo.hide()
        else:
            self.eta.show()
            self.fileNo.show()

    def set_download_mode(self, active=True):
        if active:
            self.set_filename_only(state=False)
            self.fileProgress.show()
        else:
            self.set_filename_only(state=True)
            self.fileProgress.hide()



class Progress:
    def __init__( self, ui, win, view):
        """
        win     : the window widget
        view    : the TreeView Widget
        pbar    : the progressbar widget
        details : the label widget

        """
        self.ui  = ui
        self.win = win
        self.dnlProgress = DownloadProgress(self.ui)
        self.download_mode(False)
        pbar = self.dnlProgress.totalProgress
        details = self.dnlProgress.fileName
        self.psteps = ProgressStepsView(view, pbar, details)
        self.hide()

    def show(self):
        self.win.show()

    def hide(self):
        self.win.hide()

    def add_steps(self, steps):
        for frac, text in steps:
            self.psteps.add_step(text, frac)
        doGtkEvents()

    def progress(self, frac, details=""):
        self.psteps.progress(frac, details)
        doGtkEvents()

    def download_mode(self, active):
        self.dnlProgress.set_download_mode(active)

    def set_filename(self, fn):
        self.dnlProgress.set_filename(fn)


    def set_fileno(self, now, total):
        self.dnlProgress.set_fileno(now, total)

    def set_file_progress(self, frac):
        self.dnlProgress.set_file_progress(frac)

    def pulse(self):
        self.psteps.pulse_progressbar()


    def bump(self):
        self.psteps.bump()

    def reset(self):
        self.psteps.reset_all_steps()

    def clear(self):
        self.psteps.clear()

    def details(self, details):
        self.psteps.set_details(details)
        doGtkEvents()

    def set_stop_handler(self, func):
        self.dnlProgress.stopButton.connect('clicked', func)



def doGtkEvents():
    while gtk.events_pending():      # process gtk events
        gtk.main_iteration()


if __name__ == '__main__':

    def quit(w=None, event=None ):
        win.hide()
        win.destroy()
        gtk.main_quit()
        sys.exit(0)

    steps = [(0.1, "Initialiasing the system"),
             (0.4, "Downloading the needed files"),
             (0.4, "Processing the files"),
             (0.1, "Cleanup the system")]

    xml = gtk.glade.XML( "ProgressSteps.glade", "Progress")
    win = xml.get_widget("Progress")
    win.connect( "destroy", quit )
    win.connect( "delete_event", quit )
    view = xml.get_widget( "ProgressSteps" )
    pbar = xml.get_widget( "ProgressBar" )
    details = xml.get_widget( "Details" )
    progress = Progress(win, view, pbar, details)
    progress.add_steps(steps)
    progress.show()

    import time
    for j in range(len(steps)):
        step, text = steps[j]
        for i in range(0, 101):
            frac = i/100.0
            progress.progress(frac, details="Sub Progress current task : %i %%" % i)
            while gtk.events_pending():      # process gtk events
                gtk.main_iteration()
            time.sleep(0.05)
        progress.bump()

        
