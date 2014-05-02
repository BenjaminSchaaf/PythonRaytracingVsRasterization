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
    uvs = []
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
        elif attributes[0] == "vt":
            uvs.append(Vector(
                float(attributes[1]),
                float(attributes[2])));
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
    uv = []

    triangledict = {}
    triangles = []

    index = 0
    for triangle in tris:
        name = ''.join([str(int(triangle[0])), str(int(triangle[1])), str(int(triangle[2]))])
        if name not in triangledict:
            triangledict[name] = index
            vertices.append(verts[int(triangle[0])])
            if triangle[1] >= 0:
                uv.append(uvs[int(triangle[1])])
            else:
                uv.append(Vector(0, 0))
            if triangle[2] >= 0:
                normals.append(norms[int(triangle[2])])
            else:
                normals.append(Vector(0, 0, 0))
            index += 1
        triangles.append(triangledict[name])

    mesh = Mesh()
    mesh.vertices = tuple(vertices)
    mesh.normals = tuple(normals)
    mesh.uv = tuple(uv)
    mesh.triangles = tuple(triangles)

    return mesh
