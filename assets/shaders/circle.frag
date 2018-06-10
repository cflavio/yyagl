#version 120
varying vec2 texcoord;
uniform sampler2D p3d_Texture0;
uniform float ray;
uniform float width;
uniform vec4 color_start;
uniform vec4 color_end;
uniform float progress;

vec4 p3d_FragColor;

void main() {
    const float PI = 3.14159265359;
    vec2 xy = texcoord - .5;
    float r = length(xy);
    float r_ext = ray + width / 2.0;
    float k_r_ext = smoothstep(r_ext, r_ext - .005, r);
    float r_int = ray - width / 2.0;
    float k_r_int = smoothstep(r_int - .005, r_int, r);
    float angle = atan(xy.y, xy.x);
    float angle_void = .4;
    float scaled_progr = (PI - angle_void) - (PI - 2 * angle_void) * progress;
    float mix_val = 1 - (angle - angle_void) / (PI - 2 * angle_void);
    vec4 fragcol = mix(color_start, color_end, mix_val);
    fragcol *= k_r_int * k_r_ext;
    fragcol *= smoothstep(scaled_progr - 0.01, scaled_progr, angle);
    fragcol *= smoothstep(PI - angle_void, PI - angle_void - 0.01, angle);
    gl_FragColor = fragcol;
}
