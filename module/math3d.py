"""This module has definitions for some useful
mathematical values represented in pure python,
such as vector maths, quaternion and matrices
as well as some useful shortcut solutions
to some common problems

Works best with pypy (Not CPython)
"""

import math

class _classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()

class DimentionMissmatchException(Exception): pass

class Vector():
    """A Generalised Vector class deigned with minimal overhead.
    The Vectors dimension number is determined when it is created
    and stays constant for it's lifetime.
    """
    __slows__ = ["_value"]
    def __init__(self, *args):
        """Makes a new Vector with either
        each vector component separately
        or any iterable as arguments
        """
        if len(args) == 1:
            args = args[0]
        self._value = tuple(float(arg) for arg in args)

    def __len__(self):
        """Returns the dimension number"""
        return len(self._value)

    def __str__(self):
        """Returns a nicely formatted string representation of the Vector"""
        return str(self._value)
    def __repr__(self):
        """Returns a nicely formatted string representation of the Vector"""
        return repr(self._value)

    def __add__(vec1, vec2):
        """Adds two Vectors with the same dimension number.
        Raises a DimentionMissmatchException if they don't match
        """
        if len(vec1) == len(vec2):
            return Vector(vec1[i] + vec2[i] for i in range(len(vec1)))
        raise DimentionMissmatchException()
    __radd__ = __add__

    def __iadd__(self, other):
        """Adds another Vector to itself.
        Raises a DimentionMissmatchException
        if the dimension numbers don't match
        """
        if len(self) == len(other):
            self._value = tuple(self[i] + other[i] for i in range(len(self)))
            return self
        raise DimentionMissmatchException()

    def __sub__(vec1, vec2):
        """Subtracts two Vectors with the same dimension number.
        Raises a DimentionMissmatchException if they don't match
        """
        if len(vec1) == len(vec2):
            return Vector(vec1[i] - vec2[i] for i in range(len(vec1)))
        raise DimentionMissmatchException()
    __rsub__ = __sub__

    def __isub__(self, other):
        """Subtracts another Vector to itself.
        Raises a DimentionMissmatchException
        if the dimension numbers don't match
        """
        if len(self) == len(other):
            self._value = tuple(self[i] - other[i] for i in range(len(self)))
            return self
        raise DimentionMissmatchException()

    def __neg__(self):
        """Returns the negative value of the Vector"""
        return Vector(-value for value in self)

    def __mul__(vec, scalar):
        """Multiplies a Vector by a Scalar"""
        scalar = float(scalar)
        return Vector(value*scalar for value in vec)
    __rmul__ = __mul__

    def __imul__(self, other):
        """Multiplies another Scalar by itself"""
        other = float(other)
        self._value = tuple(self[i]*other for i in range(len(self)))

    def __div__(vec, scalar):
        """Divides a Vector by a Scalar"""
        scalar = float(scalar)
        return Vector(value/scalar for value in vec)
    __truediv__ = __div__

    def __floordiv__(vec, scalar):
        """Divides a Vector by an integer Scalar"""
        scalar = int(scalar)
        return Vector(value/scalar for value in vec)

    def __idiv__(self, other):
        """Divides another Scalar by itself"""
        other = float(other)
        self._value = tuple(self[i]/other for i in range(len(self)))

    def __eq__(vec1, vec2):
        """Checks equality between Vectors"""
        if len(vec1) != len(vec2): return False

        return False not in [vec1[i] == vec2[i] for i in range(len(vec1))]

    def __getitem__(self, key):
        """Get a value from a Vector given a dimension"""
        return self._value[key]

    def __setitem__(self, key, value):
        """Set a value from a Vector given a dimension"""
        self._value = tuple(float(value) if i == key else self[i]
                            for i in range(len(self)))

    def __iter__(self):
        """Returns the iterator of the internal Tuple object"""
        return iter(self._value)

    def __list__(self):
        return list(self._value)

    def __tuple__(self):
        return tuple(self._value)

    def __float__(self):
        return self.magnitude

    def __int__(self):
        return len(self)

    @property
    def x(self):
        """Shorthand for getting Vector[0]"""
        return self[0]

    @x.setter
    def x(self, value):
        """Shorthand for setting Vector[0]"""
        self[0] = value

    @property
    def y(self):
        """Shorthand for getting Vector[1]"""
        return self[1]

    @y.setter
    def y(self, value):
        """Shorthand for setting Vector[1]"""
        self[0]= value

    @property
    def z(self):
        """Shorthand for getting Vector[2]"""
        return self[2]

    @z.setter
    def z(self, value):
        """Shorthand for setting Vector[2]"""
        self[2] = value

    @property
    def w(self):
        """Shorthand for getting Vector[3]"""
        return self[3]

    @w.setter
    def w(self, value):
        """Shorthand for setting Vector[3]"""
        self[3] = value

    @property
    def magnitude(self):
        """Returns the magnitude of the Vector"""
        return sum(value**2 for value in self)**0.5

    @magnitude.setter
    def magnitude(self, value):
        """Sets the magnitude of the Vector
        Direction is maintained
        """
        multi = float(value)/self.magnitude
        self._value = tuple(val*multi for val in self)

    @property
    def magnitude2(self):
        """Returns the magnitude squared of the Vector
        Useful for comparing lengths
        """
        return sum(value**2 for value in self)

    @property
    def normalized(self):
        """Returns the normalized direction Vector"""
        return self/self.magnitude

    @normalized.setter
    def normalized(self, value):
        """Sets the normalized direction Vector
        Magnitude is maintained
        """
        if len(self) == len(value):
            mag = self.magnitude
            self._value = tuple(val*mag for val in value)
        else:
            raise DimentionMissmatchException()

    def normalize(self):
        """Normalizes the Vector"""
        magnitude = self.magnitude
        self._value = tuple(value/magnitude for value in self)

    @classmethod
    def dot(cls, vect1, vect2):
        """Returns the dot product between two Vectors"""
        if len(vect1) == len(vect2):
            return sum(vect1[i]*vect2[i] for i in range((len(vect1))))
        raise DimentionMissmatchException()

    @classmethod
    def angle(cls, vect1, vect2):
        """Returns the angle between two Vectors in radians"""
        return math.acos(cls.dot(vect1, vect2)/
                         vect1.magnitude*vect2.magnitude)

    @classmethod
    def angleD(cls, vect1, vect2):
        """Returns the angle between two Vectors in degrees"""
        return cls.angle(vect1, vect2)*180/math.pi

    @classmethod
    def distance(cls, vect1, vect2):
        """Returns the distance between two Vectors"""
        return (vect1 - vect2).magnitude

    @classmethod
    def scale(cls, vect1, vect2):
        """Multiplies two Vectors component wise"""
        if len(vect1) == len(vect2):
            return Vector(vect1[i] * vect2[i] for i in range(len(vect1)))
        raise DimentionMissmatchException()

    @classmethod
    def cross2(cls, vect):
        """Returns the two dimensional cross product of a Vector.
        Ignores other dimensions
        """
        if len(vect) >= 2:
            return Vector(-vect[1], vect[0])
        raise DimentionMissmatchException()

    @classmethod
    def cross3(cls, v1, v2):
        """Returns the three dimensional cross product of two Vectors.
        Ignores other dimensions
        """
        if len(v1) == len(v2) >= 3:
            return Vector(v1[1]*v2[2] - v1[2]*v2[1],
                          v1[2]*v2[0] - v1[0]*v2[2],
                          v1[0]*v2[1] - v1[1]*v2[0])
        raise DimentionMissmatchException()

class Quaternion(object):
    __slots__ = ["_value"]
    def __init__(self, *args):
        if len(args) == 4:
            self._value = (float(args[0]), float(args[1]), float(args[2]), float(args[3]))
        elif len(args) == 1:
            args = args[0]
            self._value = (float(args[0]), float(args[1]), float(args[2]), float(args[3]))
        else:
            raise AttributeError()

    def __len__(self):
        return len(self._value)

    def __str__(self):
        return str(self._value)
    __repr__ = __str__

    def __mul__(self, other):
        if len(other) == len(self):
            return Quaternion(
                self[3]*other[3] - self[1]*other[1] - self[2]*other[2] - self[0]*other[0],
                self[3]*other[1] + self[1]*other[3] + self[2]*other[0] - self[0]*other[2],
                self[3]*other[2] - self[1]*other[0] + self[2]*other[3] + self[0]*other[1],
                self[3]*other[0] + self[1]*other[2] - self[2]*other[1] + self[0]*other[3]
            )
        return self.matrix*other
    __rmul__ = __mul__

    def __getitem__(self, key):
        return self._value[key]

    def __setitem__(self, key, value):
        values = list(self._value)
        values[key] = float(value)
        self._value = tuple(values)

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, value):
        self._value = (float(value), self[1], self[2], self[3])

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, value):
        self._value = (self[0], float(value), self[2], self[3])

    @property
    def z(self):
        return self[2]

    @z.setter
    def z(self, value):
        self._value = (self[0], self[1], float(value), self[3])

    @property
    def w(self):
        return self[3]

    @w.setter
    def w(self, value):
        self._value = (self[0], self[1], self[2], float(value))

    @property
    def matrix(self):
        return Matrix3x3(
            (1 - 2*self.y**2 - 2*self.z**2), 2*(self.x*self.y + self.w*self.z), 2*(self.x*self.z - self.w*self.y),
            2*(self.x*self.y - self.w*self.z), (1 - 2*self.x**2 - 2*self.z**2), 2*(self.y*self.z + self.w*self.x),
            2*(self.x*self.z + self.w*self.y), 2*(self.y*self.z - self.w*self.x), (1 - 2*self.x**2 - 2*self.y**2)
        )

    @classmethod
    def euler(cls, *args):
        if len(args) == 3:
            args = [Vector(*args)]
        angles = args[0]

        c1 = math.cos(angles.y/2)
        s1 = math.sin(angles.y/2)
        c2 = math.cos(angles.z/2)
        s2 = math.sin(angles.z/2)
        c3 = math.cos(angles.x/2)
        s3 = math.sin(angles.x/2)
        c1c2 = c1*c2
        s1s2 = s1*s2
        return Quaternion(
            c1c2*s3 + s1s2*c3,
            s1*c2*c3 + c1*s2*s3,
            c1*s2*c3 - s1*c2*s3,
            c1c2*c3 - s1s2*s3
        )

    @_classproperty
    def identity(cls):
        return Quaternion(0, 0, 0, 1)

class Matrix3x3(object):
    def __init__(self, *args):
        if len(args) == 9:
            self._value = tuple(args)
        else:
            raise AttributeError()

    def __len__(self):
        return (3, 3)

    def __getitem__(self, key):
        return self._value[key]

    def __setitem__(self, key, value):
        values = list(self._value)
        values[key] = float(value)
        self._value = tuple(values)

    def __mul__(self, other):
        if len(other) == 3:
            return Vector(
                other[0]*self[0] + other[1]*self[1] + other[2]*self[2],
                other[0]*self[3] + other[1]*self[4] + other[2]*self[5],
                other[0]*self[6] + other[1]*self[7] + other[2]*self[8])
        if len(other) == (3, 3):
            raise NotImplementedError()
