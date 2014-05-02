"""
Holds classes for simpler opengl work
"""

from OpenGL.GL import *

class Shader():
    #Shader file extensions
    _vertex_extensions = ["vert", "v"]
    _fragment_extensions = ["frag", "f"]
    
    def __init__(self, path, type=None):
        #infer shader type from file extension
        if not type: type = Shader.get_type(path)
        
        #create shader object
        self.id = shader = glCreateShader(type)
        
        #compile shader from file
        with open(path) as file:
            lines = file.readlines()
        glShaderSource(shader, lines)
        glCompileShader(shader)
        
        #print shader log
        info = glGetShaderInfoLog(shader)
        if info: print info
    
    @classmethod
    def get_type(cls, path):
        #get file extension
        extension = path.split(".")[-1]
        
        #Map file extension to shader type
        if extension in cls._vertex_extensions:
            return GL_VERTEX_SHADER
        elif extension in cls._fragment_extensions:
            return GL_FRAGMENT_SHADER
        
        #throw error if type could not be inferred
        raise Exception("Could not infer Shader type from file extension")

class ShaderProgram():
    def __init__(self, vertex, fragment):
        #Create a shader program
        self.id = id = glCreateProgram()
        
        #Attach and upload shaders
        glAttachShader(id, vertex)
        glAttachShader(id, fragment)
        glLinkProgram(id)
        
        #Try using the shader. OpenGL will raise Exceptions if there was an error
        try:
            glUseProgram(id)
        except OpenGL.error.GLError:
            print glGetProgramInfoLog(id)
        glUseProgram(0)
        
        #Get active Uniform values from Shader Program and add them to object by name
        for i in range(glGetProgramiv(id, GL_ACTIVE_UNIFORMS)):
            #Try block in case of implementation error
            try:
                name = glGetActiveUniform(id, i)[0]
                #only add uniforms that are possible to access by python
                if "." not in name:
                    self.__dict__[name] = i
            except:
                continue

def QUAD():
    #Create a primitive Quad
    id = glGenLists(1)
    glNewList(id, GL_COMPILE)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(-1, -1)
    glTexCoord2f(1, 0)
    glVertex2f(1, -1)
    glTexCoord2f(1, 1)
    glVertex2f(1, 1)
    glTexCoord2f(0, 1)
    glVertex2f(-1, 1)
    glEnd()
    glEndList()
    return id
