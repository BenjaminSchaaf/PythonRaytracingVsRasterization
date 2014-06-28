"""
Contains functions for loading optimised Wavefront .obj
files into nicely formatted objects with optimised data.
"""

import string
from math3d import Vector
from objects import Mesh

def load(path):
    """
    load(path:str) -> [Mesh,]

    Loads a .obj file from "path"
    and returns it in a Mesh object
    """

    objects = []

    with open(path, "r") as file:
        lines = file.readlines()
        objs = __split_objects(lines)
        for obj in objs:
            obj = __parse_lines(obj)
            if obj:
                obj.file = path
                objects.append(obj)

    return objects

def __split_objects(lines):
    objects = []

    index = 0
    last_index = 0
    while index < len(lines):
        values = lines[index].split(" ")
        index += 1

        if values[0] == "o":
            objects.append(lines[last_index:index])
            last_index = index
    objects.append(lines[last_index:])

    return objects

def __parse_lines(lines):
    verts = []
    norms = []
    tris = []

    for line in lines:
        attributes = line.split(" ")

        if attributes[0] == "#" or len(attributes) < 2:
            continue

        if attributes[0] == "v":
            verts.append(Vector(
                float(attributes[1]),
                float(attributes[2]),
                float(attributes[3])));
        elif attributes[0] == "vn":
            norms.append(Vector(
                float(attributes[1]),
                float(attributes[2]),
                float(attributes[3])));
        elif attributes[0] == "f":
            i = 3
            while i < len(attributes):
                for j in xrange(3):
                    values = attributes[i - 2 + j].split("/")
                    value = Vector(-1, -1, -1)
                    value[0] = int(values[0]) - 1
                    if len(values) == 3:
                        if values[1] != "":
                            value[1] = int(values[1]) - 1
                        if values[2] != "":
                            value[2] = int(values[2]) - 1
                    tris.append(value)
                i += 1

    if len(tris) == 0:
        return

    vertices = []
    normals = []

    triangles = []

    index = 0
    for triangle in tris:
        vertices.append(verts[int(triangle[0])])
        normals.append(norms[int(triangle[2])])
        triangles.append(index)
        index += 1

    mesh = Mesh()
    mesh.vertices = tuple(vertices)
    mesh.normals = tuple(normals)
    mesh.triangles = tuple(triangles)

    return mesh
