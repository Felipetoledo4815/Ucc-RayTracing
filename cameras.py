#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  camera.py
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
from rt_math import *


class Hit():
    """ Cada impacto registra 3 datos:
            spot        float   distancia del origen del rayo
            normal      Vec3    normal en el punto de impacto
            obj         object  referencia al objeto impactado
    """
    def __init__(self, t, normal, obj):
        self.t = t
        self.normal = normal
        self.obj = obj



class Hit_list():
    """ Lista de impactos """
    def __init__(self):
        self.hits = []


    def __str__(self):
        s = ""
        for hit in self.hits:
            s += "{:12.6f} {:s}\n".format(hit.t, str(hit.normal))

        return s


    def nearest(self):
        """ Busca al impacto mas cercano """
        dist = 1e99
        if len(self.hits) == 0:
            return None

        for hit in self.hits:
            if hit.t < dist:
                nearest_hit = hit
                dist = hit.t

        return nearest_hit



    def append(self, new_hits):
        """ Agrega un impacto a la lista """
        self.hits += new_hits



class Picture():
    def __init__(self, w, h):
        self.pixels = bytearray(w * h * 3)
        self.w = w
        self.h = h
        self.rowstride = w * 3


    def set_pixel(self, x, y, rgb):
        pixel_offset = (self.h - 1 - y) * self.rowstride + x * 3
        self.pixels[pixel_offset + 0] = rgb[0]
        self.pixels[pixel_offset + 1] = rgb[1]
        self.pixels[pixel_offset + 2] = rgb[2]


    def make_pixbuf(self):
        return GdkPixbuf.Pixbuf.new_from_bytes(
                    GLib.Bytes(self.pixels),
                    GdkPixbuf.Colorspace.RGB,
                    False, 8, self.w, self.h, self.rowstride)



class Camera():
    def __init__(self, toplevel, props, objects, lights):
        self.props = props
        self.toplevel = toplevel

        self.objects = objects
        self.lights = lights

        self.width = int(self.props["width"])
        self.height = int(self.props["height"])
        self.begcol = int(self.props["begcol"])
        self.endcol = int(self.props["endcol"])
        self.begrow = int(self.props["begrow"])
        self.endrow = int(self.props["endrow"])
        self.aspect = self.height/self.width
        self.fov_y = float(self.props["fov_y"])

        self.pixels = Picture(self.width, self.height)


    def render(self):
        cte_x = self.width/2 - 0.5
        cte_y = self.height/2 - 0.5
        scale = 2/self.height
        for y in range(self.begrow, self.endrow+1):
            for x in range(self.begcol, self.endcol+1):
                ray = Ray(Vec3(0, 0, 0),
                          Vec3((x - cte_x) * scale,
                               (y - cte_y) * scale,
                               1).normalize())

                self.pixels.set_pixel(x, y, self.tracer(ray))

        #~ pdb.set_trace()
        self.toplevel.viewer.update(self.pixels.make_pixbuf())


    def tracer(self, ray):
        """ Tracer
                - sigue el ray <ray> y determina impactos
                - determina el impacto mas cercano
                - devuelve el color correspondiente como (R, G, B)
        """
        hits = Hit_list()

        for obj in self.objects:
            if obj.props["reference"] != "planeCAMARA":
                new_hits = obj.intersection(ray)
                hits.append(new_hits)

        nearest_hit = hits.nearest()

        if nearest_hit == None:
            return (0, 0, 0)
        else:
            #~ pdb.set_trace()
            amb_col = nearest_hit.obj.ambient

            # Calculo rayo que va hacia la luz desde el punto de impacto. El rayo se va a llamar "ShadowRay"
            ShadowRay = Ray(ray.direct.scale(nearest_hit.t),
                            Vec3(self.lights[0].props["location"]).subtract(ray.direct.scale(nearest_hit.t)).normalize())

            Epsilon = Vec3(ShadowRay.direct.x * 0.01, ShadowRay.direct.y * 0.01, ShadowRay.direct.z * 0.01)
            OriginPlusEpsilon = Vec3(ShadowRay.orig.x + Epsilon.x, ShadowRay.orig.y + Epsilon.y, ShadowRay.orig.z +Epsilon.z)
            ShadowRay.orig = OriginPlusEpsilon

            if self.shadow(ShadowRay):                 # Hay sombra
                return Vec3(amb_col).as_RGB()
            else:                                      # No hay sombra
                # Calculo Luz Difusa
                cos_ang = abs(nearest_hit.normal.dot(ray.direct))
                dif_col = nearest_hit.obj.diffuse.scale(cos_ang)
                col = Vec3(amb_col).add(dif_col)

                # Calculo Luz Phong
                R = nearest_hit.normal.scale(2 * (ShadowRay.direct.dot(nearest_hit.normal))).subtract(ShadowRay.direct)
                phong_col = nearest_hit.obj.reflection.scale(R.dot(ray.direct) ** 160)
                # .mult(Vec3(self.lights[0].props["color"]))
                col = col.add(phong_col)

                return col.as_RGB()


    def shadow(self, ray):
        hits2 = Hit_list()

        for obj in self.objects:
            new_hits = obj.intersection(ray)
            hits2.append(new_hits)


        nearest_hit = hits2.nearest()

        if nearest_hit == None:
            return False
        else:
            if nearest_hit.obj.props["reference"] == "planeCAMARA":
                return False
            else:
                return True


def main(args):

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
