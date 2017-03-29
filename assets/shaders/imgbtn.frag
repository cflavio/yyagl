#version 120
varying vec2 texcoord;
uniform sampler2D p3d_Texture0;
uniform float col_offset;
vec4 p3d_FragColor;
uniform float enable;

void main() {
    float dist_l = texcoord.x;
    float dist_r = 1 - texcoord.x;
    float dist_u = texcoord.y;
    float dist_b = 1 - texcoord.y;
    float min_dist = min(dist_l, min(dist_r, min(dist_u, dist_b)));
    float alpha = clamp(min_dist * 30, 0, 1);
    vec4 txt_col = texture2D(p3d_Texture0, texcoord);
    vec4 offset_col = vec4(vec3(col_offset), 1);
    gl_FragColor = (txt_col + offset_col) * vec4(1, 1, 1, alpha * enable);
}