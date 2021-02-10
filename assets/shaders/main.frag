#version 130
uniform sampler2D p3d_Texture1;
in vec2 texCoord;
out vec4 fragColor;

void main() {
    fragColor = texture(p3d_Texture1, texCoord);
}