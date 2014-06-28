"""holds definitions for many different types of objects
useful for rendering
"""

#standard
import abc
import traceback
from math3d import *

"""
---OBJECTS---
"""

class Camera():
    """Holds standard camera info for rendering"""
    def __init__(self):
        self.position = Vector(0, 0, 0)
        self.rotation = Quaternion.identity
        self.fov = 60.0
        self.near = 0.05
        self.far = 100.0

    def forward(self):
        return self.rotation*Vector(0, 0, 1)

    def up(self):
        return self.rotation*Vector(0, 1, 0)

class Object():
    """Holds standard object info for rendering"""
    def __init__(self):
        self.mesh = None
        self.material = None
        self.scale = Vector(1, 1, 1)
        self.position = Vector(0, 0, 0)
        self.rotation = Quaternion.identity

class Mesh():
    """Holds sandard mesh info"""
    def __init__(self):
        self.static = False
        self.vertices = ()
        self.normals = ()
        self.uv = ()
        self.triangles = ()

    def recalculate_normals(self):
        """Recalculates the normals
        according to the surface normals
        of each connected triangle.
        """
        normals = []

        for index in xrange(len(self.vertices)):
            vertex = self.vertices[index]
            norms = self._calculate_normals(index)

            average = Vector3.zero
            for normal in norms:
                average += normal
            if average.magnitude > 0:
                normals.append(average.normalized)
            else:
                normals.append(self.normals[index])

        self.normals = tuple(normals)

    def _calculate_normals(self, vertex):
        triangles = self.triangles
        vertices = self.vertices
        out = []

        for index in xrange(len(triangles)/3):
            index *= 3

            if vertex in triangles[index:index + 2]:
                v1 = vertices[triangles[index]]
                v2 = vertices[triangles[index + 1]]
                v3 = vertices[triangles[index + 2]]
                out.append(Vector3.cross(v2 - v1, v3 - v1))

        return out
