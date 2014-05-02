import pygame
import OpenGL
import module.objects
from OpenGL.GL import *
from OpenGL.GL.ARB.framebuffer_object import *
from OpenGL.GLU import *
from module.objects import Renderer, Material
from module.pyopengl import *

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
            glNormal3f(self.normals[tris][2], self.normals[tris][1], self.normals[tris][0])
        if len(self.uv) != 0:
            glTexCoord2f(self.uv[tris][0], self.uv[tris][1])
        glVertex3f(self.vertices[tris][0], self.vertices[tris][1], self.vertices[tris][2])
    #End adding triangle data
    glEnd()
    
    #end defining a list object
    glEndList()
#Apply extension method
module.objects.Mesh.generate_glList = _Mesh__generate_glList

#Extension method for Material objects
#Sets uniform values to those of the object
def _Material__apply_glUniforms(self):
    glMaterialfv(GL_FRONT, GL_EMISSION, list(self.emission)) #emmissive property
    glMaterialfv(GL_FRONT, GL_DIFFUSE, list(self.diffuse)) #diffuse property
    glMaterialfv(GL_FRONT, GL_AMBIENT, list(self.ambient)) #ambient property
    glMaterialfv(GL_FRONT, GL_SPECULAR, list(self.specular)) #specuar property 
    glMaterialf(GL_FRONT, GL_SHININESS, self.shininess) #shiny property
#Apply extension method
module.objects.Material.apply_glUniforms = _Material__apply_glUniforms

#Extension method for Object objects
#Sets transformation matrix
def _Object__apply_glMatrix(self):
    #calculate matrix from rotation, scale and translation
    rt = self.rotation.matrix
    matrix = [rt[0], rt[1], rt[2], 0,
              rt[3], rt[4], rt[5], 0,
              rt[6], rt[7], rt[8], 0,
              0,     0,     0,     1]
    #apply matrix
    glMultMatrixf(matrix)
    #Apply translation
    glTranslatef(*self.position)
    #Apply scaling
    glScalef(*self.scale)
#Apply extension method
module.objects.Object.apply_glMatrix = _Object__apply_glMatrix

#Extension method for Camera objects
#Sets projection matrix
def _Camera__apply_glMatrix(self):
    #calculate aspect ratio
    width, height = pygame.display.get_surface().get_size()

    #Set perspective matrix
    gluPerspective(self.fov, float(width)/float(height), self.near, self.far)

    #Apply rotation matrix
    rt = self.rotation.matrix
    matrix = [rt[0], rt[1], rt[2], 0,
              rt[3], rt[4], rt[5], 0,
              rt[6], rt[7], rt[8], 0,
              0,     0,     0,     1]
    glMultMatrixf(matrix)
    #Apply translation
    glTranslatef(*self.position)
#Apply extension method
module.objects.Camera.apply_glMatrix = _Camera__apply_glMatrix

"""
   MAIN CLASS
"""

class Rasterizer(Renderer):
    """Deferred Rastorizor"""

    """
       INITIALIZATION
    """
    def __init__(self, width, height):
        #Setup the pygame screen
        self.set_display(width, height)
        
        #set opengl global parameters
        self.set_opengl()
        #load glsl shaders
        self.load_shaders()
        #generate framebuffers
        self.gen_buffers()
        #generate rendering quad
        self.render_quad = QUAD()
        
        #Setup local lists
        self.objects = []
        self.lights = []
        
        #Print OpenGL version
        print "Using OpenGL version: " + glGetString(GL_VERSION)
    
    def set_display(self, width, height):
        #initialize pygame display and set the pygame display mode appropriately
        pygame.display.init()
        pygame.display.set_mode((width, height), pygame.OPENGL|pygame.DOUBLEBUF)

    def set_opengl(self):
        glEnable(GL_DEPTH_TEST) #Z Buffer
        glEnable(GL_CULL_FACE) #face culling
    
    def load_shaders(self):
        #Load shader objects from Hardcoded shader paths
        geo_vert = Shader("Deferred/geo.vert")
        geo_frag = Shader("Deferred/geo.frag")
        comp_vert = Shader("Deferred/comp.vert")
        comp_frag = Shader("Deferred/comp.frag")
        
        #Create program objects
        self.geo_pass = ShaderProgram(geo_vert.id, geo_frag.id)
        self.comp_pass = ShaderProgram(comp_vert.id, comp_frag.id)
    
    def gen_buffers(self):
        #create a new framebuffer
        self.framebuffer = buffer = glGenFramebuffers(1)
        #Bind the framebuffer so we can add textures
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, buffer)
        
        #add textures to the framebuffer
        self.diffuse_texture = RenderTexture(GL_RGBA, GL_UNSIGNED_BYTE, GL_COLOR_ATTACHMENT0)
        self.ambient_texture = RenderTexture(GL_RGBA, GL_UNSIGNED_BYTE, GL_COLOR_ATTACHMENT1)
        self.normal_texture = RenderTexture(GL_RGBA, GL_UNSIGNED_BYTE, GL_COLOR_ATTACHMENT2)
        
        self.check_framebuffer_status()

    def check_framebuffer_status(self):
        #check if the framebuffer is good
        status = glCheckFramebufferStatus(GL_DRAW_FRAMEBUFFER)
        if (status != GL_FRAMEBUFFER_COMPLETE):
            print status
            #BAD Framebuffer
            raise Exception("Bad Framebuffer")

    """
       EVENT FUNCTIONS
    """
    
    def add_objects(self, objects):
        #Create a new opengl list object for each object
        for object in objects:
            mesh = object.mesh
            mesh.generate_glList()
        
        #add objects to objects list for rendering
        self.objects += objects
    
    def add_lights(self, lights):
        #TODO: Stuff, Write comments
        id = len(self.lights)
        
        for light in lights:
            light.id = getattr(OpenGL.GL, "GL_LIGHT" + str(id))
            id += 1

    """
       RUNTIME
    """
    
    #render with camera
    def render(self, camera):
        #Setup camera projection matrix
        glMatrixMode(GL_PROJECTION)
        camera.apply_glMatrix()
        
        #render objects to Framebuffer
        self.geometry_pass(camera)
        
        #Reset camera projection matrix to identity
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        #Combine lighting with Framebuffer and render to screen
        self.combination_pass()
        
        #Flip front and back buffers
        pygame.display.flip()

    """
       GEOMETRY PASS
    """
    
    def geometry_pass(self, camera):
        #Setup model view matrix
        glMatrixMode(GL_MODELVIEW)
        
        #use the geometry pass Shader Program
        glUseProgram(self.geo_pass.id)
        
        #give the shaders the cameras far clip plane
        glUniform1f(self.geo_pass.farClip, camera.far)
        
        #Set to use the created framebuffer with MTR rendering
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)
        glDrawBuffers(4, [GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1,
                          GL_COLOR_ATTACHMENT2])
        self.clear() #must clear framebuffer
        
        #Render objects to framebuffer object
        self.draw_objects()

    def draw_objects(self):
        default_material = Material()
        
        #render all objects in objects list
        for obj in self.objects:
            #copy model view matrix into stack
            #erases the need to reset the matrix after every object
            glPushMatrix()

            #Apply material properties
            if obj.material:
                obj.material.apply_glUniforms()
            else:
                default_material.apply_glUniforms()
            
            #apply object rotation
            obj.apply_glMatrix()
            
            #render object
            glCallList(obj.mesh.listid)
            
            #pop transformation matrix from stack
            glPopMatrix()

    """
       LIGHTING PASS
    """
    
    def combination_pass(self):
        #Set to use screen framebuffer for rendering
        #Keep previous framebuffer for reading
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        #Set to STR rendering for the back buffer
        glDrawBuffer(GL_BACK)
        #clear the buffer
        self.clear()
        
        #use the lighting pass Shader Program
        comp_pass = self.comp_pass
        glUseProgram(comp_pass.id)
        
        #Set uniform texture values
        self.set_uniform_texture(comp_pass.diffuse2D, self.diffuse_texture.id)
        self.set_uniform_texture(comp_pass.ambient2D, self.ambient_texture.id)
        self.set_uniform_texture(comp_pass.normal2D, self.normal_texture.id)
        
        #Render the render quad. Like Blit but with shaders
        glCallList(self.render_quad)
    
    def set_uniform_texture(self, uniform, id):
        #Activate the texture for accessing
        glActiveTexture(GL_TEXTURE0 + id)
        #No idea why you have to bind it
        glBindTexture(GL_TEXTURE_2D, id)
        #Apply it to the uniform value
        glUniform1i(uniform, id)
    
    def set_lights(self):
        #TODO: STUFF!!!
        for light in self.lights:
            glLightfv(light.id, GL_AMBIENT, *light.ambient)
            glLightfv(light.id, GL_DIFFUSE, *light.diffuse)
            glLightfv(light.id, GL_SPECULAR, *light.specular)
            
            if light.type == DIRECTIONAL_LIGHT:
                glLightfv(light.id, GL_POSITION, *light.forward())
                continue
            else:
                glLightfv(light.id, GL_POSITION, *light.position)
                glLightfv(light.id, GL_SPOT_DIRECTION, *light.forward())
    
    def clear(self):
        #clear the current draw buffer
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT) #clear both color and depth

    """
       CLEANUP
    """
    
    def close(self):
        #cleanup after ourselves
        pygame.quit()
        #Drivers should be smart enough to clean up the mess we left
        #Just like in python, we shouldn't need to free memory ourselves

"""
   CLASSES
"""

class Framebuffer():
    def __init__(self):
        self.id = id = glGenFramebuffersEXT(1)

class RenderTexture():
    def __init__(self, format, internal_format, attachement, width=None, height=None):
        #infer width and height fron pygame context
        if not (width or height):
            width, height = pygame.display.get_surface().get_size()
        
        #generate texture object
        self.id = texture = glGenTextures(1)
        
        #Bind texture
        glBindTexture(GL_TEXTURE_2D, texture)
        glEnable(GL_TEXTURE_2D)
        
        #Add parameters for texture access
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        
        #upload texture to GPU
        glTexImage2D(GL_TEXTURE_2D, 0, format,
                     width, height, 0,
                     format, internal_format,
                     None)
        
        #Reference texture to framebuffer and unbind
        glFramebufferTexture2D(GL_FRAMEBUFFER, attachement, GL_TEXTURE_2D, texture, 0)
        glBindTexture(GL_TEXTURE_2D, 0)