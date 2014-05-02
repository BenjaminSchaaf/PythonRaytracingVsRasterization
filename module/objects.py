"""holds definitions for many different types of objects
useful for rendering
"""

#standard
import abc
import traceback
from math3d import *

"""
---PARENTS---
"""

class Renderer():
    """Abstract baseclass for renderers.
    contains abstract methods for use in a base engine
    """
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def __init__(self, width, height):
        raise NotImplementedError("should have implemented this")
    
    @abc.abstractmethod
    def add_objects(self, objects):
        raise NotImplementedError("should have implemented this")
        
    @abc.abstractmethod
    def add_lights(self, lights):
        raise NotImplementedError("should have implemented this")
    
    @abc.abstractmethod
    def render(self, camera):
        raise NotImplementedError("should have implemented this")
    
    @abc.abstractmethod
    def close(self):
        raise NotImplementedError("should have implemented this")

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

def BLACK(): return Vector(0, 0, 0, 1)
def WHITE(): return Vector(1, 1, 1, 1)

class Material():
    """Holds standard material properties"""
    def __init__(self):
        self.emission = BLACK()
        self.ambient = BLACK()
        self.diffuse = WHITE()
        self.specular = WHITE()
        self.shininess = 0.0

POINT_LIGHT = 0
DIRECTIONAL_LIGHT = 1
SPOT_LITHGT = 2

class Light():
    def __init__(self, type=None):
        if not type: type = POINT_LIGHT
        self.type = type
        self.position = Vector(0, 0, 0)
        self.rotation = Quaternion.identity
        
        self.ambient = BLACK()
        self.diffuse = WHITE()
        self.specular = WHITE()
        self.spot_exponent = 0.0
        self.spot_angle = 0.0
        self.constant_atten = 0.0
        self.linear_atten = 1.0
        self.quadratic_atten = 0.0
    
    def forward(self):
        return self.rotation*Vector(0, 0, 1)
        