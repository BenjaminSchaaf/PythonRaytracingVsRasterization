uniform sampler2D diffuse2D;
uniform sampler2D ambient2D;
uniform sampler2D normal2D;

void main(void) {
    vec4 color = texture2D(diffuse2D, gl_TexCoord[0].xy) + texture2D(ambient2D, gl_TexCoord[0].xy);
    vec4 normal_distance = texture2D(normal2D, gl_TexCoord[0].xy);
    vec3 normal = normal_distance.xyz;
    float dist = float(normal_distance.w);

    gl_FragColor = color*(dot(normal, vec3(0.0, 0.0, 1.0) + 0.1));
}
