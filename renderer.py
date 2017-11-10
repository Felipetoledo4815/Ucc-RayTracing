
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

import pdb
from gi.repository import GdkPixbuf, GLib
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
            new_hits = obj.intersection(ray)
            hits.append(new_hits)

        nearest_hit = hits.nearest()

        if nearest_hit == None:
            return (0, 0, 0)
        else:
            return nearest_hit.obj.ambient.as_RGB()



class Light():
    def __init__(self, props):
        self.props = props



class Object():
    def __init__(self, props):
        self.props = props
        self.ambient = Vec3(props['ambient'])
        self.diffuse = Vec3(props['diffuse'])
        self.reflection = Vec3(props['reflection'])


    def intersection(self, ray):
        pass



class Plane(Object):
    def __init__(self, props):
        super(Plane, self).__init__(props)
        self.dist = float(props['distance'])
        self.normal = Vec3(props['normal'])


    def intersection(self, ray):
        #~ print(str(ray))
        #~ pdb.set_trace()
        ln = self.normal.dot(ray.direct)

        if (ln == 0):
            return []

        numerador = self.normal.scale(self.dist).subtract(ray.orig).dot(self.normal)
        t = numerador/ln

        return [] if t <= 0 else [Hit(t, self.normal, self)]



class Sphere(Object):
    def __init__(self, props):
        super(Sphere, self).__init__(props)
        self.center = props['location']
        self.radius = float(props['radius'])


    def intersection(self, ray):
        a = ray.direct.dot(ray.direct)    #El rayo ya está normalizado (vector unitario)

        aux = Vec3(ray.orig).subtract(Vec3(self.center))

        b = 2 * (ray.direct.dot(aux))

        c = ((Vec3(ray.orig).subtract(Vec3(self.center))).dot(Vec3(ray.orig).subtract(Vec3(self.center)))) - self.radius**2


        square_root = b**2 - 4*a*c

        if(square_root < 0):
            return []
        elif (square_root == 0):
            d = -b / (2*a)
            n = ray.direct.scale(d).subtract(Vec3(self.center)) #Resta entre vector unitario del rayo * distancia y vector centro de la esfera
            return [Hit(d, n, self)]   #Sacar normal en ese punto para mandarla por parámetro en HIT()
        else:
            d1 = (-b + np.sqrt(square_root)) / (2*a)
            d2 = (-b - np.sqrt(square_root)) / (2*a)
            if(d1<=0 and d2<=0):
                return []

            d = self.closest(d1, d2)
            n = ray.direct.scale(d).subtract(Vec3(self.center))
            return [Hit(d, n, self)]

    def closest(self, d1, d2):
        if(d1 <= 0):
            return d2
        elif(d2 <= 0):
            return d1
        elif (d1 <= d2):
            return d1
        else:
            return d2


class Triangle(Object):
    def __init__(self, props):
        super(Triangle, self).__init__()
        self.props = props

    def intersection(self, ray):
        pass



class Cone(Object):
    def __init__(self, props):
        super(Cone, self).__init__(props)
        self.center = props['location']
        self.radius = float(props['radius'])
        self.height = float(props['height'])
        self.angle = np.arctan(self.radius/self.height) #np.deg2rad(2 * np.arctan(self.radius/self.height))

    def intersection(self, ray):
        c = Vec3(self.center).add(Vec3(0,self.height,0))
        v = Vec3("0 -1 0") #Es (0,1,0) solo si esta vertical siempre sino es (0,self.height,0)

        a = ((ray.direct.dot(v))**2) - np.cos(self.angle)**2

        b = 2 * ((ray.direct.dot(v) * (ray.orig.subtract(c).dot(v))) - ((ray.direct.dot(ray.orig.subtract(c)) * np.cos(self.angle) ** 2)))

        ce = (ray.orig.subtract(c).dot(v)) ** 2 - ((ray.orig.subtract(c).dot(ray.orig.subtract(c))) * np.cos(self.angle) ** 2)

        # b = 2*((ray.direct.dot(v)*(c.cross(ray.orig).dot(v)))-(ray.direct.dot(c.cross(ray.orig))*np.cos(self.angle)**2))
        #ce = (c.cross(ray.orig).dot(v))**2 - c.cross(ray.orig).dot(c.cross(ray.orig)) * np.cos(self.angle)**2

        square_root = b**2 - 4*a*ce

        if(square_root < 0):
            return []
        elif (square_root == 0):
            d = -b / (2*a)
            aux = ray.direct.scale(d).subtract(c).dot(v)
            if(aux>0):
                n = ray.direct.scale(d).subtract(Vec3(self.center)) #Sacar NORMAL del Cono
                return [Hit(d, n, self)]
            else:
                return []
        else:
            d1 = (-b + np.sqrt(square_root)) / (2 * a)
            d2 = (-b - np.sqrt(square_root)) / (2 * a)
            if (d1 <= 0 and d2 <= 0):
                return []

            d = self.closest(d1, d2)
            aux = ray.direct.scale(d).subtract(c).dot(v)
            if(aux>0):
                n = ray.direct.scale(d).subtract(Vec3(self.center))
                return [Hit(d, n, self)]
            else:
                return []

    def closest(self, d1, d2):
        if(d1 <= 0):
            return d2
        elif(d2 <= 0):
            return d1
        elif (d1 <= d2):
            return d1
        else:
            return d2



class Cylinder(Object):
    def __init__(self, props):
        super(Cylinder, self).__init__()
        self.props = props


    def intersection(self, ray):
        pass



class Box(Object):
    def __init__(self, props):
        super(Box, self).__init__()
        self.props = props


    def intersection(self, ray):
        pass



class Renderer():
    def __init__(self, scene, cam_props):
        self.scene = scene
        self.lights = []
        self.objects = []
        self.cam = Camera(scene.toplevel, cam_props, self.objects, self.lights)
        obj_dict = {'sphere'  : Sphere,
                    'plane'   : Plane,
                    'box'     : Box,
                    'triangle': Triangle,
                    'cone': Cone,
                    'cylinder': Cylinder}

        for row in self.scene.store:
            if row[0] == "objects":
                for subrow in row.iterchildren():
                    el_name = subrow[1]['element']
                    if el_name in obj_dict:
                        self.objects.append(obj_dict[el_name](subrow[1]))
                    else:
                        print("Elemento no reconocido. Falta agregar en renderer.py?")

            elif row[0] == "lights":
                for subrow in row.iterchildren():
                    self.lights.append(Light(subrow[1]))

        self.cam.render()



def main(args):
    cam_props = {
                "location": "0 0 0",
                "look_at": "0 0 0",
                "fov_y": "45",
                "width": "16",
                "height": "12",
                "begrow": "0",
                "endrow": "11",
                "begcol": "0",
                "endcol": "15"}
    cam = Camera(cam_props)

    cam.render()
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
