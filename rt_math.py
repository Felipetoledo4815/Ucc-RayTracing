#!/usr/bin/env python3

import numpy as np

def d2r(d):
    return d*np.pi/180

def r2d(r):
    return r*180/np.pi


class Vec3():
    def __init__(self, x, y = 0, z = 0):
        if isinstance(x, str):
            v = x.split()
            self.x = float(v[0])
            self.y = float(v[1])
            self.z = float(v[2])
        elif isinstance(x, tuple):
            self.x, self.y, self.z = x
        elif isinstance(x, Vec3):
            self.x, self.y, self.z = x.x, x.y, x.z
        else:
            self.x, self.y, self.z = x, y, z

    def __str__(self):
        return "Vec3 ({:.6g}, {:.6g}, {:.6g})".format(self.x, self.y, self.z)

    def as_tuple(self):
        return (self.x, self.y, self.z)

    def as_RGB(self):
        """ Devuelve los componentes del Vec3, normalizando y limitando """
        return (min(int(self.x * 255), 255),
                min(int(self.y * 255), 255),
                min(int(self.z * 255), 255))

    def mag(self):
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        d = self.mag()
        self.x /= d
        self.y /= d
        self.z /= d
        return self

    def add(self, v3):
        return Vec3(self.x + v3.x,
                    self.y + v3.y,
                    self.z + v3.z)

    def mult(self, v3):
        return Vec3(self.x * v3.x,
                    self.y * v3.y,
                    self.z * v3.z)

    def subtract(self, v3):
        return Vec3(self.x - v3.x,
                    self.y - v3.y,
                    self.z - v3.z)

    def scale(self, scalar):
        return Vec3(self.x * scalar,
                    self.y * scalar,
                    self.z * scalar)

    def dot(self, v3):
        return self.x * v3.x + self.y * v3.y + self.z * v3.z

    def cross(self, v3):
        return Vec3(self.y * v3.z - self.z * v3.y,
                    self.z * v3.x - self.x * v3.z,
                    self.x * v3.y - self.y * v3.x)


class Ray():
    def __init__(self, orig, direct):
        self.orig = orig
        self.direct = direct

    def __str__(self):
        return "Loc: {:s} Dir: {:s}".format(str(self.orig), str(self.direct))


def main():
    v3 = Vec3(123, 234, 345)
    print(v3)
    v3 = Vec3("123.4  234.5  345.6")
    print(v3)
    print(v3.mag())
    v3.normalize()
    print(v3)
    v3.add(Vec3(1, 2, 3))
    print(v3)
    v3.subtract(Vec3(1, 2, 3))
    print(v3)

    a = Vec3(9, 2, 7)
    b = Vec3(4, 8, 10)
    print(a.dot(b))
    a = Vec3(2, 3, 4)
    b = Vec3(5, 6, 7)
    print(a.cross(b))

    a = Vec3(2, 3, 4)
    b = Vec3(5, 6, 7)
    print(a.mult(b))

if __name__ == '__main__':
    main()
