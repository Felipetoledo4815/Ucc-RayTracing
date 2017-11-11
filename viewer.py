#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
##  viewer.py
#  
#  Copyright 2017 Unknown <root@hp425>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  


from gi.repository import Gtk


class Viewer(Gtk.Frame):
    def __init__(self, toplevel):
        super(Viewer, self).__init__(
                    label = "Imagen")
        self.toplevel = toplevel

        self.img = Gtk.Image()
        self.scroller = Gtk.ScrolledWindow(
                    margin = 4)
        self.scroller.add(self.img)

        self.add(self.scroller)


    def update(self, pixbuf):
        self.img.set_from_pixbuf(pixbuf)




class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.connect('destroy', lambda x: Gtk.main_quit())
        self.set_size_request(400, 300)
        
        viewer = Viewer(self)
        
        self.add(viewer)
        self.show_all()
        
    def run(self):
        Gtk.main()
        
        
def main():
    mw = MainWindow()
    mw.run()
    return 0

if __name__ == '__main__':
    main()

