#version 130
in float time;
in float ptime;
uniform float part_lifetime;
uniform vec4 col;
uniform sampler2D tex_in;

in vec3 start_particle_time;

void main() {
    vec4  _col = texture(tex_in, gl_PointCoord) * col * gl_Color;
    gl_FragColor = vec4(_col.rgb, _col.a * clamp(1 - ptime / part_lifetime, 0, 1));
}
