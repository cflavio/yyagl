#version 130
in float from_emission;
uniform float part_duration;
uniform vec4 col;
uniform sampler2D image;

in vec3 start_particle_time;

void main() {
    vec4  _col = texture(image, gl_PointCoord) * col * gl_Color;
    float alpha = clamp(1 - from_emission / part_duration, 0, 1);
    gl_FragColor = vec4(_col.rgb, _col.a * alpha);
}
