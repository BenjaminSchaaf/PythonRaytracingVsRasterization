uniform vec3 camera_position;

varying vec3 position;
varying vec3 normal;

void main(void) {
    normal = gl_NormalMatrix * gl_Normal;

    position = gl_Vertex * gl_ProjectionMatrix;

    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
