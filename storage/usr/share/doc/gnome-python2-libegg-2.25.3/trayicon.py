#! /usr/bin/python
import pygtk
pygtk.require("2.0")
import gtk
import egg.trayicon
t = egg.trayicon.TrayIcon("MyFirstTrayIcon")
t.add(gtk.Label("Hello"))
t.show_all()
gtk.main()
