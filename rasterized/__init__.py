import pygame
import OpenGL
import common.objects
from OpenGL.GL import *
from OpenGL.GL.ARB.framebuffer_object import *
from OpenGL.GLU import *
from common.pyopengl import *

"""
   EXTENTION METHODS
"""
#Set renderer specific object methods. Makes code cleaner

#Extension method for Mesh objects
#Generates a OpenGL List Object for the mesh
def _Mesh__generate_glList(self):
    #Create a new list object
    self.listid = id = glGenLists(1)
    #Start defining a list object
    glNewList(id, GL_COMPILE)

    #Begin adding triangle data
    glBegin(GL_TRIANGLES)
    for tris in self.triangles:
        #add normal, uv and vertex data
        if len(self.normals) != 0:
            glNormal3f(*self.normals[tris])
        glVertex3f(*self.vertices[tris])
    #End adding triangle data
    glEnd()

    #end defining a list object
    glEndList()
#Apply extension method
common.objects.Mesh.generate_glList = _Mesh__generate_glList

#Extension method for Camera objects
#Sets projection matrix
def _Camera__apply_glMatrix(self):
    #calculate aspect ratio
    width, height = pygame.display.get_surface().get_size()

    glLoadIdentity()
    #Set perspective matrix
    gluPerspective(self.fov, float(width)/float(height), self.near, self.far)

    #Apply rotation matrix
    rt = self.rotation.matrix
    matrix = [rt[0], rt[1], rt[2], 0,
              rt[3], rt[4], rt[5], 0,
              rt[6], rt[7], rt[8], 0,
              0,     0,     0,     1]
    glMultMatrixf(matrix)
    glScalef(1, 1, -1)
    #Apply translation
    glTranslatef(*-self.position)
#Apply extension method
common.objects.Camera.apply_glMatrix = _Camera__apply_glMatrix

"""
   MAIN CLASS
"""

class Rasterizer:
    """Deferred Rastorizor"""

    """
       INITIALIZATION
    """
    def __init__(self, resolution, object):
        #Setup the pygame screen
        self.set_display(resolution)

        #set opengl global parameters
        self.set_opengl()
        #load glsl shaders
        self.load_shaders()

        #Add object
        object.generate_glList()
        self.object = object

        #Print OpenGL version
        print "Using OpenGL version: " + glGetString(GL_VERSION)

    def set_display(self, resolution):
        #initialize pygame display and set the pygame display mode appropriately
        pygame.display.init()
        pygame.display.set_mode(resolution, pygame.OPENGL|pygame.DOUBLEBUF)

    def set_opengl(self):
        glEnable(GL_DEPTH_TEST) #Z Buffer
        glEnable(GL_CULL_FACE) #face culling
        glClearColor(0.0, 0.0, 0.0, 0.0)

    def load_shaders(self):
        #Load shader objects from Hardcoded shader paths
        vertex = Shader("Rasterized/shader.vert")
        fragment = Shader("Rasterized/shader.frag")

        #Create program objects
        self.shader = ShaderProgram(vertex.id, fragment.id)
        glUseProgram(self.shader.id)

    """
       RUNTIME
    """

    #render with camera
    def render(self, camera):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #Setup camera projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        camera.apply_glMatrix()

        #Set camera forward uniform
        pos = camera.position
        #glUniform3f(self.shader.camera_position, pos.z, pos.y, pos.x)

        #Draw object
        glCallList(self.object.listid)

        #Flip front and back buffers
        pygame.display.flip()

    """
       CLEANUP
    """

    def close(self):
        #cleanup after ourselves
        pygame.quit()
        #Drivers should be smart enough to clean up the mess we left
