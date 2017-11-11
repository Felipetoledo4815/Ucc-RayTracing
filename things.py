#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  things.py
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


from rt_math import *
from camera import Hit, Hit_list


class Thing():
    def __init__(self, props):
        self.props = props
        self.ambient = Vec3(props['ambient'])
        self.diffuse = Vec3(props['diffuse'])
        self.reflection = Vec3(props['reflection'])


    def intersection(self, ray):
        pass



class Plane(Thing):
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



class Sphere(Thing):
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


class Cone(Thing):
    def __init__(self, props):
        super(Cone, self).__init__(props)
        self.center = props['location']
        self.radius = float(props['radius'])
        self.height = float(props['height'])
        self.angle = np.arctan(self.radius/self.height)

    def intersection(self, ray):
        c = Vec3(self.center).add(Vec3(0,self.height,0))
        v = Vec3("0 -1 0") #Es (0,-1,0) porque el verser v en las fórmulas va hacia abajo

        a = ((ray.direct.dot(v))**2) - np.cos(self.angle)**2

        b = 2 * ((ray.direct.dot(v) * (ray.orig.subtract(c).dot(v))) - ((ray.direct.dot(ray.orig.subtract(c)) * np.cos(self.angle) ** 2)))

        ce = (ray.orig.subtract(c).dot(v)) ** 2 - ((ray.orig.subtract(c).dot(ray.orig.subtract(c))) * np.cos(self.angle) ** 2)

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
                n = ray.direct.scale(d).subtract(Vec3(self.center)) #Sacar NORMAL del Cono
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



class Triangle(Thing):
    def __init__(self, props):
        super(Triangle, self).__init__()
        self.props = props


    def intersection(self, ray):
        pass



class Cylinder(Thing):
    def __init__(self, props):
        super(Cylinder, self).__init__()
        self.props = props


    def intersection(self, ray):
        pass



class Box(Thing):
    def __init__(self, props):
        super(Box, self).__init__()
        self.props = props


    def intersection(self, ray):
        pass


obj_dict = {
            'sphere'  : Sphere,
            'plane'   : Plane,
            'box'     : Box,
            'triangle': Triangle,
            'cylinder': Cylinder,
            'cone': Cone}


def main(args):

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
