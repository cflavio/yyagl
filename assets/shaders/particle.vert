#version 130
in vec3 init_vel;  // speicific particle's initial velocity vector
in vec3 start_particle_time;  // specific particle's start time
uniform float osg_FrameTime;
uniform float start_time;  // particle system's start time
uniform mat4 p3d_ModelViewProjectionMatrix;
out float time;  // time relative to specific particle's beginning

void main() {
    vec3 gravity = vec3(.0, .0, -.85);
    time = osg_FrameTime - start_time;
    vec3 pos = vec3(0);
    if (time > start_particle_time.x) {
        float t = time - start_particle_time.x;
        pos = init_vel * t + gravity * t * t;
    }
    gl_PointSize = 10;
    gl_Position = p3d_ModelViewProjectionMatrix * vec4(pos, 1.0);
}
