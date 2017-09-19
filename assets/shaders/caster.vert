#version 130
in vec4 p3d_Vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;
out vec4 texcoord;

void main() {
    texcoord = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    gl_Position = texcoord;
}