#version 130
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Vertex;
out vec2 texCoord;

void main() {
    texCoord = p3d_MultiTexCoord0;
    gl_Position = p3d_ModelViewProjectionMatrix  * p3d_Vertex;
}