#version 130
in vec2 texcoord;
uniform sampler2D in_tex;
uniform float gamma;
out vec4 p3d_FragColor;

vec4 gamma_correct(vec4 col) {
    return vec4(pow(vec3(col), vec3(1.0 / gamma)), 1.0);
}

void main() {
    p3d_FragColor = gamma_correct(texture(in_tex, texcoord));
}