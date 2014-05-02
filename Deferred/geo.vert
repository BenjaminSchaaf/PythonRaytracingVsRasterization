uniform float farClip;

varying vec2 texCoord;
varying vec3 normal;
varying float depth;

float getViewDistance(void) {
    return -(gl_ModelViewMatrix * gl_Vertex).z;
}

void main(void) {
    texCoord = gl_MultiTexCoord0.st;
    normal = gl_NormalMatrix * gl_Normal;
    depth = getViewDistance() / farClip;
    
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}