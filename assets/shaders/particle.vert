#version 130
in vec3 init_vel;  // speicific particle's initial velocity vector
in vec3 start_particle_time;  // specific particle's start time
in vec3 start_pos;  // particle's start position
uniform float gravity;
uniform float osg_FrameTime;
uniform float start_time;  // particle system's start time
uniform mat4 p3d_ModelViewProjectionMatrix;
out float time;  // time relative to specific particle's beginning
out float ptime;


void main() {
    time = osg_FrameTime - start_time;
    ptime = 0;
    vec3 pos = start_pos;
    gl_FrontColor = vec4(1);
    if (time > start_particle_time.x) {
        float t = time - start_particle_time.x;
        ptime = t;
        pos += init_vel * t + vec3(.0, .0, gravity) * t * t;
    } else gl_FrontColor = vec4(0);
    gl_PointSize = 10;
    gl_Position = p3d_ModelViewProjectionMatrix * vec4(pos, 1.0);
}
