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

import gtk.glade

class UI(gtk.glade.XML):
    """Base class for UIs loaded from glade."""

    def __init__(self, filename, rootname, domain=None):
        """Initialize a new instance.
        `filename' is the name of the .glade file containing the UI hierarchy.
        `rootname' is the name of the topmost widget to be loaded.
        `gladeDir' is the name of the directory, relative to the Python
        path, in which to search for `filename'."""
        if domain:
            gtk.glade.XML.__init__(self, filename, rootname, domain)
        else:
            gtk.glade.XML.__init__(self, filename, rootname)
        self.filename = filename
        self.root = self.get_widget(rootname)

    def __getattr__(self, name):
        """Look up an as-yet undefined attribute, assuming it's a widget."""
        result = self.get_widget(name)
        if result is None:
            raise AttributeError("Can't find widget %s in %s.\n" %
                                 (name, self.filename))

        # Cache the widget to speed up future lookups.  If multiple
        # widgets in a hierarchy have the same name, the lookup
        # behavior is non-deterministic just as for libglade.
        setattr(self, name, result)
        return result

class Controller:
    """Base class for all controllers of glade-derived UIs."""
    def __init__(self, ui):
        """Initialize a new instance.
        `ui' is the user interface to be controlled."""
        self.ui = ui
        self.ui.signal_autoconnect(self._getAllMethods())

    def _getAllMethods(self):
        """Get a dictionary of all methods in self's class hierarchy."""
        result = {}

        # Find all callable instance/class attributes.  This will miss
        # attributes which are "interpreted" via __getattr__.  By
        # convention such attributes should be listed in
        # self.__methods__.
        allAttrNames = self.__dict__.keys() + self._getAllClassAttributes()
        for name in allAttrNames:
            value = getattr(self, name)
            if callable(value):
                result[name] = value
        return result

    def _getAllClassAttributes(self):
        """Get a list of all attribute names in self's class hierarchy."""
        nameSet = {}
        for currClass in self._getAllClasses():
            nameSet.update(currClass.__dict__)
        result = nameSet.keys()
        return result

    def _getAllClasses(self):
        """Get all classes in self's heritage."""
        result = [self.__class__]
        i = 0
        while i < len(result):
            currClass = result[i]
            result.extend(list(currClass.__bases__))
            i = i + 1
        return result

def doGtkEvents():
    while gtk.events_pending():      # process gtk events
        gtk.main_iteration()

