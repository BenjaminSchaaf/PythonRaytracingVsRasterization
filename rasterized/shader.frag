varying vec3 position;
varying vec3 normal;

void main(void) {
    float shading = dot(normalize(position), normalize(normal));
    gl_FragColor = vec4(normal, 1.0);
}
