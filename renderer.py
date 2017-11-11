
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  renderer.py
#
#  Copyright 2017 John Coppens <john@jcoppens.com>
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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib
from viewer import Viewer
from rt_math import *
from lights import *
from things import *
from cameras import *
import pdb



class Renderer():
    def __init__(self, scene, cam_props):
        self.scene = scene
        self.lights = []
        self.objects = []
        self.cam = Camera(scene.toplevel, cam_props, self.objects, self.lights)

        # Crear instancias de objetos y luces y crear un indice
        for row in self.scene.store:
            if row[0] == "objects":
                for subrow in row.iterchildren():
                    el_name = subrow[1]['element']
                    if el_name in obj_dict:
                        self.objects.append(obj_dict[el_name](subrow[1]))
                    else:
                        print("Elemento no reconocido ({:s}). "
                              "Falta agregar en renderer.py?".format(el_name))

            elif row[0] == "lights":
                for subrow in row.iterchildren():
                    el_name = subrow[1]['element']
                    if el_name in light_dict:
                        self.lights.append(light_dict[el_name](subrow[1]))
                    else:
                        print("Elemento no reconocido ({:s}). "
                              "Falta agregar en renderer.py?".format(el_name))

        self.cam.render()

CAM_PROPS = {
            "location": "0 0 0",
            "look_at": "0 0 0",
            "fov_y": "45",
            "width": "16",
            "height": "12",
            "begrow": "0",
            "endrow": "11",
            "begcol": "0",
            "endcol": "15"}

class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.connect('destroy', lambda x: Gtk.main_quit())
        self.set_size_request(400, 400)

        self.viewer = Viewer(self)
        cam = Camera(self, CAM_PROPS, [], [])

        cam.render()

        self.add(self.viewer)
        self.show_all()

    def run(self):
        Gtk.main()


def main(args):
    mw = MainWindow()
    mw.run()
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
