#version 130
in float time;
uniform float tot_time;  // particle system's total time
uniform vec4 color;
void main() {
    gl_FragColor = vec4(color.rgb, clamp(1 - time / tot_time, 0, 1));
}
