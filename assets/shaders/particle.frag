#version 150
in float from_emission;
in vec4 color;
uniform float part_duration;
uniform vec4 col;
uniform sampler2D image;
out vec4 p3d_FragData[1];

in vec3 start_particle_time;

void main() {
    vec4  _col = texture(image, gl_PointCoord) * col * color;
    float alpha = clamp(1 - from_emission / part_duration, 0, 1);
    p3d_FragData[0] = vec4(_col.rgb, _col.a * alpha);
}
