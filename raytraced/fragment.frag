uniform sampler2D renderTexture;

void main(void) {
    gl_FragColor = texture2D(renderTexture, gl_TexCoord[0].xy);
}