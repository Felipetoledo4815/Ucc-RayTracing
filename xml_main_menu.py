#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

PROG_NAME = "UccPOV"
VERSION = PROG_NAME + " v0.1beta"

class Main_menu1(Gtk.MenuBar):
    def __init__(self, parent):
        super(Main_menu1, self).__init__()
        self.main_menu = {}
        self.parent = parent

        for key in ["Archivo", "Editar", "Herramientas", "Ayuda"]:
            item = Gtk.MenuItem(key)
            self.main_menu[key] = Gtk.Menu()
            item.set_submenu(self.main_menu[key])
            self.add(item)

        self.add_items_to("Archivo", (("Salir", lambda x: Gtk.main_quit()), ))
        self.add_items_to("Ayuda", (("Acerca", self.on_about_activated), ))

    def add_items_to(self, main_item, items):
        for item, handler in items:
            if item == None:
                it = Gtk.SeparatorMenuItem()
            else:
                it = Gtk.ImageMenuItem(item)
                it.connect("activate", handler)
            self.main_menu[main_item].insert(it, 0)

    def on_about_activated(self, menuitem):
        pxb = GdkPixbuf.Pixbuf.new_from_file("logo.png")
        dlg = Gtk.AboutDialog(version = VERSION,program_name = PROG_NAME,
                              license_type = Gtk.License.GPL_3_0,
                              logo = pxb)
        dlg.set_transient_for(self.parent)
        dlg.run()
        dlg.destroy()

