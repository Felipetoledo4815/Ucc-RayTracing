#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  test_scanning.py
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

CSV_FILE = "cam_points.csv"

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pylab as plt
import csv
import math


def show_xyz(x, y, z, N):
    for i in range(N):
        print("{:12.6f}  {:12.6f}  {:12.6f}".format(x[i], y[i], z[i]))

def normalize(x, y, z):
    d = math.sqrt(x*x + y*y + z*z)
    return x/d, y/d, z/d

def dot(x1, y1, z1, x2, y2, z2):
    return x1*x2 + y1*y2 + z1*z2

def main(args):
    x = []; y = []; z = []
    with open(CSV_FILE, "r") as csvf:
        rdr = csv.reader(csvf)
        for row in rdr:
            x.append(float(row[0]))
            y.append(float(row[1]))
            z.append(float(row[2]))

    #~ show_xyz(x, y, z, 20)

    # Calcular un plano a distancia del origen, perpendicular con eje z
    # (representa la pantalla de la computadora)
    D = 1
    x1 = []; y1 = []; z1 = []
    for i in range(len(x)):
        scale = D/z[i]
        z1.append(D)
        y1.append(y[i]*scale)
        x1.append(x[i]*scale)

    # Calcular la intersección de cada rayo con un plano variable
    D = 1                                  # Distancia origen al plano
    dx = 0; dy = 0.2; dz = 0.5                  # Vector perpendicular sobre plano
    nx, ny, nz = normalize(dx, dy, dz)        # Valores normalizados (= normal)
    print(nx, ny, nz)

    x2 = []; y2 = []; z2 = []

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_zlim3d([0, 2])
    ax.set_title("Intersección rayos con un plano")
    #~ ax.set_ylim3d([-1, 1])
    #~ ax.set_xlim3d([-1, 1])

    ax.scatter(x, y, z)         # Puntos finales de los vectores de direccion
    ax.scatter(x1, y1, z1)      # Puntos reconstruidos de la pantalla

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
