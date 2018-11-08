#version 130
in float time;
uniform float tot_time;  // particle system's total time
uniform vec4 color;
uniform sampler2D tex_in;
void main() {
    vec4  tex_col = texture(tex_in, gl_PointCoord);
    gl_FragColor = vec4(tex_col.rgb, clamp(1 - time / tot_time, 0, 1));
}
