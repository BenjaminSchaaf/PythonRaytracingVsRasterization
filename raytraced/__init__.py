import pygame
import os
import common
from OpenGL.GL import *
from OpenGL.GLU import *
try:
    from OpenGL import GLX
    print "Using X (Unix) window system"
except:
    from OpenGL import WGL
    print "Using Wiggle (windows) window system"
import numpy
import ctypes
from ctypes import *
#import PyOpenCL Objects
from pyopencl import Buffer, Program, Context, CommandQueue, GLTexture
#import PyOpenCL enumberations
from pyopencl import mem_flags, context_properties, platform_info
#import dtypes
from pyopencl.array import vec as cltypes
from pyopencl import tools as cltools
import pyopencl as OpenCL
import pyopencl.array as cl_array
from common.pyopengl import *
import itertools

"""
Structures
"""

cltypes.Vertex = numpy.dtype([("position", cltypes.float4),
                              ("normal", cltypes.float4)])

"""
EXTENSION METHODS
"""
#Set renderer specific object methods. Makes code cleaner

#Extension method of Device class
#Returns wether device meets renderer requirements
def _pyopencl_Device__meets_requirements(self):
    #TODO: Maybe
    return "cl_khr_gl_sharing" in self.extensions
#Apply extension method
OpenCL.Device.meets_requirements = _pyopencl_Device__meets_requirements

#Extension method for Camera objects
#Sets projection matrix
def _Camera__getCl_info(self):
    mat = self.rotation.matrix
    pos = self.position
    forward = mat*common.math3d.Vector(0, 0, 1)
    up = mat*common.math3d.Vector(0, 1, 0)
    right = mat*common.math3d.Vector(1, 0, 0)
    out = numpy.array(list(pos) + [0] +
                      list(forward) + [0] +
                      list(up) + [0] +
                      list(right) + [0],
                      dtype=numpy.float32)
    return numpy.ndarray((4, 4), numpy.float32, out)
#Apply extension method
common.objects.Camera.getCl_info = _Camera__getCl_info

#Extension method for Object objects
#Sets transformation matrix
def _Object__get_matrix(self):
    #calculate matrix from rotation, scale and translation
    rt = self.rotation.matrix
    return [rt[0], rt[1], rt[2], self.position[0],
            rt[3], rt[4], rt[5], self.position[1],
            rt[6], rt[7], rt[8], self.position[2],
            0,     0,     0,     1]
#Apply extension method
common.objects.Object.get_matrix = _Object__get_matrix

"""
   MAIN CLASS
"""

class Raytracer:
    """Raytraced Renderer"""

    """
       INITIALISATION
    """
    def __init__(self, resolution, object):
        #initialize display
        self.set_display(resolution)
        self.width, self.height = resolution

        #initialize opengl
        self.set_opengl()

        #initialize opencl
        self.set_opencl()

        #build program
        self.load_program()

        #create the texture we render to
        self.create_texture()

        #Create global OpenCL buffers
        self.create_buffers()

        self.object = object
        self.load_object()

        #print OpenGL Version
        print "Using OpenGL version: " + glGetString(GL_VERSION)

    def set_display(self, resolution):
        #Create a pygame window
        pygame.display.init()
        pygame.display.set_mode(resolution,
                                pygame.OPENGL|pygame.DOUBLEBUF)

    def set_opengl(self):
        #create shader program
        vertex_shader = Shader("Raytraced/vertex.vert")
        fragment_shader = Shader("Raytraced/fragment.frag")
        self.draw_program = ShaderProgram(vertex_shader.id, fragment_shader.id)

        #create render quad
        self.render_quad = QUAD()

    def set_opencl(self):
        #Get all devices that fit requirements
        #from one platform
        good_devices = []
        good_platform = None
        for platform in OpenCL.get_platforms():
            for device in platform.get_devices():
                if device.meets_requirements():
                    good_devices.append(device)
            if len(good_devices) > 0:
                good_platform = platform
                break

        #Raise a not-supported exception if there are no good devices
        if len(good_devices) == 0:
            raise Exception("This program is not supported on your hardware")

        #Create a OpenCL context with platform specific properties
        properties = self.get_context_properties(good_platform)
        self.context = Context(good_devices, properties=properties)

        #Create the context queue
        self.queue = CommandQueue(self.context)

        #print OpenCL version
        print "Using OpenCL version: " + str(good_platform.get_info(platform_info.VERSION))

    def get_context_properties(self, plat):
        #reference context properties enumeration
        out = []

        #link OpenCL context platform
        out.append((context_properties.PLATFORM, plat))
        #link OpenGL context
        out.append((context_properties.GL_CONTEXT_KHR, platform.GetCurrentContext()))
        #link platform specific window contexts
        if "GLX" in globals():
            out.append((context_properties.GLX_DISPLAY_KHR, GLX.glXGetCurrentDisplay()))
        if "WGL" in globals():
            out.append((context_properties.WGL_HDC_KHR, WGL.wglGetCurrentDC()))

        #return context properties
        return out

    def load_program(self):
        #Read all the lines of the cl file into one string (safely)
        with open("Raytraced/Raytracer.cl", "r") as file:
            source = ''.join(file.readlines())

        #Create the opencl program
        program = Program(self.context, source)

        #make program options
        options = "-cl-mad-enable -cl-fast-relaxed-math -Werror -I %s" % os.path.dirname(os.path.abspath(__file__))

        #build program
        program.build(options=options)
        self.kernel = program.raytrace
        self.kernel.set_scalar_arg_dtypes([None, None, None,
                                           numpy.int32])

        #Match OpenCL Dtype. May not work everywhere
        cltypes.Vertex, c_decl = OpenCL.tools.match_dtype_to_c_struct(self.context.devices[0], 'Vertex', cltypes.Vertex)

    def create_texture(self):
        #Grab the screen size
        width, height = self.width, self.height

        #Create a GL texture objects
        self.gl_texture = texture = glGenTextures(1)

        #Bind the texture so we can change things
        glBindTexture(GL_TEXTURE_2D, texture)

        #Add parameters for texture access
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        #upload texture to GPU
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                     width, height, 0, GL_RGBA,
                     GL_FLOAT, None)

        #wait for OpenGL to finish executing every command
        glFinish()

        #Link the opengl texture to opencl
        self.render_texture = GLTexture(self.context,
                                        mem_flags.READ_WRITE,
                                        GL_TEXTURE_2D, 0,
                                        texture, 2)

    def create_buffers(self):
        self.meshes_buffer = None

    def load_object(self):
        vertices = []
        for tri in self.object.triangles:
            #Built vertex object
            position = tuple(list(self.object.vertices[tri]) + [0.0])
            normal = tuple(list(self.object.normals[tri]) + [0.0])
            vertex = (position, normal)
            vertices.append(vertex)

        self.meshes_array = numpy.array(vertices, dtype=cltypes.Vertex)

        #Make buffers
        self.meshes_buffer = Buffer(self.context, mem_flags.READ_ONLY | mem_flags.COPY_HOST_PTR, hostbuf=self.meshes_array)

    def render(self, camera):
        camera_info = camera.getCl_info()

        #Grab the screen size
        width, height = self.width, self.height

        #wait for OpenGL to finish all functions
        glFinish()
        #Bind OpenGL texture for OpenCL
        OpenCL.enqueue_acquire_gl_objects(self.queue, [self.render_texture])

        #Queue Raytrace
        self.raytrace(camera_info)

        #Unbind OpenGL texture from OpenCL
        OpenCL.enqueue_release_gl_objects(self.queue, [self.render_texture])

        #Render rendered texture to back-buffer
        self.render_render_texture()

        #Swap back and front buffers
        pygame.display.flip()

    def raytrace(self, camera_info):
        #Grab the global memory size (screen size)
        global_size = (self.width, self.height)

        #Execute OpenCL kernel with arguments
        self.kernel(self.queue, global_size, None,
                    self.render_texture, camera_info,
                    self.meshes_buffer,
                    len(self.meshes_array))

        #Wait for OpenCL to finish rendering
        self.queue.finish()

    def render_render_texture(self):
        #Reset projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        #Bind shader program
        glUseProgram(self.draw_program.id)

        #Bind render-texture for reading
        glActiveTexture(GL_TEXTURE0 + self.gl_texture)
        glBindTexture(GL_TEXTURE_2D, self.gl_texture)
        #Set argument in shader program
        glUniform1i(self.draw_program.renderTexture, self.gl_texture)

        #Render render-quad with texture to back-buffer
        glCallList(self.render_quad)

    def close(self):
        #close the pygame window
        pygame.quit()
        #The rest should be handled by the OS and the hardware driver
