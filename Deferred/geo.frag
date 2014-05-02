uniform sampler2D diffuseTexture;

varying vec2 texCoord;
varying vec3 normal;
varying float depth;

void main(void) {
    //diffuse color
    gl_FragData[0] = (gl_FrontMaterial.diffuse + texture2D(diffuseTexture, texCoord.st))/2.0;
    //ambient color
    gl_FragData[1] = gl_FrontMaterial.emission + gl_FrontMaterial.ambient;
    //normal + depth
    gl_FragData[2] = vec4(normalize(normal), depth);
}