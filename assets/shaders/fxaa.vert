#version 130
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform sampler2D in_tex;
out vec4 texcoord;
out vec2 win_size;
out vec2 rcp_frame;

void main() {
    float subpix_shift = 1.0 / 8.0;
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    win_size = textureSize(in_tex, 0).xy;
    rcp_frame = vec2(1.0 / win_size.x, 1.0 / win_size.y);
    texcoord.xy = p3d_MultiTexCoord0.xy;
    texcoord.zw = p3d_MultiTexCoord0.xy - (rcp_frame * (0.5 + subpix_shift));
}