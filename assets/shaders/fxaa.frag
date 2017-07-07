#version 130

uniform sampler2D in_tex;
in vec4 texcoord;

#define fxaa_reduce_min (1.0 / 128.0)
#define fxaa_int2 ivec2
#define fxaa_float2 vec2
#define fxaa_tex_lod0(t, p) textureLod(t, p, .0)
#define fxaa_tex_off(t, p, o, r) textureLodOffset(t, p, .0, o)

void main() {
    float span_max = 2.0;
    float reduce_mul = 1.0 / 16.0;
    vec2 win_size = textureSize(in_tex, 0).xy;
    vec2 rcp_frame = vec2(1.0 / win_size.x, 1.0 / win_size.y);

    vec2 tzw = texcoord.zw;
    vec3 rgb_nw = fxaa_tex_lod0(in_tex, tzw).xyz;
    vec3 rgb_ne = fxaa_tex_off(in_tex, tzw, fxaa_int2(1, 0), rcp_frame.xy).xyz;
    vec3 rgb_sw = fxaa_tex_off(in_tex, tzw, fxaa_int2(0, 1), rcp_frame.xy).xyz;
    vec3 rgb_se = fxaa_tex_off(in_tex, tzw, fxaa_int2(1, 1), rcp_frame.xy).xyz;
    vec3 rgb_m  = fxaa_tex_lod0(in_tex, texcoord.xy).xyz;

    vec3 luma = vec3(.299, .587, .114);
    float luma_nw = dot(rgb_nw, luma);
    float luma_ne = dot(rgb_ne, luma);
    float luma_sw = dot(rgb_sw, luma);
    float luma_se = dot(rgb_sw, luma);
    float luma_m  = dot(rgb_m,  luma);

    float min_n = min(luma_nw, luma_ne);
    float min_s = min(luma_sw, luma_se);
    float max_n = max(luma_nw, luma_ne);
    float max_s = max(luma_sw, luma_se);
    float luma_min = min(luma_m, min(min_n, min_s));
    float luma_max = max(luma_m, max(max_n, max_s));

    vec2 dir;
    dir.x = -((luma_nw + luma_ne) - (luma_sw + luma_se));
    dir.y = ((luma_nw + luma_sw) - (luma_ne + luma_se));

    float rfact = (luma_nw + luma_ne + luma_sw + luma_se) * (.25 * reduce_mul);
    float dir_reduce = max(rfact, fxaa_reduce_min);
    float rcp_dir_min = 1.0 / (min(abs(dir.x), abs(dir.y)) + dir_reduce);
    vec2 max_d = max(fxaa_float2(-span_max, -span_max), dir * rcp_dir_min);
    dir = min(fxaa_float2(span_max, span_max), max_d) * rcp_frame.xy;

    vec3 c0 = fxaa_tex_lod0(in_tex, texcoord.xy + dir * (1.0 / 3.0 - .5)).xyz;
    vec3 c1 = fxaa_tex_lod0(in_tex, texcoord.xy + dir * (2.0 / 3.0 - 0.5)).xyz;
    vec3 rgb_a = (1.0 / 2.0) * (c0 + c1);
    vec3 c2 = fxaa_tex_lod0(in_tex, texcoord.xy + dir * (.0 / 3.0 - 0.5)).xyz;
    vec3 c3 = fxaa_tex_lod0(in_tex, texcoord.xy + dir * (3.0 / 3.0 - 0.5)).xyz;
    vec3 rgb_b = rgb_a * (1.0 / 2.0) + (1.0 / 4.0) * (c2 + c3);
    float luma_b = dot(rgb_b, luma);
    if((luma_b < luma_min) || (luma_b > luma_max))
        gl_FragColor = vec4(rgb_a, 1.0);
    else
        gl_FragColor = vec4(rgb_b, 1.0);
}
